"""T08 — Aerotermia (calefacción + ACS) frente a caldera de gas, butano o radiadores eléctricos."""
from __future__ import annotations

import numpy as np

from core import emisiones, finanzas as fin, fv, montecarlo as mc, perfiles_carga as pc, precios, termico
from core.herramienta import Param, Parametros, Pregunta, ejecutar, tri_rel
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t08"
NOMBRE = "Aerotermia vs caldera"
DESCRIPCION = "Calefacción y agua caliente: coste, VAN del cambio y emisiones."
SISTEMAS = {"gas": "Caldera de gas natural", "butano": "Caldera de butano", "electrica": "Radiadores eléctricos", "aero": "Aerotermia"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("edad", "Antigüedad del edificio", "select", [("pre1980", "Anterior a 1980"), ("1980", "1980–2006"), ("2007", "Desde 2007"), ("nose", "No lo sé")], "1980"),
        Pregunta("actual", "Calefacción actual", "select", [("gas", "Caldera de gas natural"), ("butano", "Caldera de butano"), ("electrica", "Radiadores eléctricos")], "gas"),
        Pregunta("emisores", "Emisores", "select", [("alta", "Radiadores clásicos (agua a 55–70 ºC)"), ("media", "Radiadores de baja temperatura o fan-coil"),
                                                      ("suelo", "Suelo radiante"), ("nose", "No lo sé")], "alta"),
        Pregunta("cocina_gas", "¿Cocinas con gas?", "select", [("si", "Sí"), ("no", "No")], "no"),
        Pregunta("caldera", "Estado de tu caldera", "select", [("toca", "Hay que cambiarla pronto"), ("bien", "Funciona bien")], "bien"),
        Pregunta("uso", "Uso de la calefacción", "select", [("todo", "Casi todo el día"), ("tardes", "Tardes y noches"), ("ocasional", "Ocasional")], "tardes"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", [("piso_<70", "Piso <70 m²"), ("piso_70_120", "Piso 70–120 m²"), ("piso_>120", "Piso >120 m²"),
                                                                   ("unif_<120", "Unifamiliar <120 m²"), ("unif_>120", "Unifamiliar >120 m²")], perfil="vivienda"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"edad": "1980", "actual": "gas", "emisores": "alta", "cocina_gas": "no", "caldera": "bien", "uso": "tardes"}
    a.update(respuestas or {})
    D = mc.desde_rango
    zl = pc.letra_zona(perfil)
    edad = r.sub("calefaccion.edad", a["edad"])
    d = pc.demanda_calefaccion_util(perfil, edad)
    uso = r.sub("calefaccion.uso", a["uso"])
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    p["Q_cal"] = Param("Q_cal", "Demanda útil de calefacción", "kWh/año", mc.logn(d[1] * uso[1], r.get("calefaccion.sg_demanda")))
    p["Q_acs"] = Param("Q_acs", "Demanda útil de ACS (CTE)", "kWh/año", mc.logn(pc.acs_util_cte_kwh(perfil), r.get("acs.sg_demanda")))
    p["eta_caldera"] = Param("eta_caldera", "Rendimiento estacional de la caldera (PCS)", "-", D(r.rango("calefaccion.caldera_gas_rendimiento_estacional_pcs")))
    f_em = r.get("calefaccion.factor_scop_emisores")["media" if a["emisores"] == "nose" else a["emisores"]]
    p["scop"] = Param("scop", "SCOP de la aerotermia (clima de la zona)", "-", D(r.get("calefaccion.bdc_scop_aerotermia")[zl]))
    p["f_emisor"] = Param("f_emisor", "Factor de emisores sobre el SCOP", "×", mc.fijo(f_em))
    p["scop_acs"] = Param("scop_acs", "COP medio para ACS", "-", D(r.rango("acs.bdc_cop_nominal_acs")))
    gv = r.get("gas.tur_termino_variable_tur1")
    lib = r.rango("gas.oferta_libre_tipica")
    p["p_gas"] = Param("p_gas", "Término variable del gas", "€/kWh sin impuestos", mc.tri(min(gv, lib[0]), gv, max(gv, lib[2])))
    p["p_butano_bombona"] = Param("p_butano_bombona", "Bombona de butano", "€", tri_rel(r.get("gas.butano_precio_bombona"), r.get("gas.banda_bombona")))
    fijo = (r.get("gas.tur_termino_fijo_tur1") + r.get("gas.alquiler_contador")) * (1 + r.get("gas.iva") / 100.0)
    p["gas_fijo_evit"] = Param("gas_fijo_evit", "Cuota fija de gas (se evita si abandonas el gas)", "€/año", mc.fijo(0 if a["cocina_gas"] == "si" else 12 * fijo))
    p["dP"] = Param("dP", "Potencia eléctrica adicional a contratar", "kW", mc.fijo(0) if a["actual"] == "electrica" else D(r.get("calefaccion.potencia_extra_aerotermia_kw")))
    p["capex_aero"] = Param("capex_aero", "CAPEX de la aerotermia", "€", D(r.rango("calefaccion.bdc_capex_aerotermia_eur")))
    capcal = r.rango("calefaccion.capex_caldera_condensacion_eur")
    p["reposicion"] = Param("reposicion", "Coste de la caldera que te ahorras", "€", D(capcal) if a["caldera"] == "toca" and a["actual"] != "electrica" else mc.fijo(0))
    p["ayuda"] = Param("ayuda", "Ayudas y deducciones (ver T11)", "€", mc.fijo(0))
    p["mant_aero"] = Param("mant_aero", "Mantenimiento aerotermia", "€/año", mc.fijo(r.get("acs.mantenimiento_anual_eur")["bdc"][1]))
    p["mant_cal"] = Param("mant_cal", "Mantenimiento caldera", "€/año", D(r.rango("calefaccion.mantenimiento_caldera_eur_ano")))
    p["g_elec"] = Param("g_elec", "Inflación de la electricidad", "fracción/año", D(r.rango("fv.inflacion_electricidad")))
    p["g_fuel"] = Param("g_fuel", "Inflación del gas", "fracción/año", D(r.rango("combustibles.inflacion_anual")))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": a["actual"]})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["Q_cal"])
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]) * imp
    F = pc.formas_cached(perfil if "calefaccion_electrica" in perfil.equipos else Perfil.from_dict({**perfil.to_dict(), "equipos": ["calefaccion_electrica", "termo_electrico"]}))
    p_cal = p_h @ F["calefaccion"].astype(np.float32)
    p_acs = p_h @ F["acs"].astype(np.float32)
    ef = emisiones.ef_anual_8760()
    ef_cal, ef_acs = float(F["calefaccion"] @ ef), float(F["acs"] @ ef)
    iva = 1 + r.get("gas.iva") / 100.0
    ih = r.get("gas.gas_natural_impuesto_hidrocarburos")
    # --- energías finales por sistema
    gas_kwh = (S["Q_cal"] + S["Q_acs"]) / S["eta_caldera"]
    c_gas = gas_kwh * (S["p_gas"] + ih) * iva + S["gas_fijo_evit"] + S["mant_cal"]
    c_but = gas_kwh / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs")) * S["p_butano_bombona"] + S["mant_cal"]
    e_el_cal, e_el_acs = S["Q_cal"], S["Q_acs"]  # radiadores y termo: COP 1
    c_el = e_el_cal * p_cal + e_el_acs * p_acs
    e_ae_cal = S["Q_cal"] / (S["scop"] * S["f_emisor"])
    e_ae_acs = S["Q_acs"] / S["scop_acs"]
    pot = precios.potencia_regulada()
    c_pot = S["dP"] * pot[0] * (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    c_ae = e_ae_cal * p_cal + e_ae_acs * p_acs + c_pot + S["mant_aero"]
    costes = {"gas": c_gas, "butano": c_but, "electrica": c_el, "aero": c_ae}
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    co2 = {"gas": gas_kwh / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci"), "butano": gas_kwh / pci * r.get("emisiones.butano_kgco2_kwh_pci"),
           "electrica": e_el_cal * ef_cal + e_el_acs * ef_acs, "aero": e_ae_cal * ef_cal + e_ae_acs * ef_acs}
    act = ctx["actual"]
    N = int(r.get("acs.vida_util_bdc")[1])
    anios = np.arange(N)
    elec_act = act == "electrica"
    g_act = S["g_elec"] if elec_act else S["g_fuel"]
    ener_act = costes[act] - (S["mant_cal"] if not elec_act else 0)
    ener_ae = c_ae - S["mant_aero"]
    ah = ener_act[:, None] * (1 + g_act[:, None]) ** anios + (S["mant_cal"][:, None] if not elec_act else 0) \
        - ener_ae[:, None] * (1 + S["g_elec"][:, None]) ** anios - S["mant_aero"][:, None]
    cf = fin.flujos_proyecto(S["capex_aero"] - S["ayuda"] - S["reposicion"], ah)
    out = {"ahorro": costes[act] - c_ae, "van": fin.van(cf, S["r_desc"]), "payback": fin.payback(cf), "tir": fin.tir(cf) * 100,
           "e_aero": e_ae_cal + e_ae_acs, "co2_ahorro": co2[act] - co2["aero"]}
    for k in SISTEMAS:
        out[f"c_{k}"] = costes[k]
        out[f"co2_{k}"] = co2[k]
    return out


KPIS = [
    {"id": "ahorro", "nombre": "Ahorro anual con aerotermia frente a tu sistema", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "van", "nombre": "VAN del cambio", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "co2_ahorro", "nombre": "CO₂ evitado", "unidad": "kg/año", "clave": "co2_ahorro"},
    {"id": "e_aero", "nombre": "Electricidad de la aerotermia", "unidad": "kWh/año", "clave": "e_aero"},
    {"id": "tir", "nombre": "TIR", "unidad": "%", "clave": "tir", "fmt": "{:.1f}"},
] + [{"id": f"c_{k}", "nombre": f"Coste anual: {v}", "unidad": "€/año", "clave": f"c_{k}", "tipo": "coste"} for k, v in SISTEMAS.items()]


def graficos(out, ctx):
    b = [mc.p10_50_90(out[f"c_{k}"]) for k in SISTEMAS]
    return [{"tipo": "barras", "titulo": "Coste anual de calefacción + ACS (P10–P90)", "ylabel": "€/año", "categorias": list(SISTEMAS.values()),
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    return [{"Sistema": v, "Coste P10": round(mc.p10_50_90(out[f"c_{k}"])[0]), "Coste P50": round(mc.p10_50_90(out[f"c_{k}"])[1]),
             "Coste P90": round(mc.p10_50_90(out[f"c_{k}"])[2]), "CO₂ P50 (kg/año)": round(mc.p10_50_90(out[f"co2_{k}"])[1])} for k, v in SISTEMAS.items()]


def notas(out, ctx):
    return ["La demanda de calefacción es la cifra más incierta: depende del edificio y del uso. Si tienes facturas de invierno, ajústala en Avanzado.",
            "SCOP de campo (no de etiqueta) por zona climática, penalizado por emisores de alta temperatura.",
            "Se considera la potencia adicional a contratar al electrificar desde gas y la cuota fija de gas solo si abandonas el gas por completo."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, tabla=tabla, notas=notas)
