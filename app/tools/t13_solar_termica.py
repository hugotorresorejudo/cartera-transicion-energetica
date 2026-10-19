"""T13 — Solar térmica para ACS: fracción solar, ahorro y retorno."""
from __future__ import annotations

import numpy as np

from core import clima, emisiones, finanzas as fin, fv, montecarlo as mc, perfiles_carga as pc, precios, termico
from core.herramienta import Param, Parametros, Pregunta, ejecutar, tri_rel
from core.perfil import Perfil
from core.referencias import ref
from core.termico import DIAS_MES
from tools import t01_tarifas as t01, t02_fv as t02

ID = "t13"
NOMBRE = "Solar térmica"
DESCRIPCION = "Captadores para agua caliente: fracción solar, ahorro y retorno."
MESES = list(range(1, 12 + 1))


def preguntas() -> list[Pregunta]:
    qs = [q for q in t02.preguntas() if q.id in ("orientacion", "inclinacion", "sombras")]
    qs += [Pregunta("captadores", "Captadores previstos", "select", [("1", "1"), ("2", "2"), ("3+", "3 o más")], "2"),
           Pregunta("actual", "Sistema actual de ACS", "select", [("termo", "Termo eléctrico"), ("gas", "Calentador de gas natural"), ("butano", "Butano")], "termo"),
           Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
           Pregunta("cp", "Código postal", "texto", perfil="cp")]
    return qs


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"orientacion": "S", "inclinacion": "poca", "sombras": "ninguna", "captadores": "2", "actual": "termo"}
    a.update(respuestas or {})
    D = mc.desde_rango
    b = t02.inferir(perfil, {k: a[k] for k in ("orientacion", "inclinacion", "sombras") if k in a})
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas", "r_desc") if k in base.params}
    p["r_desc"] = b.params["r_desc"]
    for k in ("azimut", "inclinacion", "L_sh", "g_elec"):
        p[k] = b.params[k]
    p["n_cap"] = Param("n_cap", "Número de captadores", "ud", mc.fijo(r.sub("solar_termica.n_captadores", a["captadores"])))
    p["a_cap"] = Param("a_cap", "Área de un captador", "m²", D(r.rango("solar_termica.area_captador_m2")))
    rc = r.get("solar_termica.rendimiento_captador")
    p["eta0"] = Param("eta0", "Rendimiento óptico η₀", "-", D(rc["eta0"]))
    p["a1"] = Param("a1", "Pérdidas lineales a₁", "W/m²K", D(rc["a1"]))
    p["a2"] = Param("a2", "Pérdidas cuadráticas a₂", "W/m²K²", D(rc["a2"]))
    p["t_col"] = Param("t_col", "Temperatura media del captador", "ºC", D(r.rango("solar_termica.t_colector_c")))
    p["eta_sis"] = Param("eta_sis", "Rendimiento del sistema (tuberías y acumulación)", "-", D(r.rango("solar_termica.eta_sistema")))
    p["f_dem"] = Param("f_dem", "Factor de demanda de ACS (CTE)", "×", mc.logn(1, r.get("solar_termica.sg_demanda")))
    p["capex_m2"] = Param("capex_m2", "Coste instalado", "€/m²", D(r.rango("solar_termica.capex_eur_m2")))
    p["mant"] = Param("mant", "Mantenimiento anual", "fracción CAPEX", D(r.rango("solar_termica.mantenimiento_anual_fraccion")))
    p["vida"] = Param("vida", "Vida útil", "años", mc.fijo(r.get("solar_termica.vida_util")[1]))
    p["ayuda"] = Param("ayuda", "Ayudas y deducciones (ver T11)", "€", mc.fijo(0))
    p["eta_act"] = Param("eta_act", "Rendimiento del sistema actual", "-",
                         mc.fijo(r.get("acs.rendimiento_termo_electrico")["rendimiento_fraccion"][1]) if a["actual"] == "termo"
                         else D(r.rango("acs.rendimiento_calentador_gas")))
    gv = r.get("gas.tur_termino_variable_tur1")
    p["p_gas"] = Param("p_gas", "Término variable del gas", "€/kWh sin impuestos", tri_rel(gv, r.get("gas.banda_variable")))
    pb = r.get("gas.butano_precio_bombona")
    p["bombona"] = Param("bombona", "Bombona de butano", "€", tri_rel(pb, r.get("gas.banda_bombona")))
    p["g_fuel"] = Param("g_fuel", "Inflación del gas", "fracción/año", D(r.rango("combustibles.inflacion_anual")))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": a["actual"]})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["n_cap"])
    # irradiancia sobre el plano del captador (kW/m²) a partir de la producción FV unitaria por kWp
    Gu = fv.generacion_unitaria(perfil.cp, S["azimut"], S["inclinacion"], rng) * (1 - S["L_sh"])[:, None].astype(np.float32)
    G = Gu / r.get("solar_termica.pr_fv_proxy")
    Ta = clima.t2m(perfil.cp)[None, :]
    dT = np.maximum(S["t_col"][:, None] - Ta, 0).astype(np.float32)
    Gs = np.maximum(G, r.get("solar_termica.umbral_g_kw_m2"))
    eta = np.clip(S["eta0"][:, None] - S["a1"][:, None] * dT / (Gs * 1000) - S["a2"][:, None] * dT ** 2 / (Gs * 1000), 0, None)
    eta = np.where(G > r.get("solar_termica.umbral_g_kw_m2"), eta, 0.0)
    area = S["n_cap"] * S["a_cap"]
    q_col = fv.suma_mensual(eta * G) * area[:, None] * S["eta_sis"][:, None]   # kWh útiles por mes
    v = termico.demanda_ref_cte_l_dia(pc.n_personas(perfil)) * S["f_dem"]
    q_acs = termico.energia_util_mensual(v, r.get("acs.t_referencia_c"), clima.t_red_mensual(perfil.cp)) * DIAS_MES  # (n,12)
    aporte_m = np.minimum(q_col, q_acs)
    solar = aporte_m.sum(axis=1)
    frac = solar / np.maximum(q_acs.sum(axis=1), 1e-9)
    act = ctx["actual"]
    if act == "termo":
        omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
        imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
        p_h = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]) * imp
        F = pc.formas_cached(Perfil.from_dict({**perfil.to_dict(), "equipos": sorted(set(perfil.equipos) | {"termo_electrico"})}))
        precio_kwh = p_h @ F["acs"].astype(np.float32)
        g_act = S["g_elec"]
    elif act == "gas":
        precio_kwh = (S["p_gas"] + r.get("gas.gas_natural_impuesto_hidrocarburos")) * (1 + r.get("gas.iva") / 100.0)
        g_act = S["g_fuel"]
    else:
        precio_kwh = S["bombona"] / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs"))
        g_act = S["g_fuel"]
    ahorro = solar / S["eta_act"] * precio_kwh
    capex = S["capex_m2"] * area
    N = int(round(float(np.median(S["vida"]))))
    ah = fin.serie_anual(ahorro, N, g_act, 0.0) - (S["mant"] * capex)[:, None]
    cf = fin.flujos_proyecto(capex - S["ayuda"], ah)
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    if act == "termo":
        co2 = solar / S["eta_act"] * float(pc.formas_cached(perfil)["acs"] @ emisiones.ef_anual_8760())
    else:
        co2 = solar / S["eta_act"] / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci" if act == "gas" else "emisiones.butano_kgco2_kwh_pci")
    return {"frac": frac * 100, "ahorro": ahorro, "van": fin.van(cf, S["r_desc"]), "payback": fin.payback(cf), "solar": solar, "capex": capex, "co2": co2,
            "area": area, "_q_col_m": q_col, "_q_acs_m": q_acs, "_aporte_m": aporte_m}


KPIS = [
    {"id": "frac", "nombre": "Fracción solar anual", "unidad": "%", "clave": "frac", "fmt": "{:.0f}"},
    {"id": "ahorro", "nombre": "Ahorro del primer año", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro"},
    {"id": "van", "nombre": "VAN", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "solar", "nombre": "Energía solar aportada", "unidad": "kWh/año", "clave": "solar"},
    {"id": "capex", "nombre": "Inversión", "unidad": "€", "clave": "capex", "tipo": "coste"},
    {"id": "co2", "nombre": "CO₂ evitado", "unidad": "kg/año", "clave": "co2"},
]


def graficos(out, ctx):
    ap = np.nanpercentile(out["_aporte_m"], [10, 50, 90], axis=0)
    dem = np.nanpercentile(out["_q_acs_m"], 50, axis=0)
    return [{"tipo": "abanico_multi", "titulo": "Aporte solar mensual frente a la demanda de ACS", "xlabel": "Mes", "ylabel": "kWh",
             "series": [{"nombre": "Aporte solar (P10–P90)", "x": MESES, "p10": ap[0].tolist(), "p50": ap[1].tolist(), "p90": ap[2].tolist()},
                        {"nombre": "Demanda de ACS (P50)", "x": MESES, "p10": dem.tolist(), "p50": dem.tolist(), "p90": dem.tolist()}]}]


def notas(out, ctx):
    return ["El CTE DB-HE 4 exige una contribución solar mínima en obra nueva o rehabilitación; esta herramienta evalúa la decisión voluntaria en vivienda existente.",
            "Modelo mensual con captador plano (curva η₀, a₁, a₂) y la irradiancia deducida de PVGIS; sin sobrecalentamiento ni recirculación."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, notas=notas)
