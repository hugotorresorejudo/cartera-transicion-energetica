"""T18 — Climatización de verano: split eficiente, equipo antiguo o multisplit reversible."""
from __future__ import annotations

import numpy as np

from core import clima, emisiones, finanzas as fin, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t18"
NOMBRE = "Climatización de verano"
DESCRIPCION = "Split o bomba de calor reversible: consumo, coste y potencia necesaria."
SISTEMAS = {"antiguo": "Split antiguo", "eficiente": "Split inverter eficiente", "reversible": "Multisplit reversible"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("actual", "Tu equipo actual", "select", [("ninguno", "Ninguno"), ("antiguo", "Split antiguo (sin inverter)"), ("eficiente", "Split inverter reciente")], "antiguo"),
        Pregunta("estancias", "Estancias a climatizar", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("toda", "Toda la vivienda")], "2"),
        Pregunta("uso", "Uso en verano", "select", [("poco", "Poco"), ("medio", "Medio"), ("mucho", "Mucho")], "medio"),
        Pregunta("soleada", "¿Vivienda muy soleada (sin protección solar)?", "select", [("si", "Sí"), ("no", "No")], "no"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", [("piso_<70", "Piso <70 m²"), ("piso_70_120", "Piso 70–120 m²"), ("piso_>120", "Piso >120 m²"),
                                                                   ("unif_<120", "Unifamiliar <120 m²"), ("unif_>120", "Unifamiliar >120 m²")], perfil="vivienda"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"actual": "antiguo", "estancias": "2", "uso": "medio", "soleada": "no"}
    a.update(respuestas or {})
    D = mc.desde_rango
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    m2 = pc.superficie_m2(perfil)
    dem = r.get("refrigeracion.demanda_kwh_m2_ano_por_zona")[pc.letra_zona(perfil)]
    p["m2_clim"] = Param("m2_clim", "Superficie climatizada", "m²", mc.logn(m2 * r.sub("refrigeracion.fraccion_estancias", a["estancias"])[1], 1.2))
    p["dem_m2"] = Param("dem_m2", "Demanda de refrigeración", "kWh/m²·año", D(dem))
    p["f_uso"] = Param("f_uso", "Factor de uso", "×", D(r.sub("refrigeracion.uso", a["uso"])))
    p["f_sol"] = Param("f_sol", "Factor de soleamiento", "×", D(r.sub("refrigeracion.factor_soleada", a["soleada"])))
    p["seer_nuevo"] = Param("seer_nuevo", "SEER de etiqueta del equipo eficiente", "-", D(r.rango("refrigeracion.seer_split")))
    p["seer_antiguo"] = Param("seer_antiguo", "SEER del equipo antiguo", "-", D(r.rango("refrigeracion.seer_antiguo")))
    p["f_campo"] = Param("f_campo", "SEER de campo / etiqueta", "×", D(r.rango("refrigeracion.factor_seer_real")))
    p["f_rev"] = Param("f_rev", "SEER reversible / split", "×", D(r.rango("refrigeracion.factor_reversible")))
    p["capex_split"] = Param("capex_split", "Coste de un split instalado", "€", D(r.rango("refrigeracion.capex_split_eur")))
    p["f_capex_rev"] = Param("f_capex_rev", "Sobrecoste del reversible por estancia", "×", D(r.rango("refrigeracion.capex_reversible_factor")))
    p["n_equipos"] = Param("n_equipos", "Número de unidades interiores", "ud", mc.fijo(r.sub("refrigeracion.estancias_equipos", a["estancias"])))
    p["w_m2"] = Param("w_m2", "Potencia frigorífica de diseño", "W/m²", D(r.rango("refrigeracion.potencia_frigorifica_w_m2")))
    p["eer"] = Param("eer", "EER a plena carga", "-", D(r.rango("refrigeracion.potencia_electrica_eer")))
    p["g_elec"] = Param("g_elec", "Inflación de la electricidad", "fracción/año", D(r.rango("fv.inflacion_electricidad")))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": a["actual"]})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["m2_clim"])
    util = S["m2_clim"] * S["dem_m2"] * S["f_uso"] * S["f_sol"]  # kWh térmicos/año
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]) * imp
    F = pc.formas_cached(Perfil.from_dict({**perfil.to_dict(), "equipos": sorted(set(perfil.equipos) | {"aire_acondicionado"})}))
    p_ref = p_h @ F["refrigeracion"].astype(np.float32)
    ef = float(F["refrigeracion"] @ emisiones.ef_anual_8760())
    seer = {"antiguo": S["seer_antiguo"], "eficiente": S["seer_nuevo"] * S["f_campo"], "reversible": S["seer_nuevo"] * S["f_campo"] * S["f_rev"]}
    e = {k: util / v for k, v in seer.items()}
    c_op = {k: e[k] * p_ref for k in e}
    capex = {"antiguo": np.zeros(n), "eficiente": S["capex_split"] * S["n_equipos"],
             "reversible": S["capex_split"] * S["n_equipos"] * S["f_capex_rev"]}
    N = int(r.get("refrigeracion.vida_util"))
    crf = fin.crf(S["r_desc"], N)
    anios = np.arange(N)
    tco_anual = {k: capex[k] * crf + c_op[k] for k in e}
    act = ctx["actual"]
    base = "antiguo" if act == "ninguno" else act
    ah = (c_op[base] - c_op["eficiente"])[:, None] * (1 + S["g_elec"][:, None]) ** anios
    cf = fin.flujos_proyecto(capex["eficiente"], ah)
    pico = S["m2_clim"] * S["w_m2"] / 1000.0 / S["eer"]
    out = {"c_op": c_op["eficiente"], "ahorro": c_op[base] - c_op["eficiente"], "van": fin.van(cf, S["r_desc"]), "payback": fin.payback(cf),
           "pico": pico, "util": util, "e_ef": e["eficiente"], "co2_ahorro": (e[base] - e["eficiente"]) * ef}
    for k in SISTEMAS:
        out[f"tco_{k}"] = tco_anual[k]
        out[f"c_{k}"] = c_op[k]
        out[f"e_{k}"] = e[k]
    return out


KPIS = [
    {"id": "c_op", "nombre": "Coste anual de operar un split eficiente", "unidad": "€/año", "clave": "c_op", "tipo": "coste"},
    {"id": "ahorro", "nombre": "Ahorro anual frente a tu equipo", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro", "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "pico", "nombre": "Potencia eléctrica máxima", "unidad": "kW", "clave": "pico", "fmt": "{:.2f}"},
    {"id": "van", "nombre": "VAN de sustituir por un split eficiente", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "e_ef", "nombre": "Consumo eléctrico del split eficiente", "unidad": "kWh/año", "clave": "e_ef"},
    {"id": "util", "nombre": "Demanda de refrigeración", "unidad": "kWh/año", "clave": "util"},
] + [{"id": f"tco_{k}", "nombre": f"Coste anualizado: {v}", "unidad": "€/año", "clave": f"tco_{k}", "tipo": "coste"} for k, v in SISTEMAS.items()]


def graficos(out, ctx):
    b = [mc.p10_50_90(out[f"tco_{k}"]) for k in SISTEMAS]
    return [{"tipo": "barras", "titulo": "Coste anualizado (inversión con CRF + operación)", "ylabel": "€/año", "categorias": list(SISTEMAS.values()),
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    return [{"Equipo": v, "Consumo P50 (kWh/año)": round(mc.p10_50_90(out[f"e_{k}"])[1]), "Operación P50 (€/año)": round(mc.p10_50_90(out[f"c_{k}"])[1]),
             "Coste anualizado P50 (€/año)": round(mc.p10_50_90(out[f"tco_{k}"])[1])} for k, v in SISTEMAS.items()]


def notas(out, ctx):
    n = ["La demanda de refrigeración varía mucho dentro de cada zona CTE (es una zona de invierno): usa Avanzado si conoces tu consumo de verano.",
         "El multisplit reversible también calefacta: su ahorro en invierno se evalúa en T08."]
    if ctx["actual"] == "ninguno":
        n.append("Sin equipo actual, el ahorro se compara con un split antiguo de referencia.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="c_op", graficos=graficos, tabla=tabla, notas=notas)
