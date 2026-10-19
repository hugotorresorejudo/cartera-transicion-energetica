"""T03 — Explorador de precios del mercado diario OMIE."""
from __future__ import annotations

import numpy as np

from core import calendario, clima, datos, fv, montecarlo as mc, perfiles_carga as pc
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t03"
NOMBRE = "Explorador de precios OMIE"
DESCRIPCION = "Cuándo es barata la luz, qué vale un kWh solar y cuánto pagaría tu consumo."

PUNTOS_GRAFICO, FILAS_MAPA = 4 * 100, 12 * 10  # tamaños de remuestreo de los gráficos (presentación)
VISTAS = [("perfil", "Perfil horario medio"), ("calor", "Mapa de calor"), ("duracion", "Curva de duración"), ("serie", "Serie temporal")]


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("periodo", "Periodo", "select", [("semana", "Última semana"), ("mes", "Último mes"), ("anio", "Último año"),
                                                 ("comparar", "Comparar años")], "anio"),
        Pregunta("vista", "Vista", "select", VISTAS, "perfil"),
        Pregunta("zona", "Zona", "select", [("es", "España"), ("pt", "Portugal"), ("ambas", "Ambas")], "es"),
        Pregunta("ponderar", "Ponderar por", "select", [("nada", "Nada"), ("solar", "Solar"), ("eolica", "Eólica"),
                                                       ("mi_fv", "Mi FV (T02)"), ("mi_consumo", "Mi consumo (T01)")], "solar"),
        Pregunta("dias", "Días", "select", [("todos", "Todos"), ("laborables", "Laborables"), ("finde", "Fines de semana y festivos")], "todos"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"periodo": "anio", "vista": "perfil", "zona": "es", "ponderar": "solar", "dias": "todos"}
    a.update(respuestas or {})
    base = t01.inferir(perfil, {})
    p = {k: v for k, v in base.params.items() if k.startswith("E_") or k == "f_consumo"}
    p["azimut"] = Param("azimut", "Azimut de «mi FV»", "º", mc.desde_rango(r.get("omie.az_mi_fv")))
    p["inclinacion"] = Param("inclinacion", "Inclinación de «mi FV»", "º", mc.desde_rango(r.get("omie.incl_mi_fv")))
    p["umbral"] = Param("umbral", "Umbral de precio bajo", "€/MWh", mc.fijo(r.get("omie.umbral_precio_bajo")))
    p["n_spread"] = Param("n_spread", "Ventana del spread", "horas", mc.fijo(r.get("omie.n_spread_horas")))
    p["excluir_ajuste"] = Param("excluir_ajuste", "Excluir periodo del mecanismo de ajuste del gas (1 = sí)", "-", mc.fijo(0))
    return Parametros(p, {"perfil": perfil.to_dict(), **a})


def ventana(ctx, excluir_ajuste=False):
    """Selecciona (fechas, M (nd,24)) según periodo, tipo de día y exclusión del mecanismo de ajuste."""
    zona = "pt" if ctx["zona"] == "pt" else "es"
    fechas, M = datos.omie_dias(zona)
    nd = len(fechas)
    r = ref()
    if ctx["periodo"] in ("semana", "mes", "anio"):
        k = r.get("omie.ventana_dias")[ctx["periodo"]]
        sel = np.arange(nd) >= nd - k
    else:
        sel = np.isin(calendario.anio_de(fechas), np.array(datos.anios_completos()))
    dow = (fechas.astype("datetime64[D]").astype(int) + 3) % 7  # 0 = lunes
    fest = np.zeros(nd, bool)
    for y in np.unique(calendario.anio_de(fechas)):
        ff = {np.datetime64(f) for f in calendario.festivos(int(y))}
        fest |= np.isin(fechas, list(ff))
    if ctx["dias"] == "laborables":
        sel &= (dow < 5) & ~fest
    elif ctx["dias"] == "finde":
        sel &= (dow >= 5) | fest
    if excluir_ajuste:
        ini, fin = np.datetime64(r.get("tarifa.ajuste_gas_inicio")), np.datetime64(r.get("tarifa.ajuste_gas_fin"))
        sel &= ~((fechas >= ini) & (fechas <= fin))
    return fechas[sel], M[sel]


def _indices_hora(fechas):
    """Índice de hora del año tipo (0..8759) de cada hora de las fechas dadas (29-feb -> 28-feb)."""
    return calendario.indices_hora_tipo(fechas)


def _perfil_dato(nombre, fechas):
    tabla = datos.redata_perfil_mes_hora(nombre)
    if tabla is None:
        return None
    mes = (fechas.astype("datetime64[M]").astype(int) % 12)
    return tabla[mes]  # (nd, 24)


def modelo(S, ctx, rng):
    n = len(S["umbral"])
    excl = bool(round(float(S["excluir_ajuste"][0])))
    fechas, M = ventana(ctx, excl)
    nd = len(fechas)
    if nd == 0:
        raise ValueError("La ventana seleccionada no contiene días con datos")
    bloque = ref().get("omie.dias_semana")
    nb = max(nd // bloque, 1)
    if nd >= bloque * 2:
        inicios = rng.integers(0, nd - bloque + 1, size=(n, nb))
        dias_idx = (inicios[:, :, None] + np.arange(bloque)[None, None, :]).reshape(n, -1)
    else:
        dias_idx = np.tile(np.arange(nd), (n, 1))
    P = M[dias_idx]  # (n, nd', 24)
    nd2 = P.shape[1]
    Pv = P.reshape(n, -1)
    media = Pv.mean(axis=1)
    dem = _perfil_dato("demanda", fechas)
    if dem is None:
        w_dem = np.ones((n, Pv.shape[1]))
    else:
        w_dem = dem[dias_idx].reshape(n, -1)
    pond_dem = (Pv * w_dem).sum(1) / w_dem.sum(1)
    modo = ctx["ponderar"]
    idx_h = _indices_hora(fechas)[dias_idx].reshape(n, -1)
    perfil = Perfil.from_dict(ctx["perfil"])
    if modo == "nada":
        w = np.ones_like(Pv)
    elif modo in ("solar", "eolica"):
        tab = _perfil_dato("solar" if modo == "solar" else "lica", fechas)
        w = np.ones_like(Pv) if tab is None else tab[dias_idx].reshape(n, -1)
    elif modo == "mi_fv":
        Gu = fv.generacion_unitaria(perfil.cp, S["azimut"], S["inclinacion"], rng)
        w = np.take_along_axis(Gu, idx_h, axis=1)
    else:
        E, _ = t01.consumo_horario(S, {}, perfil, rng)
        w = np.take_along_axis(E, idx_h, axis=1)
    capturado = (Pv * w).sum(1) / np.maximum(w.sum(1), 1e-12)
    umbral = S["umbral"][:, None]
    horas_bajo = (Pv <= umbral).sum(1) * (8760.0 / Pv.shape[1])
    k = int(round(float(S["n_spread"][0])))
    s = np.sort(P, axis=2)
    spread = (s[:, :, -k:].mean(2) - s[:, :, :k].mean(2)).mean(1)
    return {"media": media, "pond_dem": pond_dem, "capturado": capturado, "fc": capturado / media, "horas_bajo": horas_bajo,
            "spread": spread, "_fechas": fechas, "_M": M}


KPIS = [
    {"id": "media", "nombre": "Precio medio aritmético", "unidad": "€/MWh", "clave": "media", "fmt": "{:,.1f}"},
    {"id": "capturado", "nombre": "Precio capturado (perfil elegido)", "unidad": "€/MWh", "clave": "capturado", "fmt": "{:,.1f}"},
    {"id": "fc", "nombre": "Factor de captura", "unidad": "×", "clave": "fc", "fmt": "{:.2f}"},
    {"id": "pond_dem", "nombre": "Precio medio ponderado por demanda", "unidad": "€/MWh", "clave": "pond_dem", "fmt": "{:,.1f}"},
    {"id": "spread", "nombre": "Spread diario de n horas", "unidad": "€/MWh", "clave": "spread", "fmt": "{:,.1f}"},
    {"id": "horas_bajo", "nombre": "Horas con precio ≤ umbral", "unidad": "h/año", "clave": "horas_bajo", "fmt": "{:,.0f}"},
]


def graficos(out, ctx):
    fechas, M = out["_fechas"], out["_M"]
    vista = ctx["vista"]
    ZONAS = {"es": "España", "pt": "Portugal"}
    zonas = ["es", "pt"] if ctx["zona"] == "ambas" else [ctx["zona"]]
    series = []
    if vista == "perfil":
        for z in zonas:
            f, Mz = ventana({**ctx, "zona": z})
            b = np.percentile(Mz, [10, 50, 90], axis=0)
            series.append({"nombre": ZONAS[z], "x": list(range(24)), "p10": b[0].tolist(), "p50": b[1].tolist(), "p90": b[2].tolist()})
        return [{"tipo": "abanico_multi", "titulo": "Perfil horario del precio (P10–P50–P90 de los días)", "xlabel": "Hora del día",
                 "ylabel": "€/MWh", "series": series}]
    if vista == "calor":
        return [{"tipo": "heatmap", "titulo": "Mapa de calor del precio (día × hora)", "xlabel": "Hora del día", "ylabel": "Día",
                 "z": M[:: max(1, len(M) // FILAS_MAPA)].tolist(), "unidad": "€/MWh"}]
    if vista == "duracion":
        for z in zonas:
            f, Mz = ventana({**ctx, "zona": z})
            v = np.sort(Mz.ravel())[::-1]
            paso = max(1, len(v) // PUNTOS_GRAFICO)
            series.append({"nombre": ZONAS[z], "x": (np.arange(len(v))[::paso] / len(v) * 100).tolist(), "y": v[::paso].tolist()})
        return [{"tipo": "lineas", "titulo": "Curva de duración del precio", "xlabel": "% de las horas", "ylabel": "€/MWh", "series": series}]
    for z in zonas:
        f, Mz = ventana({**ctx, "zona": z})
        diario = Mz.mean(axis=1)
        series.append({"nombre": ZONAS[z], "x": list(range(len(diario))), "y": diario.tolist()})
    return [{"tipo": "lineas", "titulo": "Precio medio diario", "xlabel": "Días del periodo", "ylabel": "€/MWh", "series": series}]


def tabla(out, ctx):
    return [{"Indicador": k["nombre"], "Unidad": k["unidad"], **dict(zip(("P10", "P50", "P90"), [round(float(x), 2) for x in mc.p10_50_90(out[k["clave"]])]))}
            for k in KPIS]


def notas(out, ctx):
    n = []
    ini, fin = ref().get("tarifa.ajuste_gas_inicio"), ref().get("tarifa.ajuste_gas_fin")
    f = out["_fechas"]
    if len(f) and np.any((f >= np.datetime64(ini)) & (f <= np.datetime64(fin))):
        n.append(f"La ventana incluye días del mecanismo de ajuste del gas (RDL 10/2022, {ini} a {fin}): las series no son homogéneas. Puedes excluirlos en Avanzado.")
    n.append("Las bandas P10–P90 reflejan el remuestreo semanal del periodo y la incertidumbre del perfil de ponderación.")
    n.append("Resolución horaria (los ficheros cuartohorarios de OMIE se promedian por hora).")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="capturado", graficos=graficos, tabla=tabla, notas=notas)
