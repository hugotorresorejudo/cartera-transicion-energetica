"""T09 — Cocina de inducción frente a gas natural, butano o vitrocerámica."""
from __future__ import annotations

import numpy as np

from core import emisiones, finanzas as fin, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t09"
NOMBRE = "Inducción vs gas"
DESCRIPCION = "Cocina: placa de inducción frente a gas o vitrocerámica."
SISTEMAS = {"gas": "Gas natural", "butano": "Butano", "vitro": "Vitrocerámica", "ind": "Inducción"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("actual", "¿Con qué cocinas ahora?", "select", [("gas", "Gas natural"), ("butano", "Butano"), ("vitro", "Vitrocerámica")], "gas"),
        Pregunta("frecuencia", "¿Cuánto cocinas?", "select", [("poco", "Poco"), ("normal", "Normal"), ("mucho", "Mucho")], "normal"),
        Pregunta("otros_gas", "¿Usas gas para algo más (agua caliente, calefacción)?", "select", [("si", "Sí"), ("no", "No")], "si"),
        Pregunta("reforma", "¿Hay que reformar la instalación eléctrica?", "select", [("si", "Sí"), ("no", "No"), ("nose", "No lo sé")], "nose"),
        Pregunta("menaje", "¿Tu menaje es apto para inducción?", "select", [("si", "Sí"), ("no", "No"), ("nose", "No lo sé")], "nose"),
        Pregunta("repone", "¿Hay que cambiar la placa actual de todos modos?", "select", [("si", "Sí"), ("no", "No")], "no"),
        Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"actual": "gas", "frecuencia": "normal", "otros_gas": "si", "reforma": "nose", "menaje": "nose", "repone": "no"}
    a.update(respuestas or {})
    D = mc.desde_rango
    npers = pc.n_personas(perfil)
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    p["E_gas"] = Param("E_gas", "Gas para cocinar (a gas)", "kWh/año", mc.logn(r.get("cocina.gas_consumo_kwh_ano_persona")[1] * npers, r.get("perfil.sg_componente")))
    p["frecuencia"] = Param("frecuencia", "Factor de frecuencia de cocinado", "×", D(r.sub("cocina.frecuencia", a["frecuencia"])))
    p["eta_gas"] = Param("eta_gas", "Rendimiento de la cocina de gas", "-", D(r.rango("cocina.rendimiento_gas_cocina")))
    p["eta_ind"] = Param("eta_ind", "Rendimiento de la inducción", "-", D(r.rango("cocina.rendimiento_induccion")))
    p["eta_vitro"] = Param("eta_vitro", "Rendimiento de la vitrocerámica", "-", D(r.rango("cocina.rendimiento_vitro")))
    gv = r.get("gas.tur_termino_variable_tur1")
    p["p_gas"] = Param("p_gas", "Término variable del gas", "€/kWh sin impuestos", D((0.9 * gv, gv, 1.2 * gv)))
    pb = r.get("gas.butano_precio_bombona")
    p["bombona"] = Param("bombona", "Bombona de butano", "€", mc.tri(0.92 * pb, pb, 1.08 * pb))
    fijo = (r.get("gas.tur_termino_fijo_tur1") + r.get("gas.alquiler_contador")) * 12 * (1 + r.get("gas.iva") / 100.0)
    p["gas_fijo_evit"] = Param("gas_fijo_evit", "Cuota fija de gas evitada", "€/año", mc.fijo(0 if a["otros_gas"] == "si" else fijo))
    p["capex_ind"] = Param("capex_ind", "Placa de inducción", "€", D(r.rango("cocina.capex_induccion_eur")))
    reforma = {"si": D(r.rango("cocina.instalacion_induccion_adicional_eur")), "no": mc.fijo(0), "nose": D(r.rango("cocina.instalacion_induccion_adicional_eur"))}[a["reforma"]]
    p["reforma"] = Param("reforma", "Adaptación de la instalación", "€", reforma)
    p["menaje"] = Param("menaje", "Menaje compatible", "€", mc.fijo(0) if a["menaje"] == "si" else D(r.rango("cocina.menaje_eur")))
    p["reposicion"] = Param("reposicion", "Coste de la placa actual que te ahorras", "€",
                            D(r.rango("cocina.capex_gas_eur")) if a["repone"] == "si" else mc.fijo(0))
    p["dP"] = Param("dP", "Potencia adicional a contratar", "kW", D(r.get("cocina.potencia_extra_kw")))
    p["g_elec"] = Param("g_elec", "Inflación de la electricidad", "fracción/año", D(r.rango("fv.inflacion_electricidad")))
    p["g_fuel"] = Param("g_fuel", "Inflación del gas", "fracción/año", D(r.rango("combustibles.inflacion_anual")))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": a["actual"]})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["E_gas"])
    util = S["E_gas"] * S["frecuencia"] * S["eta_gas"]  # energía útil de cocinado
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]) * imp
    F = pc.formas_cached(perfil)
    p_coc = p_h @ F["cocina"].astype(np.float32)
    ef = float(F["cocina"] @ emisiones.ef_anual_8760())
    iva = 1 + r.get("gas.iva") / 100.0
    e_gas = util / S["eta_gas"]
    c_gas = e_gas * (S["p_gas"] + r.get("gas.gas_natural_impuesto_hidrocarburos")) * iva + S["gas_fijo_evit"]
    c_but = e_gas / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs")) * S["bombona"]
    e_vitro = util / S["eta_vitro"]
    e_ind = util / S["eta_ind"]
    pot = precios.potencia_regulada()
    c_pot = S["dP"] * pot[0] * imp
    c_vitro = e_vitro * p_coc
    c_ind = e_ind * p_coc + c_pot
    costes = {"gas": c_gas, "butano": c_but, "vitro": c_vitro, "ind": c_ind}
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    co2 = {"gas": e_gas / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci"), "butano": e_gas / pci * r.get("emisiones.butano_kgco2_kwh_pci"),
           "vitro": e_vitro * ef, "ind": e_ind * ef}
    act = ctx["actual"]
    N = int(r.get("cocina.vida_util"))
    anios = np.arange(N)
    g_act = S["g_elec"] if act == "vitro" else S["g_fuel"]
    ah = costes[act][:, None] * (1 + g_act[:, None]) ** anios - c_ind[:, None] * (1 + S["g_elec"][:, None]) ** anios
    cf = fin.flujos_proyecto(S["capex_ind"] + S["reforma"] + S["menaje"] - S["reposicion"], ah)
    out = {"ahorro": costes[act] - c_ind, "van": fin.van(cf, S["r_desc"]), "payback": fin.payback(cf), "co2_ahorro": co2[act] - co2["ind"],
           "e_ind": e_ind}
    for k in SISTEMAS:
        out[f"c_{k}"] = costes[k]
        out[f"co2_{k}"] = co2[k]
    return out


KPIS = [
    {"id": "ahorro", "nombre": "Ahorro anual con inducción frente a tu cocina", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "van", "nombre": "VAN del cambio", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "co2_ahorro", "nombre": "CO₂ evitado", "unidad": "kg/año", "clave": "co2_ahorro"},
    {"id": "e_ind", "nombre": "Electricidad de la inducción", "unidad": "kWh/año", "clave": "e_ind"},
] + [{"id": f"c_{k}", "nombre": f"Coste anual: {v}", "unidad": "€/año", "clave": f"c_{k}", "tipo": "coste"} for k, v in SISTEMAS.items()]


def graficos(out, ctx):
    b = [mc.p10_50_90(out[f"c_{k}"]) for k in SISTEMAS]
    return [{"tipo": "barras", "titulo": "Coste anual de cocinar (P10–P90)", "ylabel": "€/año", "categorias": list(SISTEMAS.values()),
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    return [{"Sistema": v, "Coste P50 (€/año)": round(mc.p10_50_90(out[f"c_{k}"])[1]), "CO₂ P50 (kg/año)": round(mc.p10_50_90(out[f"co2_{k}"])[1])}
            for k, v in SISTEMAS.items()]


def notas(out, ctx):
    return ["El ahorro es pequeño en términos absolutos: la decisión suele pesar más por seguridad, aire interior y comodidad que por coste.",
            "Si el gas solo se usa para cocinar, abandonar el gas elimina también la cuota fija anual."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, tabla=tabla, notas=notas)
