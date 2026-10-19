"""T17 — Señal horaria de mix y emisiones: cuándo consumir para emitir menos."""
from __future__ import annotations

import numpy as np

from core import emisiones, montecarlo as mc, perfiles_carga as pc, precios
from core.calendario import calendario_tipico
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t17"
NOMBRE = "Señal horaria de mix y emisiones"
DESCRIPCION = "Cuándo consumir para emitir menos CO₂ y cómo se relaciona con el precio."


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("habitual", "¿Cuándo consumes más?", "select", [("manana", "Por la mañana"), ("tarde", "Por la tarde"), ("noche", "Por la noche")], "noche"),
        Pregunta("ventana", "¿Cuándo aceptarías mover consumos?", "select", [("noche", "De noche (23–7 h)"), ("solar", "Horas centrales (10–18 h)"), ("cualquiera", "A cualquier hora")], "cualquiera"),
        Pregunta("estacion", "Época del año", "select", [("todo", "Todo el año"), ("invierno", "Invierno"), ("verano", "Verano")], "todo"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"habitual": "noche", "ventana": "cualquiera", "estacion": "todo"}
    a.update(respuestas or {})
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    p["kwh_dia"] = Param("kwh_dia", "Energía diaria que puedes desplazar", "kWh/día", mc.desde_rango(r.get("emisiones.carga_desplazable_kwh_dia")))
    p["sg_dia"] = Param("sg_dia", "Variabilidad entre días (0 = sin remuestreo)", "-", mc.fijo(1))
    return Parametros(p, {"perfil": perfil.to_dict(), **a})


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["kwh_dia"])
    ef = emisiones.serie_ef_8760().reshape(365, 24)
    cal = calendario_tipico()
    mes_dia = cal["mes"].reshape(365, 24)[:, 0]
    meses = r.get("emisiones.estaciones")[ctx["estacion"]]
    sel = np.isin(mes_dia, meses)
    # remuestreo diario dentro de cada mes (conserva la estacionalidad)
    idx = np.empty((n, 365), dtype=int)
    for m in range(12):
        dm = np.nonzero(mes_dia == m)[0]
        idx[:, dm] = dm[rng.integers(0, len(dm), size=(n, len(dm)))]
    EF = ef[idx]                                     # (n, 365, 24) kgCO2/kWh
    hab = np.asarray(r.get("desplazamiento.horas_habituales")[ctx["habitual"]])
    ven = np.asarray(r.get("desplazamiento.ventanas")[ctx["ventana"]])
    ef_hab = EF[:, sel][:, :, hab].mean(axis=(1, 2))
    best = EF[:, sel][:, :, ven].min(axis=2)         # mejor hora de cada día
    ef_best = best.mean(axis=1)
    dias = int(sel.sum())
    reduccion = S["kwh_dia"] * (ef_hab - ef_best) * dias                     # kg/año
    # intensidad de «mi consumo»
    perfil = Perfil.from_dict(ctx["perfil"])
    F = pc.formas_cached(perfil)
    w = sum(F[c] for c in F) / len(F)
    ef_mi = EF.reshape(n, 8760) @ w
    ef_media = EF.mean(axis=(1, 2))
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    precio = omie.reshape(n, 365, 24)
    corr = np.array([np.corrcoef(precio[i].ravel(), EF[i].ravel())[0, 1] for i in range(min(n, int(r.get("emisiones.n_muestras_correlacion"))))])
    corr = np.resize(corr, n)
    return {"ef_media": ef_media * 1000, "ef_mi": ef_mi * 1000, "ef_best": ef_best * 1000, "ef_hab": ef_hab * 1000, "reduccion": reduccion,
            "reduccion_pct": (1 - ef_best / np.maximum(ef_hab, 1e-9)) * 100, "corr": corr, "_ef_hora": EF[:, sel].mean(axis=1), "_ef_mes": None,
            "_mapa": ef.reshape(365, 24)}


KPIS = [
    {"id": "reduccion", "nombre": "CO₂ evitado al mover tu carga a la mejor hora", "unidad": "kg/año", "clave": "reduccion", "tipo": "ahorro", "fmt": "{:,.0f}"},
    {"id": "ef_mi", "nombre": "Intensidad de emisiones de tu consumo", "unidad": "g CO₂/kWh", "clave": "ef_mi", "tipo": "coste"},
    {"id": "reduccion_pct", "nombre": "Reducción de intensidad en la mejor hora", "unidad": "%", "clave": "reduccion_pct", "tipo": "ahorro", "fmt": "{:.0f}"},
    {"id": "ef_media", "nombre": "Intensidad media del sistema", "unidad": "g CO₂/kWh", "clave": "ef_media"},
    {"id": "ef_hab", "nombre": "Intensidad a tu hora habitual", "unidad": "g CO₂/kWh", "clave": "ef_hab"},
    {"id": "ef_best", "nombre": "Intensidad en la mejor hora de tu ventana", "unidad": "g CO₂/kWh", "clave": "ef_best"},
    {"id": "corr", "nombre": "Correlación precio–emisiones", "unidad": "r", "clave": "corr", "fmt": "{:.2f}"},
]


def graficos(out, ctx):
    h = np.nanpercentile(out["_ef_hora"], [10, 50, 90], axis=0) * 1000
    g = [{"tipo": "abanico", "titulo": "Intensidad de emisiones por hora del día (P10–P90)", "xlabel": "Hora del día", "ylabel": "g CO₂/kWh",
          "x": list(range(24)), "p10": h[0].tolist(), "p50": h[1].tolist(), "p90": h[2].tolist()},
         {"tipo": "heatmap", "titulo": "Intensidad media por día y hora del año (g CO₂/kWh)", "xlabel": "Hora del día", "ylabel": "Día del año",
          "z": (out["_mapa"][::3] * 1000).tolist(), "unidad": "g/kWh"}]
    mix = emisiones.mix_por_hora()
    if mix:
        tot = np.sum([v for v in mix.values()], axis=0)
        g.append({"tipo": "barras_apiladas", "titulo": "Mix de generación por hora del día (%)", "ylabel": "%", "categorias": [str(i) for i in range(24)],
                  "series": [{"nombre": k, "y": (100 * v / np.maximum(tot, 1e-9)).tolist()} for k, v in mix.items()]})
    return g


def tabla(out, ctx):
    ef = np.asarray(out["_mapa"]).reshape(365, 24).mean(axis=0) * 1000
    orden = np.argsort(ef)
    return [{"Posición": f"{i + 1}.ª hora más limpia", "Hora": f"{int(orden[i])}:00", "g CO₂/kWh (media anual)": round(float(ef[orden[i]]))} for i in range(3)] + \
           [{"Posición": "Hora más intensiva", "Hora": f"{int(orden[-1])}:00", "g CO₂/kWh (media anual)": round(float(ef[orden[-1]]))}]


def notas(out, ctx):
    n = ["La intensidad es la del sistema eléctrico peninsular por hora (emisiones / demanda de REData), no la de tu contrato.",
         "Las horas más limpias suelen coincidir con las de mayor producción solar y eólica, que también son las de precio más bajo."]
    if emisiones.mix_por_hora() is None:
        n.append("No hay datos de mix por tecnología en esta copia de datos.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="reduccion", graficos=graficos, tabla=tabla, notas=notas)
