"""T01 — Comparador de tarifas (PVPC, fija, indexada) y potencia contratada."""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from core import montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import EQUIPOS, FACTURA, LIMITADOR, OCUPACION, PERSONAS, VIVIENDAS, Perfil
from core.referencias import ref

ID = "t01"
NOMBRE = "Tarifas y potencia contratada"
DESCRIPCION = "¿PVPC, precio fijo o indexada? ¿Qué potencia te conviene contratar?"
MODALIDADES = {"pvpc": "PVPC", "fija": "Precio fijo", "fija_per": "Fijo por periodos", "idx": "Indexada"}


def preguntas() -> list[Pregunta]:
    pot = [("nose", "No lo sé")] + [(str(p), f"{p} kW") for p in ref().get("tarifa.potencias_normalizadas")]
    return [
        Pregunta("cp", "Código postal", "texto", defecto="28001", perfil="cp"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", VIVIENDAS, perfil="vivienda"),
        Pregunta("personas", "Personas en casa", "select", PERSONAS, perfil="personas"),
        Pregunta("ocupacion", "Ocupación entre semana", "select", OCUPACION, perfil="ocupacion"),
        Pregunta("equipos", "Equipos eléctricos de alto consumo", "multi", EQUIPOS, perfil="equipos"),
        Pregunta("factura", "Importe medio de la factura mensual", "select", FACTURA, perfil="factura"),
        Pregunta("potencia", "Potencia contratada actual (aparece en la factura)", "select", pot, perfil="potencia"),
        Pregunta("limitador", "¿Salta el limitador al encender varios aparatos?", "select", LIMITADOR, perfil="limitador"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    p = dict(pc.inferir_componentes(perfil))
    p["f_consumo"] = Param("f_consumo", "Factor global de consumo", "-", mc.logn(1, r.get("tarifa.sg_f_consumo")))
    p["f_omie"] = Param("f_omie", "Nivel del precio OMIE (factor sobre el histórico)", "-", mc.logn(1, r.get("tarifa.sg_f_omie")))
    pn = r.get("tarifa.potencias_normalizadas")
    i0, i1, i2 = r.get("tarifa.potencia_sin_dato")
    dist_p = mc.fijo(perfil.potencia) if perfil.potencia else mc.tri(pn[i0], pn[i1], pn[i2])
    p["P1"] = Param("P1", "Potencia contratada P1", "kW", dist_p)
    p["P2_delta"] = Param("P2_delta", "Diferencia de potencia P2 − P1", "kW", mc.fijo(0))
    p["p_fija"] = Param("p_fija", "Precio fijo de la energía", "€/kWh", mc.desde_rango(r.rango("tarifa.oferta_fija_energia_tipica")))
    p["pot_fija_dia"] = Param("pot_fija_dia", "Precio de potencia de la oferta fija", "€/kW·día",
                              mc.desde_rango(r.rango("tarifa.oferta_fija_potencia_tipica")))
    p["margen_idx"] = Param("margen_idx", "Margen de la indexada", "€/MWh", mc.desde_rango(r.rango("tarifa.indexada_margen")))
    p["c_aj"] = Param("c_aj", "Servicios de ajuste y otros costes", "€/MWh", mc.desde_rango(r.rango("tarifa.indexada_servicios_ajuste")))
    p["perdidas"] = Param("perdidas", "Coeficiente de pérdidas", "-", mc.desde_rango(r.rango("tarifa.indexada_perdidas")))
    p["bono"] = Param("bono", "Descuento de bono social", "fracción", mc.fijo(0))
    return Parametros(p, {"perfil": perfil.to_dict()})


@lru_cache(maxsize=16)
def _pmax(equipos: tuple, limitador: str, P_actual: float | None):
    n = ref().get("tarifa.pmax_muestras")
    return pc.simular_pmax(set(equipos), n, np.random.default_rng(mc.SEMILLA + 1), limitador=limitador, P_actual=P_actual)


def consumo_horario(S, ctx, perfil, rng):
    """E_t (n, 8760): curva medida (T16) si existe, o perfil sintético calibrado con la factura."""
    if ctx.get("curva") is not None:
        return np.asarray(ctx["curva"], np.float32)[None, :] * S["f_consumo"][:, None].astype(np.float32), None
    esc, importe = pc.escala_factura(perfil, S, rng)
    E = pc.matriz_consumo(S, pc.formas_cached(perfil), esc) * S["f_consumo"][:, None].astype(np.float32)
    return E, importe


def modelo(S, ctx, rng):
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["f_omie"])
    E, importe = consumo_horario(S, ctx, perfil, rng)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    per = precios.periodos()
    P1 = S["P1"]
    P2 = P1 + S["P2_delta"]
    ca, lam = S["c_aj"][:, None], S["perdidas"][:, None]
    p_pvpc = precios.precio_pvpc(omie, per, c_aj=ca, perdidas=lam)
    bono = S["bono"]
    tot = {
        "pvpc": precios.factura(E, p_pvpc, P1, P2, precios.potencia_precios("pvpc"), bono)["total"],
        "fija": precios.factura(E, precios.precio_fijo(S["p_fija"], False, per), P1, P2,
                                precios.potencia_precios("fija", S["pot_fija_dia"]), bono)["total"],
        "fija_per": precios.factura(E, precios.precio_fijo(S["p_fija"], True, per), P1, P2,
                                    precios.potencia_precios("fija", S["pot_fija_dia"]), bono)["total"],
        "idx": precios.factura(E, precios.precio_indexado(omie, per, S["margen_idx"][:, None], ca, lam), P1, P2,
                               precios.potencia_precios("idx"), bono)["total"],
    }
    M = np.stack([tot[k] for k in MODALIDADES], axis=1)
    mejor = M.min(axis=1)
    actual = importe * 12 if importe is not None else tot["pvpc"]
    # potencia óptima
    pmax, w = _pmax(tuple(sorted(perfil.equipos)), perfil.limitador, float(np.median(P1)) if perfil.potencia is None else perfil.potencia)
    alpha = ref().get("tarifa.alpha_corte")
    Pstar = pc.potencia_optima(pmax, w, alpha, ref().get("tarifa.potencias_normalizadas"))
    f_star = precios.factura(E, p_pvpc, Pstar, Pstar, precios.potencia_precios("pvpc"), bono)["total"]
    out = {"coste_mejor": mejor, "ahorro": actual - mejor, "ahorro_pot": tot["pvpc"] - f_star,
           "Pstar": np.full(n, Pstar), "p_corte": np.full(n, float(w[pmax > Pstar].sum())), "idx_mejor": M.argmin(axis=1),
           "E_anual": E.sum(axis=1), "actual": actual}
    out.update({f"tot_{k}": v for k, v in tot.items()})
    return out


KPIS = [
    {"id": "coste_mejor", "nombre": "Coste anual de la mejor modalidad", "unidad": "€/año", "clave": "coste_mejor", "tipo": "coste"},
    {"id": "ahorro", "nombre": "Ahorro frente a tu contrato actual", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "ahorro_pot", "nombre": "Ahorro por ajustar la potencia (PVPC)", "unidad": "€/año", "clave": "ahorro_pot", "tipo": "ahorro"},
]


def graficos(out, ctx):
    cats = list(MODALIDADES.values())
    bandas = [mc.p10_50_90(out[f"tot_{k}"]) for k in MODALIDADES]
    return [{"tipo": "barras", "titulo": "Coste anual por modalidad (P10–P90)", "ylabel": "€/año", "categorias": cats,
             "p10": [b[0] for b in bandas], "p50": [b[1] for b in bandas], "p90": [b[2] for b in bandas]}]


def tabla(out, ctx):
    filas = []
    for i, (k, nombre) in enumerate(MODALIDADES.items()):
        a, b, c = mc.p10_50_90(out[f"tot_{k}"])
        filas.append({"Modalidad": nombre, "P10 (€/año)": round(a), "P50 (€/año)": round(b), "P90 (€/año)": round(c),
                      "Prob. más barata": f"{float(np.mean(out['idx_mejor'] == i)):.0%}"})
    return filas


def notas(out, ctx):
    ps, pr = float(out["Pstar"][0]), float(out["p_corte"][0])
    n = [f"Potencia recomendada P* = {ps:g} kW (probabilidad anual de corte ≈ {pr:.0%}, límite {ref().get('tarifa.alpha_corte'):.0%})."]
    if Perfil.from_dict(ctx["perfil"]).factura != "nose":
        n.append("El consumo anual está calibrado invirtiendo el importe de tu factura.")
    else:
        n.append("Sin importe de factura: la incertidumbre del consumo es mayor. Indícalo para afinar.")
    if ctx.get("curva") is not None:
        n.append("Usando tu curva horaria real (Datadis) en lugar del perfil sintético.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="coste_mejor", graficos=graficos, tabla=tabla, notas=notas)
