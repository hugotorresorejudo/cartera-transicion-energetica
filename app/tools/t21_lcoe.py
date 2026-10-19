"""T21 — Explorador de LCOE por tecnología, contrastado con los precios capturados del mercado diario."""
from __future__ import annotations

import numpy as np

from core import datos, finanzas as fin, montecarlo as mc
from core.calendario import calendario_tipico
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref

ID = "t21"
NOMBRE = "Explorador de LCOE"
DESCRIPCION = "Coste nivelado de cada tecnología frente al precio que captura en el mercado."


def _tecs():
    return ref().get("lcoe.tecnologias")


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("tecs", "Tecnologías a comparar", "multi", [(k, v) for k, v in _tecs().items()],
                 ["solar_fv_utility", "eolica_terrestre", "ciclo_combinado", "nuclear_existente_ampliacion"]),
        Pregunta("gas", "Escenario de precio del gas y del CO₂", "select", [("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto")], "medio"),
        Pregunta("capital", "Coste del capital", "select", [("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto")], "medio"),
        Pregunta("co2", "¿Incluir el coste del CO₂ del ciclo combinado?", "select", [("si", "Sí"), ("no", "No")], "si"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"tecs": ["solar_fv_utility", "eolica_terrestre", "ciclo_combinado", "nuclear_existente_ampliacion"], "gas": "medio", "capital": "medio", "co2": "si"}
    a.update(respuestas or {})
    D = mc.desde_rango
    fw = r.sub("lcoe.factor_wacc", a["capital"])
    ig = int(r.sub("lcoe.escenario_gas", a["gas"]))
    p = {}
    for t in a["tecs"]:
        n = _tecs()[t]
        p[f"capex_{t}"] = Param(f"capex_{t}", f"CAPEX: {n}", "€/kW", D(r.get("lcoe.capex_eur_kw")[t]))
        p[f"fom_{t}"] = Param(f"fom_{t}", f"OPEX fijo: {n}", "€/kW·año", D(r.get("lcoe.opex_fijo_eur_kw_ano")[t]))
        p[f"vom_{t}"] = Param(f"vom_{t}", f"OPEX variable: {n}", "€/MWh", D(r.get("lcoe.opex_variable_eur_mwh")[t]))
        p[f"fc_{t}"] = Param(f"fc_{t}", f"Factor de capacidad: {n}", "-", D(r.get("lcoe.factor_capacidad_espana")[t]))
        w = r.get("lcoe.wacc")[t]
        p[f"wacc_{t}"] = Param(f"wacc_{t}", f"WACC: {n}", "-", D(tuple(x * fw for x in w)))
        p[f"vida_{t}"] = Param(f"vida_{t}", f"Vida útil: {n}", "años", mc.fijo(r.get("lcoe.vida_util_anios")[t][1]))
    gas = r.get("lcoe.precio_gas_ttf_eur_mwh")
    co2 = r.get("lcoe.precio_co2_eur_t")
    p["gas"] = Param("gas", "Precio del gas", "€/MWh", mc.tri(gas[0], gas[ig], gas[2]) if a["gas"] == "medio" else mc.tri(gas[0], gas[ig], gas[2]))
    p["co2"] = Param("co2", "Precio del CO₂", "€/t", mc.fijo(0) if a["co2"] == "no" else mc.tri(co2[0], co2[ig], co2[2]))
    p["eta_cc"] = Param("eta_cc", "Rendimiento del ciclo combinado", "-", D(r.rango("lcoe.rendimiento_ciclo_combinado")))
    p["ef_cc"] = Param("ef_cc", "Emisiones del ciclo combinado", "t CO₂/MWh", D(r.rango("lcoe.factor_emision_ccgt_t_mwh")))
    p["comb_nuc"] = Param("comb_nuc", "Combustible nuclear", "€/MWh", D(r.rango("lcoe.costes_combustible_nuclear_eur_mwh")))
    return Parametros(p, {"perfil": perfil.to_dict(), "tecs": list(a["tecs"])})


def _captura():
    """Precio capturado (€/MWh) de solar, eólica y base a partir de OMIE y los perfiles de REData; None si no hay datos."""
    ys, M = datos.omie_matriz()
    precio = M.mean(axis=0).reshape(365, 24)  # año medio
    out = {"media": float(precio.mean())}
    cal_mes = calendario_tipico()["mes"].reshape(365, 24)[:, 0]
    for nombre, col in (("solar", "solar"), ("eolica", "lica")):
        tab = datos.redata_perfil_mes_hora(col)
        if tab is None:
            continue
        w = tab[cal_mes]
        out[nombre] = float((precio * w).sum() / max(w.sum(), 1e-9))
    return out


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["gas"])
    out = {}
    for t in ctx["tecs"]:
        crf = fin.crf(S[f"wacc_{t}"], S[f"vida_{t}"])
        e = S[f"fc_{t}"] * r.get("lcoe.mwh_por_kw_mwh")  # MWh por kW·año
        fijo = (crf * S[f"capex_{t}"] + S[f"fom_{t}"]) / e
        var = S[f"vom_{t}"]
        if t == "ciclo_combinado":
            var = var + S["gas"] / S["eta_cc"] + S["co2"] * S["ef_cc"]
        if t.startswith("nuclear"):
            var = var + S["comb_nuc"]
        out[f"lcoe_{t}"] = fijo + var
    cap = _captura()
    for k in ("media", "solar", "eolica"):
        out[f"cap_{k}"] = np.full(n, cap.get(k, np.nan))
    if "solar" in cap and any(t.startswith("solar") for t in ctx["tecs"]):
        ts = next(t for t in ctx["tecs"] if t.startswith("solar"))
        out["margen_solar"] = cap["solar"] - out[f"lcoe_{ts}"]
    else:
        out["margen_solar"] = np.full(n, np.nan)
    return out


def _kpis(ctx_tecs):
    return None


KPIS = [
    {"id": "margen_solar", "nombre": "Margen de la FV: precio capturado − LCOE", "unidad": "€/MWh", "clave": "margen_solar", "tipo": "ahorro", "fmt": "{:,.1f}",
     "prob": ("Probabilidad de margen positivo", lambda v: v > 0)},
    {"id": "cap_solar", "nombre": "Precio capturado por la solar", "unidad": "€/MWh", "clave": "cap_solar", "fmt": "{:,.1f}"},
    {"id": "cap_media", "nombre": "Precio medio del mercado diario", "unidad": "€/MWh", "clave": "cap_media", "fmt": "{:,.1f}"},
    {"id": "cap_eolica", "nombre": "Precio capturado por la eólica", "unidad": "€/MWh", "clave": "cap_eolica", "fmt": "{:,.1f}"},
]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    tecs = parametros.ctx["tecs"]
    kp = KPIS + [{"id": f"lcoe_{t}", "nombre": f"LCOE: {_tecs()[t]}", "unidad": "€/MWh", "clave": f"lcoe_{t}", "tipo": "coste", "fmt": "{:,.1f}"} for t in tecs]

    def graficos(out, ctx):
        b = [mc.p10_50_90(out[f"lcoe_{t}"]) for t in tecs]
        return [{"tipo": "barras", "titulo": "LCOE por tecnología (P10–P90) y precio medio del mercado", "ylabel": "€/MWh",
                 "categorias": [_tecs()[t] for t in tecs], "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]

    def tabla(out, ctx):
        c = float(out["cap_media"][0])
        return [{"Tecnología": _tecs()[t], "LCOE P10 (€/MWh)": round(mc.p10_50_90(out[f"lcoe_{t}"])[0], 1), "P50": round(mc.p10_50_90(out[f"lcoe_{t}"])[1], 1),
                 "P90": round(mc.p10_50_90(out[f"lcoe_{t}"])[2], 1), "Prob. LCOE < precio medio": f"{float(np.mean(out[f'lcoe_{t}'] < c)):.0%}"} for t in tecs]

    def notas(out, ctx):
        return ["El LCOE no incluye costes de sistema (integración, respaldo, redes) ni el valor de la firmeza: comparar con el precio capturado es solo una referencia.",
                "Los precios capturados se calculan con OMIE y los perfiles de generación de REData; mira T03 para el detalle."]

    return ejecutar(ID, parametros, modelo, kp, n_mc, seed, tornado_kpi=kp[4]["id"] if len(kp) > 4 else "margen_solar", graficos=graficos, tabla=tabla, notas=notas)
