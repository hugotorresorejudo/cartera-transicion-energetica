"""T02 — Autoconsumo fotovoltaico: dimensionado, balance horario y rentabilidad."""
from __future__ import annotations

import numpy as np

from core import finanzas as fin, fv, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t02"
NOMBRE = "Autoconsumo fotovoltaico"
DESCRIPCION = "¿Compensa instalar placas, de qué potencia y cuánto ahorras?"


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
        Pregunta("cubierta", "Tipo de cubierta", "select",
                 [("inclinado", "Tejado propio inclinado"), ("plano", "Cubierta plana propia"),
                  ("bloque", "Piso en bloque (usa T14: autoconsumo colectivo)")], "inclinado"),
        Pregunta("orientacion", "Orientación del faldón (brújula del móvil)", "select",
                 [("S", "Sur"), ("SE_SO", "Sureste / suroeste"), ("E_O", "Este / oeste"), ("N", "Norte"), ("nose", "No lo sé")], "S"),
        Pregunta("inclinacion", "Inclinación", "select",
                 [("plana", "Plana"), ("poca", "Poco inclinada"), ("mucha", "Muy inclinada")], "poca"),
        Pregunta("sombras", "Sombras sobre el tejado", "select",
                 [("ninguna", "Ninguna"), ("parcial", "Parcial (mañana o tarde)"), ("mucha", "Muchas")], "ninguna"),
        Pregunta("tamano", "Tamaño útil del tejado", "select",
                 [("1", "Como 1 plaza de garaje"), ("2", "2 plazas"), ("3+", "3 o más"), ("nose", "No lo sé")], "2"),
        Pregunta("prevision", "¿Prevés VE o aerotermia en 5 años?", "select",
                 [("ninguno", "Ninguno"), ("ve", "VE"), ("aerotermia", "Aerotermia"), ("ambos", "Ambos")], "ninguno"),
    ]


def _perfil_ext(perfil: Perfil, prevision: str) -> Perfil:
    p = Perfil.from_dict(perfil.to_dict())
    eq = set(p.equipos)
    if prevision in ("ve", "ambos"):
        eq.add("ve")
    if prevision in ("aerotermia", "ambos"):
        eq.add("calefaccion_electrica")
    p.equipos = sorted(eq)
    return p


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"cubierta": "inclinado", "orientacion": "S", "inclinacion": "poca", "sombras": "ninguna", "tamano": "2",
         "prevision": "ninguno"}
    a.update(respuestas or {})
    pext = _perfil_ext(perfil, a["prevision"])
    base = t01.inferir(pext, {})
    p = dict(base.params)
    if a["prevision"] in ("aerotermia", "ambos") and "calefaccion_electrica" not in perfil.equipos:
        scop = r.get("calefaccion.bdc_scop_aerotermia")[pc.letra_zona(perfil)][1]  # la resistencia (COP 1) pasa a bomba de calor
        m = p["E_calefaccion"].dist["mediana"] / scop
        p["E_calefaccion"] = Param("E_calefaccion", "Consumo anual: aerotermia prevista", "kWh/año", mc.logn(m, r.get("perfil.sg_componente")))
    az = {"S": mc.fijo(0), "SE_SO": mc.disc([-45, 45]), "E_O": mc.disc([-90, 90]), "N": mc.fijo(180), "nose": mc.unif(-90, 90)}[a["orientacion"]]
    if a["cubierta"] == "plano" or a["inclinacion"] == "plana":
        tilt = mc.desde_rango(r.rango("fv.inclinacion_estructura_plana"))
    elif a["inclinacion"] == "poca":
        tilt = mc.desde_rango(r.rango("fv.inclinacion_tejado_teja"))
    else:
        tilt = mc.desde_rango(r.rango("fv.inclinacion_muy_inclinada"))
    p["azimut"] = Param("azimut", "Azimut (0 = sur, −90 = este, 90 = oeste)", "º", az)
    p["inclinacion"] = Param("inclinacion", "Inclinación del campo FV", "º", tilt)
    p["L_sh"] = Param("L_sh", "Pérdidas por sombreado", "fracción", mc.desde_rango(r.sub("fv.perdidas_sombreado", a["sombras"])))
    p["plazas"] = Param("plazas", "Tamaño útil del tejado", "plazas de garaje", mc.desde_rango(r.sub("fv.plazas_tamano", a["tamano"])))
    p["m2_plaza"] = Param("m2_plaza", "Superficie por plaza", "m²", mc.desde_rango(r.rango("fv.area_por_plaza_garaje_m2")))
    p["m2_kwp"] = Param("m2_kwp", "Superficie de tejado por kWp", "m²/kWp", mc.desde_rango(r.rango("fv.area_tejado_por_kwp_m2")))
    p["P_p_fija"] = Param("P_p_fija", "Potencia pico fija (0 = optimizar)", "kWp", mc.fijo(0))
    p["capex_wp"] = Param("capex_wp", "CAPEX a 4 kWp", "€/Wp", mc.desde_rango(r.rango("fv.capex_residencial_eur_wp")))
    p["opex_frac"] = Param("opex_frac", "OPEX anual", "fracción CAPEX", mc.desde_rango(r.rango("fv.opex_anual_fraccion_capex")))
    p["anio_inversor"] = Param("anio_inversor", "Año de sustitución del inversor", "año", mc.desde_rango(r.rango("fv.sustitucion_inversor_anio")))
    p["coste_inversor"] = Param("coste_inversor", "Coste del inversor", "€/kW", mc.desde_rango(r.rango("fv.sustitucion_inversor_coste_eur_kw")))
    p["degradacion"] = Param("degradacion", "Degradación anual", "fracción", mc.desde_rango(r.rango("fv.degradacion_anual")))
    p["p_exc"] = Param("p_exc", "Precio de compensación de excedentes", "€/kWh", mc.desde_rango(r.rango("fv.precio_excedentes_medio")))
    p["modo_exc"] = Param("modo_exc", "Excedentes: 0 = precio fijo, 1 = precio de mercado horario", "-", mc.fijo(0))
    p["modalidad"] = Param("modalidad", "Tarifa de referencia: 0 = PVPC, 1 = fija, 2 = indexada", "-", mc.fijo(0))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", mc.desde_rango(r.rango("fv.tasa_descuento_hogar")))
    p["g_elec"] = Param("g_elec", "Inflación del precio de la electricidad", "fracción/año", mc.desde_rango(r.rango("fv.inflacion_electricidad")))
    p["ayudas"] = Param("ayudas", "Ayudas y deducciones (ver T11)", "€", mc.fijo(0))
    p["ef_evitado"] = Param("ef_evitado", "Factor de emisión evitado", "kgCO₂/kWh", mc.desde_rango(r.rango("emisiones.fv_evitado_marginal")))
    horizonte = int(r.get("fv.horizonte_anios"))
    return Parametros(p, {"perfil": perfil.to_dict(), "perfil_ext": pext.to_dict(), "horizonte": horizonte,
                          "prevision": a["prevision"], "cubierta": a["cubierta"]})


def _consumo(S, ctx, rng, perfil, pext):
    actuales = set(pc.inferir_componentes(perfil))
    nuevos = {k for k in S if k.startswith("E_") and k not in actuales}
    esc, importe = pc.escala_factura(perfil, {k: v for k, v in S.items() if k in actuales}, rng)
    F = pc.formas_cached(pext)
    sin = {k[2:] for k in nuevos}
    E = pc.matriz_consumo(S, F, esc, sin_escala=sin) * S["f_consumo"][:, None].astype(np.float32)
    return E, importe


def _precio(S, omie, per):
    ca, lam = S["c_aj"][:, None], S["perdidas"][:, None]
    cod = int(round(float(S["modalidad"][0])))
    if cod == 1:
        return precios.precio_fijo(S["p_fija"], False, per), "fija"
    if cod == 2:
        return precios.precio_indexado(omie, per, S["margen_idx"][:, None], ca, lam), "idx"
    return precios.precio_pvpc(omie, per, c_aj=ca, perdidas=lam), "pvpc"


def _ahorro1(Gu, Pp, E, p_e, p_exc, S, pot, P1, P2, bono, base_total):
    G = Gu * Pp[:, None].astype(np.float32)
    Sb, X, I = fv.balance(G, E)
    B = fv.compensacion(X, I, p_exc, p_e)
    tot = precios.factura(I, p_e, P1, P2, pot, bono, credito=B)["total"]
    return base_total - tot, Sb, G


def modelo(S, ctx, rng):
    perfil, pext = Perfil.from_dict(ctx["perfil"]), Perfil.from_dict(ctx["perfil_ext"])
    n = len(S["f_omie"])
    E, _ = _consumo(S, ctx, rng, perfil, pext)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    per = precios.periodos()
    p_e, mod = _precio(S, omie, per)
    pot = precios.potencia_precios(mod, S["pot_fija_dia"] if mod == "fija" else None)
    P1, P2, bono = S["P1"], S["P1"] + S["P2_delta"], S["bono"]
    base_total = precios.factura(E, p_e, P1, P2, pot, bono)["total"]
    p_exc = np.where(S["modo_exc"][:, None] > 0.5, np.maximum(omie, 0) / 1000.0, S["p_exc"][:, None]).astype(np.float32)
    Gu = fv.generacion_unitaria(perfil.cp, S["azimut"], S["inclinacion"], rng)
    Gu = Gu * (1 - S["L_sh"])[:, None].astype(np.float32)
    P_max = np.minimum(S["plazas"] * S["m2_plaza"] / S["m2_kwp"], ref().get("fv.compensacion_simplificada_potencia_max_kw"))
    N = ctx["horizonte"]
    anios = np.arange(1, N + 1)
    r_ref, e_ref = ref(), ref().get("fv.potencia_capex_ref_kwp")
    expo = r_ref.get("fv.economia_escala_exponente")

    def van_de(Pp, idx=slice(None)):
        a1, Sb, G = _ahorro1(Gu[idx], Pp, E[idx], p_e if p_e.ndim == 1 else p_e[idx], p_exc[idx], S, pot,
                             P1[idx], P2[idx], bono[idx], base_total[idx])
        capex = Pp * 1000 * S["capex_wp"][idx] * (np.maximum(Pp, 0.1) / e_ref) ** expo
        ah = fin.serie_anual(a1, N, S["g_elec"][idx], S["degradacion"][idx])
        extras = np.zeros_like(ah)
        k = np.clip(np.round(S["anio_inversor"][idx]).astype(int), 1, N) - 1
        extras[np.arange(ah.shape[0]), k] = -S["coste_inversor"][idx] * Pp
        cf = fin.flujos_proyecto(capex - S["ayudas"][idx], ah, S["opex_frac"][idx] * capex, extras)
        return fin.van(cf, S["r_desc"][idx]), cf, a1, Sb, G

    # dimensionado: P_p* que maximiza el VAN esperado con un subconjunto de muestras
    fija = float(np.median(S["P_p_fija"]))
    k_cand = int(r_ref.get("fv.n_candidatos"))
    sub = slice(0, min(n, int(r_ref.get("fv.n_muestras_dimensionado"))))
    hi = float(np.median(P_max))
    lo = min(1.0, hi)
    grid = np.linspace(lo, hi, k_cand) if fija <= 0 else np.array([fija])
    curva = np.stack([van_de(np.minimum(np.full(n, g), P_max)[sub], sub)[0] for g in grid], axis=1)
    Pstar = float(grid[int(np.argmax(curva.mean(axis=0)))]) if fija <= 0 else fija
    Pp = np.minimum(np.full(n, Pstar), P_max)
    van, cf, a1, Sb, G = van_de(Pp)
    sc, ss = fv.indicadores(Sb, G, E)
    return {"van": van, "tir": fin.tir(cf), "payback": fin.payback(cf), "ahorro1": a1, "sc": sc * 100, "ss": ss * 100,
            "co2": G.sum(axis=1) * S["ef_evitado"] / 1000.0, "Pp": Pp, "curva": curva, "grid": grid,
            "generacion": G.sum(axis=1), "capex": Pp * 1000 * S["capex_wp"] * (np.maximum(Pp, 0.1) / e_ref) ** expo}


KPIS = [
    {"id": "van", "nombre": "VAN a 25 años", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "ahorro1", "nombre": "Ahorro del primer año", "unidad": "€/año", "clave": "ahorro1", "tipo": "ahorro"},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}"},
    {"id": "Pp", "nombre": "Potencia pico recomendada", "unidad": "kWp", "clave": "Pp", "fmt": "{:.1f}"},
    {"id": "tir", "nombre": "TIR", "unidad": "%", "clave": "tir_pct", "fmt": "{:.1f}"},
    {"id": "sc", "nombre": "Autoconsumo (SC)", "unidad": "%", "clave": "sc", "fmt": "{:.0f}"},
    {"id": "ss", "nombre": "Autosuficiencia (SS)", "unidad": "%", "clave": "ss", "fmt": "{:.0f}"},
    {"id": "co2", "nombre": "CO₂ evitado", "unidad": "t/año", "clave": "co2", "fmt": "{:.2f}"},
    {"id": "capex", "nombre": "Inversión inicial", "unidad": "€", "clave": "capex", "tipo": "coste"},
]


def _modelo_con_pct(S, ctx, rng):
    o = modelo(S, ctx, rng)
    o["tir_pct"] = o["tir"] * 100
    return o


def graficos(out, ctx):
    b = np.nanpercentile(out["curva"], [10, 50, 90], axis=0)
    return [{"tipo": "abanico", "titulo": "VAN según la potencia instalada (P10–P90)", "xlabel": "Potencia pico (kWp)", "ylabel": "VAN (€)",
             "x": out["grid"].tolist(), "p10": b[0].tolist(), "p50": b[1].tolist(), "p90": b[2].tolist()}]


def notas(out, ctx):
    n = [f"Potencia óptima de partida: {float(np.median(out['Pp'])):.1f} kWp (máximo VAN esperado sobre el área disponible)."]
    if ctx["cubierta"] == "bloque":
        n.append("Vives en un bloque: valora el autoconsumo colectivo (T14).")
    n.append("Balance neto horario; compensación simplificada mensual con tope en el término de energía (RD 244/2019).")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, _modelo_con_pct, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, notas=notas)
