"""T05 — Agua caliente sanitaria: bomba de calor frente a termo eléctrico, calentador de gas o butano."""
from __future__ import annotations

import numpy as np

from core import clima, emisiones, finanzas as fin, fv, montecarlo as mc, precios, termico
from core.herramienta import Param, Parametros, Pregunta, ejecutar, tri_rel
from core.perfil import Perfil
from core.referencias import ref
from core.termico import DIAS_MES
from tools import t01_tarifas as t01

ID = "t05"
NOMBRE = "ACS: bomba de calor vs termo o gas"
DESCRIPCION = "Cuánto gastas en agua caliente y si compensa una bomba de calor."
MESES = list(range(1, 12 + 1))
SISTEMAS = {"termo": "Termo eléctrico", "gas": "Calentador de gas natural", "butano": "Butano", "bdc": "Bomba de calor"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
        Pregunta("duchas", "Duchas por persona y día", "select", [("<1", "Menos de 1"), ("1", "1"), (">1", "Más de 1")], "1"),
        Pregunta("duracion", "Duración típica de la ducha", "select", [("menos5", "Menos de 5 min"), ("5a10", "5–10 min"), ("mas10", "Más de 10 min")], "5a10"),
        Pregunta("banera", "Baños en bañera", "select", [("nunca", "Nunca"), ("semanal", "Semanal"), ("diario", "Diario")], "nunca"),
        Pregunta("alcachofa", "Tipo de alcachofa", "select", [("estandar", "Estándar"), ("ahorradora", "Ahorradora"), ("lluvia", "Tipo lluvia"),
                                                              ("nose", "No lo sé")], "estandar"),
        Pregunta("actual", "Sistema actual", "select", [("termo", "Termo eléctrico"), ("gas", "Calentador de gas natural"), ("butano", "Butano"),
                                                        ("mixta", "Caldera mixta"), ("nose", "No lo sé")], "termo"),
        Pregunta("ubicacion", "Dónde iría el equipo", "select", [("exterior", "Galería o terraza"), ("interior", "Cuarto interior"),
                                                                  ("garaje", "Garaje o trastero")], "interior"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"duchas": "1", "duracion": "5a10", "banera": "nunca", "alcachofa": "estandar", "actual": "termo", "ubicacion": "interior",
         "personas": perfil.personas}
    a.update(respuestas or {})
    pers = a.get("personas") or perfil.personas
    D = mc.desde_rango
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    actual = "termo" if a["actual"] == "nose" else a["actual"]
    caudal = r.get("acs.caudal_alcachofa_l_min")
    q = D(caudal["estandar"]) if a["alcachofa"] == "nose" else D(caudal[a["alcachofa"]])
    if a["alcachofa"] == "nose":
        q = mc.tri(caudal["ahorradora"][0], caudal["estandar"][1], caudal["lluvia"][2])
    p["n_pers"] = Param("n_pers", "Personas", "personas", D(r.sub("perfil.personas", pers)))
    p["duchas"] = Param("duchas", "Duchas por persona y día", "1/día", D(r.sub("acs.duchas_persona_dia", a["duchas"])))
    p["minutos"] = Param("minutos", "Duración de la ducha", "min", D(r.sub("acs.duracion_ducha_min", a["duracion"])))
    p["caudal"] = Param("caudal", "Caudal de la alcachofa", "L/min", q)
    p["banera_l"] = Param("banera_l", "Volumen de bañera", "L", D(r.rango("acs.volumen_banera_l")))
    p["banera_freq"] = Param("banera_freq", "Frecuencia de baños", "baños/día", D(r.sub("acs.banera_freq_dia", a["banera"])))
    p["otros_l"] = Param("otros_l", "Otros usos (lavabo, cocina)", "L/persona·día", D(r.rango("acs.otros_usos_l_persona_dia")))
    p["t_uso"] = Param("t_uso", "Temperatura de uso", "ºC", D(r.rango("acs.t_uso_ducha_c")))
    p["t_ac_termo"] = Param("t_ac_termo", "Temperatura de acumulación del termo", "ºC", mc.fijo(r.get("acs.t_acumulacion_c")[1]))
    p["t_ac_bdc"] = Param("t_ac_bdc", "Temperatura de acumulación de la BdC", "ºC", mc.fijo(r.get("acs.t_acumulacion_bdc_c")))
    p["perd_termo"] = Param("perd_termo", "Pérdidas en espera (termo 100 L)", "kWh/24 h", D(r.get("acs.perdidas_espera_termo_kwh_24h")["100"]))
    p["perd_bdc"] = Param("perd_bdc", "Pérdidas en espera (BdC 200 L)", "kWh/24 h", D(r.rango("acs.bdc_perdidas_espera_kwh_24h")))
    p["cop_nom"] = Param("cop_nom", "COP nominal (EN 16147, A7→55 ºC)", "-", D(r.rango("acs.bdc_cop_nominal_acs")))
    p["t_min_bdc"] = Param("t_min_bdc", "Temperatura mínima del aire sin apoyo", "ºC", D(r.rango("acs.bdc_tmin_aire_c")))
    p["P_el_bdc"] = Param("P_el_bdc", "Potencia eléctrica del compresor", "kW", D(r.rango("acs.bdc_potencia_electrica_kw")))
    p["eta_gas"] = Param("eta_gas", "Rendimiento del equipo de gas (PCS)", "-",
                         D(r.rango("acs.rendimiento_caldera_estandar_pcs" if actual == "mixta" else "acs.rendimiento_calentador_gas")))
    gas_var = r.get("gas.tur_termino_variable_tur1")
    lib = r.rango("gas.oferta_libre_tipica")
    p["p_gas"] = Param("p_gas", "Término variable del gas", "€/kWh sin impuestos", mc.tri(min(gas_var, lib[0]), gas_var, max(gas_var, lib[2])))
    p["gas_fijo_evit"] = Param("gas_fijo_evit", "Cuota fija de gas que se evita al dejar el gas (con IVA)", "€/año", D(r.rango("gas.cuota_fija_evitable")))
    p["p_butano_bombona"] = Param("p_butano_bombona", "Precio de la bombona de butano", "€", tri_rel(r.get("gas.butano_precio_bombona"), r.get("gas.banda_bombona")))
    p["g_elec"] = Param("g_elec", "Inflación de la electricidad", "fracción/año", D(r.rango("fv.inflacion_electricidad")))
    p["g_fuel"] = Param("g_fuel", "Inflación del gas", "fracción/año", D(r.rango("combustibles.inflacion_anual")))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    p["capex_bdc"] = Param("capex_bdc", "CAPEX de la bomba de calor", "€", D(r.rango("acs.capex_bdc_acs_eur")))
    p["ayuda"] = Param("ayuda", "Ayudas y deducciones (ver T11)", "€", mc.fijo(0))
    p["reposicion"] = Param("reposicion", "Coste de reponer tu sistema actual (si ya hay que cambiarlo)", "€", mc.fijo(0))
    p["programacion"] = Param("programacion", "Programación en horas baratas (1 = sí)", "-", mc.fijo(0))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": actual, "ubicacion": a["ubicacion"]})


def _t_aire(cp, ubicacion):
    t = clima.t2m(cp)
    t_int = ref().rango("acs.t_interior_c")[1]
    return {"exterior": t, "interior": np.full(8760, t_int), "garaje": 0.5 * (t + t_int)}[ubicacion]


def _horario(S, ctx, n):
    """Series horarias de demanda útil de ACS por muestra: (n, 8760) kWh térmicos y la demanda diaria (n, 365)."""
    perfil = Perfil.from_dict(ctx["perfil"])
    v = termico.volumen_uso_dia(S["n_pers"], S["duchas"], S["minutos"], S["caudal"], S["banera_l"], S["banera_freq"], S["otros_l"])
    qd_mes = termico.energia_util_mensual(v, S["t_uso"], clima.t_red_mensual(perfil.cp))  # (n, 12) kWh/día
    from core.calendario import calendario_tipico
    cal = calendario_tipico()
    qd = qd_mes[:, cal["mes"].reshape(365, 24)[:, 0]]  # (n, 365)
    forma = np.asarray(ref().get("forma.acs"), float)
    forma = forma / forma.sum()
    q_h = (qd[:, :, None] * forma[None, None, :]).reshape(n, 8760)
    return v, qd_mes, qd, q_h


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["n_pers"])
    perfil = Perfil.from_dict(ctx["perfil"])
    v, qd_mes, qd, q_h = _horario(S, ctx, n)
    util_anual = (qd_mes * DIAS_MES).sum(1)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None])
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    pe = (p_h * imp).astype(np.float32)  # €/kWh con impuestos
    t_air = _t_aire(perfil.cp, ctx["ubicacion"]).astype(np.float32)
    dt_ref = r.get("acs.dt_ref_perdidas_k")
    # --- termo eléctrico (80–150 L según demanda) y BdC 200 L
    perd_t = S["perd_termo"][:, None] * (np.maximum(S["t_ac_termo"][:, None] - t_air[None, :], 0) / dt_ref).astype(np.float32) / 24.0
    perd_b = S["perd_bdc"][:, None] * (np.maximum(S["t_ac_bdc"][:, None] - t_air[None, :], 0) / dt_ref).astype(np.float32) / 24.0
    e_termo_h = q_h + perd_t
    ens = r.get("acs.condiciones_ensayo")
    eta_c = termico.eta_carnot_desde_cop_nominal(S["cop_nom"], ens["t_aire_c"], ens["t_agua_c"])  # η_C que reproduce el COP nominal
    cop = termico.cop_carnot(t_air[None, :], S["t_ac_bdc"][:, None], eta_c[:, None]).astype(np.float32)
    cop = np.where(t_air[None, :] < S["t_min_bdc"][:, None], 1.0, cop)  # por debajo del límite entra el apoyo eléctrico
    e_bdc_h = (q_h + perd_b) / cop
    prog = float(np.median(S["programacion"])) > 0.5

    def coste_programado(q_dia, P_el_kw, cop_h):
        """Llena las horas más baratas por kWh térmico (p/COP) hasta cubrir la demanda diaria, con P_el máxima por hora."""
        pc = pe.reshape(n, 365, 24)
        cp_ = cop_h.reshape(n, 365, 24)
        c = pc / cp_
        orden = np.argsort(c, axis=2)
        cap = np.take_along_axis(P_el_kw * cp_, orden, axis=2)  # kWh térmicos por hora
        ps = np.take_along_axis(pc, orden, axis=2)
        cum = np.cumsum(cap, axis=2) - cap
        w = np.clip((q_dia[:, :, None] - cum) / np.maximum(cap, 1e-9), 0, 1)
        return (w * P_el_kw * ps).sum(axis=(1, 2)), (w * P_el_kw).sum(axis=(1, 2))

    P_termo = r.get("electrodomesticos.potencia_nominal_kw")["termo_electrico"][1]
    qd_perd_t = qd + perd_t.reshape(n, 365, 24).sum(2)
    qd_perd_b = qd + perd_b.reshape(n, 365, 24).sum(2)
    c_termo_prog, _ = coste_programado(qd_perd_t, P_termo, np.ones((n, 8760), np.float32))
    c_bdc_prog, _ = coste_programado(qd_perd_b, S["P_el_bdc"][:, None, None], cop)
    c_termo_base = (e_termo_h * pe).sum(1, dtype=np.float64)
    c_bdc_base = (e_bdc_h * pe).sum(1, dtype=np.float64)
    c_termo_e = c_termo_prog if prog else c_termo_base
    c_bdc_e = c_bdc_prog if prog else c_bdc_base
    mant = r.get("acs.mantenimiento_anual_eur")
    mtermo, mgas, mbdc = (mant[k][1] for k in ("termo_electrico", "calentador_gas", "bdc"))
    # --- gas natural y butano (rendimiento sobre PCS)
    F = util_anual / S["eta_gas"]
    iva = 1 + r.get("gas.iva") / 100.0
    c_gas = F * (S["p_gas"] + r.get("gas.gas_natural_impuesto_hidrocarburos")) * iva + S["gas_fijo_evit"] + mgas
    p_but = S["p_butano_bombona"] / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs"))
    c_but = F * p_but + mgas
    c_termo = c_termo_e + mtermo
    c_bdc = c_bdc_e + mbdc
    costes = {"termo": c_termo, "gas": c_gas, "butano": c_but, "bdc": c_bdc}
    # --- sistema actual, ahorro, VAN y payback (el gas sube con g_fuel, la electricidad con g_elec)
    act = {"termo": "termo", "gas": "gas", "mixta": "gas", "butano": "butano"}[ctx["actual"]]
    N = int(r.get("acs.vida_util_bdc")[1])
    anios = np.arange(N)
    es_elec_act = act == "termo"
    g_act = S["g_elec"] if es_elec_act else S["g_fuel"]
    ener_act = (c_termo_e if es_elec_act else costes[act] - mgas)
    mant_act = mtermo if es_elec_act else mgas
    ah = (ener_act[:, None] * (1 + g_act[:, None]) ** anios + mant_act) - (c_bdc_e[:, None] * (1 + S["g_elec"][:, None]) ** anios + mbdc)
    cf = fin.flujos_proyecto(S["capex_bdc"] - S["ayuda"] - S["reposicion"], ah)
    van = fin.van(cf, S["r_desc"])
    # --- emisiones (kg/año)
    ef_h = emisiones.ef_anual_8760().astype(np.float32)
    co2 = {"termo": (e_termo_h * ef_h).sum(1), "bdc": (e_bdc_h * ef_h).sum(1)}
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    co2["gas"] = F / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci")
    co2["butano"] = F / pci * r.get("emisiones.butano_kgco2_kwh_pci")
    v60 = termico.v60_equivalente(v, S["t_uso"], clima.t_red_mensual(perfil.cp).mean(), r.get("acs.t_referencia_c"))
    ref_cte = r.get("acs.demanda_referencia_l_persona_dia_60c") * S["n_pers"]
    out = {"ahorro": costes[act] - c_bdc, "van": van, "payback": fin.payback(cf), "util": util_anual, "v60": v60, "ref_cte": ref_cte,
           "e_bdc_mes": fv.suma_mensual(e_bdc_h), "ahorro_prog": c_bdc_base - c_bdc_prog,
           "tir": fin.tir(cf) * 100}
    for k in SISTEMAS:
        out[f"c_{k}"] = costes[k]
        out[f"co2_{k}"] = co2[k]
    return out


KPIS = [
    {"id": "ahorro", "nombre": "Ahorro anual con bomba de calor frente a tu sistema", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "van", "nombre": "VAN del cambio a bomba de calor", "unidad": "€", "clave": "van", "tipo": "ahorro",
     "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "util", "nombre": "Energía útil de ACS", "unidad": "kWh/año", "clave": "util"},
    {"id": "v60", "nombre": "Agua equivalente a 60 ºC", "unidad": "L/día", "clave": "v60", "fmt": "{:.0f}"},
    {"id": "tir", "nombre": "TIR", "unidad": "%", "clave": "tir", "fmt": "{:.1f}"},
    {"id": "ahorro_prog", "nombre": "Ahorro adicional por programar la BdC en horas baratas", "unidad": "€/año", "clave": "ahorro_prog", "tipo": "ahorro"},
] + [{"id": f"c_{k}", "nombre": f"Coste anual: {nombre}", "unidad": "€/año", "clave": f"c_{k}", "tipo": "coste"} for k, nombre in SISTEMAS.items()] \
  + [{"id": f"co2_{k}", "nombre": f"CO₂: {nombre}", "unidad": "kg/año", "clave": f"co2_{k}"} for k, nombre in SISTEMAS.items()]


def graficos(out, ctx):
    b = [mc.p10_50_90(out[f"c_{k}"]) for k in SISTEMAS]
    mes = np.nanpercentile(out["e_bdc_mes"], [10, 50, 90], axis=0)
    return [{"tipo": "barras", "titulo": "Coste anual por sistema de ACS (P10–P90)", "ylabel": "€/año", "categorias": list(SISTEMAS.values()),
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]},
            {"tipo": "abanico", "titulo": "Consumo eléctrico mensual de la bomba de calor", "xlabel": "Mes", "ylabel": "kWh",
             "x": MESES, "p10": mes[0].tolist(), "p50": mes[1].tolist(), "p90": mes[2].tolist()}]


def tabla(out, ctx):
    return [{"Sistema": nombre, "Coste P10 (€/año)": round(mc.p10_50_90(out[f"c_{k}"])[0]), "Coste P50": round(mc.p10_50_90(out[f"c_{k}"])[1]),
             "Coste P90": round(mc.p10_50_90(out[f"c_{k}"])[2]), "CO₂ P50 (kg/año)": round(mc.p10_50_90(out[f"co2_{k}"])[1])} for k, nombre in SISTEMAS.items() for nombre in [nombre]]


def notas(out, ctx):
    v, c = float(np.median(out["v60"])), float(np.median(out["ref_cte"]))
    n = [f"Demanda estimada equivalente a {v:.0f} L/día a 60 ºC frente a {c:.0f} L/día de referencia del CTE DB-HE 4 ({v / c:.0%})."]
    n.append("No se modelan recirculación, pérdidas de distribución ni ciclos antilegionela, que aumentan el consumo real.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, tabla=tabla, notas=notas)
