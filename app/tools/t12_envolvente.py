"""T12 — Rehabilitación de la envolvente: aislamiento de fachada y cubierta y cambio de ventanas."""
from __future__ import annotations

import numpy as np

from core import emisiones, finanzas as fin, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar, tri_rel
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t12"
NOMBRE = "Rehabilitación de envolvente"
DESCRIPCION = "Aislamiento y ventanas: cuánto reduces la calefacción y en cuánto tiempo se paga."
MEDIDAS = {"fachada": "Aislamiento de fachada (SATE)", "cubierta": "Aislamiento de cubierta", "ventanas": "Ventanas nuevas"}
CLAVE_AHORRO = {"fachada": "sate_fachada", "cubierta": "cubierta", "ventanas": "ventanas"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("medidas", "¿Qué vas a hacer?", "multi", [(k, v) for k, v in MEDIDAS.items()], ["fachada", "ventanas"]),
        Pregunta("edad", "Antigüedad del edificio", "select", [("pre1980", "Anterior a 1980"), ("1980", "1980–2006"), ("2007", "Desde 2007")], "pre1980"),
        Pregunta("tipo", "Tipo de edificio", "select", [("intermedio", "Piso intermedio"), ("ultima", "Piso en última planta o esquina"), ("adosada", "Unifamiliar adosada"),
                                                      ("aislada", "Unifamiliar aislada")], "intermedio"),
        Pregunta("calefaccion", "Tu calefacción", "select", [("gas", "Gas natural"), ("butano", "Butano"), ("electrica", "Radiadores eléctricos"), ("aero", "Aerotermia")], "gas"),
        Pregunta("uso", "Uso de la calefacción", "select", [("todo", "Casi todo el día"), ("tardes", "Tardes y noches"), ("ocasional", "Ocasional")], "tardes"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", [("piso_<70", "Piso <70 m²"), ("piso_70_120", "Piso 70–120 m²"), ("piso_>120", "Piso >120 m²"),
                                                                   ("unif_<120", "Unifamiliar <120 m²"), ("unif_>120", "Unifamiliar >120 m²")], perfil="vivienda"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"medidas": ["fachada", "ventanas"], "edad": "pre1980", "tipo": "intermedio", "calefaccion": "gas", "uso": "tardes"}
    a.update(respuestas or {})
    D = mc.desde_rango
    m2 = pc.superficie_m2(perfil)
    edad = r.sub("calefaccion.edad", a["edad"])
    d = pc.demanda_calefaccion_util(perfil, edad)
    uso = r.sub("calefaccion.uso", a["uso"])
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    p["Q_cal"] = Param("Q_cal", "Demanda útil de calefacción", "kWh/año", mc.logn(d[1] * uso[1], r.get("calefaccion.sg_demanda")))
    fed = r.sub("envolvente.factor_ahorro_edad", a["edad"])
    sup = r.sub("envolvente.superficie_fachada_ratio", r.sub("envolvente.tipos_edificio", a["tipo"]))
    for m in a["medidas"]:
        p[f"ahorro_{m}"] = Param(f"ahorro_{m}", f"Reducción de la demanda: {MEDIDAS[m]}", "fracción", D(tuple(min(x * fed, r.get("envolvente.reduccion_max")) for x in r.get("envolvente.ahorro_tipico_fraccion")[CLAVE_AHORRO[m]])))
    p["a_fachada"] = Param("a_fachada", "Superficie de fachada opaca", "m²", D(tuple(x * m2 for x in sup)))
    p["a_cubierta"] = Param("a_cubierta", "Superficie de cubierta", "m²", mc.fijo(m2 / (r.get("envolvente.pisos_unifamiliar") if a["tipo"] in ("adosada", "aislada") else 1.0)
                                                                      * r.sub("envolvente.tiene_cubierta", a["tipo"])))
    p["a_huecos"] = Param("a_huecos", "Superficie de ventanas", "m²", D(tuple(x * m2 for x in r.rango("envolvente.superficie_huecos_ratio"))))
    p["c_fachada"] = Param("c_fachada", "Coste del SATE", "€/m²", D(r.rango("envolvente.coste_aislamiento_sate_eur_m2")))
    p["c_cubierta"] = Param("c_cubierta", "Coste del aislamiento de cubierta", "€/m²", D(r.rango("envolvente.coste_aislamiento_cubierta_eur_m2")))
    p["c_ventana"] = Param("c_ventana", "Coste de las ventanas", "€/m²", D(r.rango("envolvente.coste_ventana_eur_m2")))
    sistema = a["calefaccion"]
    D2 = mc.fijo
    if sistema in ("gas", "butano"):
        p["eta"] = Param("eta", "Rendimiento de la caldera (PCS)", "-", D(r.rango("calefaccion.caldera_gas_rendimiento_estacional_pcs")))
        gv = r.get("gas.tur_termino_variable_tur1")
        p["p_gas"] = Param("p_gas", "Término variable del gas", "€/kWh sin impuestos", tri_rel(gv, r.get("gas.banda_variable")))
        pb = r.get("gas.butano_precio_bombona")
        p["bombona"] = Param("bombona", "Bombona de butano", "€", tri_rel(pb, r.get("gas.banda_bombona")))
    elif sistema == "aero":
        p["eta"] = Param("eta", "SCOP de la aerotermia", "-", D(r.get("calefaccion.bdc_scop_aerotermia")[pc.letra_zona(perfil)]))
    else:
        p["eta"] = Param("eta", "Rendimiento de los radiadores", "-", D2(r.get("envolvente.cop_electrica")))
    p["g_energia"] = Param("g_energia", "Inflación de la energía", "fracción/año", D(r.rango("combustibles.inflacion_anual" if sistema in ("gas", "butano") else "fv.inflacion_electricidad")))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    p["vida"] = Param("vida", "Vida útil de las medidas", "años", D2(min(r.get("envolvente.vida_util_aislamiento")[0], r.get("envolvente.horizonte_max"))))
    p["incluir_ayuda"] = Param("incluir_ayuda", "Incluir ayuda de rehabilitación (1 = sí)", "-", D2(0))
    p["ayuda_extra"] = Param("ayuda_extra", "Otras ayudas y deducciones (ver T11)", "€", D2(0))
    return Parametros(p, {"perfil": perfil.to_dict(), "medidas": list(a["medidas"]), "sistema": sistema})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["Q_cal"])
    # reducción combinada: 1 − Π(1 − f_i)
    prod = np.ones(n)
    capex = np.zeros(n)
    detalle = {}
    for m in ctx["medidas"]:
        f = S[f"ahorro_{m}"]
        prod = prod * (1 - f)
        coste = {"fachada": S["a_fachada"] * S["c_fachada"], "cubierta": S["a_cubierta"] * S["c_cubierta"], "ventanas": S["a_huecos"] * S["c_ventana"]}[m]
        capex += coste
        detalle[m] = (f, coste)
    red = 1 - prod
    kwh_ahorro_util = S["Q_cal"] * red
    sistema = ctx["sistema"]
    if sistema in ("gas", "butano"):
        kwh_final = kwh_ahorro_util / S["eta"]
        if sistema == "gas":
            precio = (S["p_gas"] + r.get("gas.gas_natural_impuesto_hidrocarburos")) * (1 + r.get("gas.iva") / 100.0)
        else:
            precio = S["bombona"] / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs"))
        pci = r.get("emisiones.gas_conversion_pcs_pci")
        co2 = kwh_final / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci" if sistema == "gas" else "emisiones.butano_kgco2_kwh_pci")
    else:
        kwh_final = kwh_ahorro_util / S["eta"]
        omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
        imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
        p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]) * imp
        F = pc.formas_cached(Perfil.from_dict({**perfil.to_dict(), "equipos": sorted(set(perfil.equipos) | {"calefaccion_electrica"})}))
        precio = p_h @ F["calefaccion"].astype(np.float32)
        co2 = kwh_final * float(F["calefaccion"] @ emisiones.ef_anual_8760())
    ahorro = kwh_final * precio
    # ayuda de rehabilitación según el nivel de ahorro alcanzado
    tabla = r.get("ayudas.rehabilitacion_envolvente")
    um = r.get("envolvente.umbrales_ahorro")
    pct = np.where(red >= um["ahorro_60"], tabla["ahorro_60"]["porcentaje"], np.where(red >= um["ahorro_45"], tabla["ahorro_45"]["porcentaje"],
                                                                                      np.where(red >= um["ahorro_30"], tabla["ahorro_30"]["porcentaje"], 0.0)))
    tope = np.where(red >= um["ahorro_60"], tabla["ahorro_60"]["tope_eur_vivienda"], np.where(red >= um["ahorro_45"], tabla["ahorro_45"]["tope_eur_vivienda"],
                                                                                              np.where(red >= um["ahorro_30"], tabla["ahorro_30"]["tope_eur_vivienda"], 0.0)))
    ayuda = (S["incluir_ayuda"] > 0.5) * np.minimum(pct * capex, tope) + S["ayuda_extra"]
    N = int(round(float(np.median(S["vida"]))))
    ah = fin.serie_anual(ahorro, N, S["g_energia"], 0.0)
    cf = fin.flujos_proyecto(capex - ayuda, ah)
    out = {"red": red * 100, "ahorro": ahorro, "van": fin.van(cf, S["r_desc"]), "payback": fin.payback(cf), "capex": capex, "kwh": kwh_final, "co2": co2,
           "ayuda": ayuda, "_det": detalle, "_precio": precio}
    for m, (f, c) in detalle.items():
        out[f"capex_{m}"] = c
        out[f"red_{m}"] = f * 100
    return out


KPIS = [
    {"id": "red", "nombre": "Reducción de la demanda de calefacción", "unidad": "%", "clave": "red", "fmt": "{:.0f}"},
    {"id": "ahorro", "nombre": "Ahorro del primer año", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro"},
    {"id": "van", "nombre": "VAN", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "capex", "nombre": "Inversión", "unidad": "€", "clave": "capex", "tipo": "coste"},
    {"id": "kwh", "nombre": "Energía final ahorrada", "unidad": "kWh/año", "clave": "kwh"},
    {"id": "co2", "nombre": "CO₂ evitado", "unidad": "kg/año", "clave": "co2"},
]


def graficos(out, ctx):
    ms = list(out["_det"])
    b = [mc.p10_50_90(out[f"capex_{m}"]) for m in ms]
    return [{"tipo": "barras", "titulo": "Inversión por medida (P10–P90)", "ylabel": "€", "categorias": [MEDIDAS[m] for m in ms],
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    return [{"Medida": MEDIDAS[m], "Inversión P50 (€)": round(mc.p10_50_90(out[f"capex_{m}"])[1]), "Reducción de la demanda P50 (%)": round(mc.p10_50_90(out[f"red_{m}"])[1])}
            for m in out["_det"]]


def notas(out, ctx):
    return ["Las reducciones se combinan multiplicativamente (1 − Π(1 − fᵢ)): dos medidas no suman sus ahorros.",
            "La inversión en envolvente tiene retornos largos pero aporta confort y reduce la potencia de calefacción necesaria (útil antes de elegir aerotermia en T08).",
            "Para incluir la ayuda de rehabilitación del programa PRTR, ponla a 1 en Avanzado (sin verificar en fuente primaria)."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, tabla=tabla, notas=notas)
