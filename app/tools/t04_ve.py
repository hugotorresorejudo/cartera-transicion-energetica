"""T04 — Vehículo eléctrico: TCO frente a una alternativa y estrategia de carga de mínimo coste."""
from __future__ import annotations

import numpy as np

from core import carga, clima, emisiones, finanzas as fin, montecarlo as mc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t04"
NOMBRE = "Vehículo eléctrico: TCO y carga"
DESCRIPCION = "¿Te sale a cuenta un eléctrico? Coste total, €/km, km de equilibrio y cuándo cargar."


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("km_lab", "Kilómetros típicos en un día laborable", "select",
                 [("<20", "Menos de 20"), ("20-50", "20–50"), ("50-100", "50–100"), (">100", "Más de 100")], "20-50"),
        Pregunta("viajes", "Viajes largos al año (>300 km)", "select",
                 [("ninguno", "Ninguno"), ("1-5", "1–5"), ("6-15", "6–15"), (">15", "Más de 15")], "1-5"),
        Pregunta("parking", "¿Dónde duerme el coche?", "select",
                 [("garaje_propio", "Garaje propio"), ("garaje_comunitario", "Plaza en garaje comunitario"), ("calle", "En la calle")], "garaje_propio"),
        Pregunta("horario", "Llegada a casa y salida", "select",
                 [("a", "Llego ~17 h, salgo ~8 h"), ("b", "Llego ~19 h, salgo ~8 h"), ("c", "Llego ~21 h, salgo ~7 h"),
                  ("d", "Llego ~19 h, salgo ~10 h")], "b"),
        Pregunta("segmento", "Segmento", "select", [("urbano", "Urbano"), ("compacto", "Compacto"), ("suv_berlina", "SUV o berlina")], "compacto"),
        Pregunta("alternativa", "Alternativa a comparar", "select",
                 [("gasolina", "Gasolina"), ("diesel", "Diésel"), ("hibrido", "Híbrido"), ("phev", "Híbrido enchufable")], "gasolina"),
        Pregunta("anios", "Años que lo mantendrás", "select", [("3-5", "3–5"), ("6-9", "6–9"), ("10+", "10 o más")], "6-9"),
    ]


def _interp_vr(tabla: dict, N: float):
    ks = sorted(int(k) for k in tabla)
    v = np.array([tabla[k] if k in tabla else tabla[str(k)] for k in ks], float)
    return tuple(float(np.interp(N, ks, v[:, i])) for i in range(3))


def _f_temp(cp):
    """Multiplicador anual de consumo por temperatura: media mensual de f(T) con T de la serie TMY (min, moda, max)."""
    tab = ref().get("ve.factor_temperatura_consumo")
    ts = sorted(tab, key=float)
    t = clima.t2m(cp)
    from core.termico import DIAS_MES
    tm = np.array([t[i:i + d * 24].mean() for i, d in zip(np.cumsum(np.r_[0, DIAS_MES[:-1]]) * 24, DIAS_MES)])
    out = [float(np.mean(np.interp(tm, [float(k) for k in ts], [tab[k][i] for k in ts]))) for i in range(3)]
    return out


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"km_lab": "20-50", "viajes": "1-5", "parking": "garaje_propio", "horario": "b", "segmento": "compacto",
         "alternativa": "gasolina", "anios": "6-9"}
    a.update(respuestas or {})
    seg, alt = a["segmento"], a["alternativa"]
    N = int(r.sub("ve.anios_tenencia", a["anios"]))
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    D = mc.desde_rango
    p["km_lab"] = Param("km_lab", "Km en día laborable", "km/día", D(r.sub("ve.km_laborable", a["km_lab"])))
    p["km_fds"] = Param("km_fds", "Km de fines de semana", "km/año", D(r.rango("ve.km_fin_de_semana_ano")))
    p["n_viajes"] = Param("n_viajes", "Viajes largos", "viajes/año", D(r.sub("ve.viajes_largos", a["viajes"])))
    p["d_viaje"] = Param("d_viaje", "Distancia de un viaje largo", "km", D(r.rango("ve.km_viaje_largo")))
    p["c_ev"] = Param("c_ev", "Consumo WLTP del VE", "kWh/100 km", D(r.sub("ve.consumo_wltp_kwh_100km", seg)))
    p["f_real"] = Param("f_real", "Consumo real / WLTP", "×", D(r.rango("ve.factor_consumo_real_vs_wltp")))
    p["f_temp"] = Param("f_temp", "Factor de consumo por temperatura (clima del CP)", "×", D(_f_temp(perfil.cp)))
    p["eta_ch"] = Param("eta_ch", "Eficiencia de carga", "-", D(r.rango("ve.eficiencia_carga_domestica")))
    p["phi"] = Param("phi", "Fracción de energía en carga pública", "-", D(r.sub("ve.fraccion_carga_publica_por_aparcamiento", a["parking"])))
    ac, dc = r.get("ve.coste_carga_publica_eur_kwh")["ac"], r.get("ve.coste_carga_publica_eur_kwh")["dc"]
    p["p_pub"] = Param("p_pub", "Precio de la carga pública", "€/kWh", mc.tri(ac[0], 0.5 * (ac[1] + dc[1]), dc[2]))
    p["P_ch"] = Param("P_ch", "Potencia del cargador doméstico", "kW", mc.fijo(r.sub("ve.potencia_cargador_kw", a["parking"])))
    p["precio_ev"] = Param("precio_ev", "Precio de compra del VE", "€", D(r.sub("ve.precio_compra_ve_eur", seg)))
    p["precio_alt"] = Param("precio_alt", "Precio de compra de la alternativa", "€", D(r.sub(f"ve.precio_compra_{alt if alt != 'diesel' else 'diesel'}_eur", seg)))
    p["c_alt"] = Param("c_alt", "Consumo WLTP de la alternativa", "L/100 km", D(r.get("ice.consumo_l_100km")[alt][seg]))
    gas = r.rango("combustibles.precio_diesel_eur_l" if alt == "diesel" else "combustibles.precio_gasolina_95_eur_l")
    p["p_fuel"] = Param("p_fuel", "Precio del combustible", "€/L", D(gas))
    p["g_fuel"] = Param("g_fuel", "Inflación del combustible", "fracción/año", D(r.rango("combustibles.inflacion_anual")))
    p["g_elec"] = Param("g_elec", "Inflación de la electricidad", "fracción/año", D(r.rango("fv.inflacion_electricidad")))
    p["mant_ev"] = Param("mant_ev", "Mantenimiento y neumáticos del VE", "€/km", D(r.rango("ve.coste_mantenimiento_ve_eur_km")))
    p["mant_alt"] = Param("mant_alt", "Mantenimiento y neumáticos de la alternativa", "€/km", D(r.rango("ice.coste_mantenimiento_eur_km")))
    p["seg_ev"] = Param("seg_ev", "Seguro del VE", "€/año", D(r.rango("ve.seguro_anual_eur")))
    p["seg_alt"] = Param("seg_alt", "Seguro de la alternativa", "€/año", D(r.rango("ice.seguro_anual_eur")))
    p["ivtm"] = Param("ivtm", "IVTM", "€/año", D(r.rango("impuestos.ivtm_medio_eur")))
    p["bonif_ivtm"] = Param("bonif_ivtm", "Bonificación IVTM del VE", "fracción", D(r.rango("ayudas.ivtm_bonificacion_ve")))
    vre, vra = _interp_vr(r.get("ve.valor_residual_fraccion")["ve"], N), _interp_vr(r.get("ve.valor_residual_fraccion")["ice"], N)
    p["vr_ev"] = Param("vr_ev", "Valor residual del VE", "fracción del precio", D(vre))
    p["vr_alt"] = Param("vr_alt", "Valor residual de la alternativa", "fracción del precio", D(vra))
    p["r_desc"] = Param("r_desc", "Tasa de descuento", "fracción", D(r.rango("fv.tasa_descuento_hogar")))
    p["f_ayuda"] = Param("f_ayuda", "Fracción de la deducción IRPF aprovechada", "-", mc.tri(*r.get("ve.f_ayuda")))
    arr, dep = r.sub("ve.horarios", a["horario"])
    return Parametros(p, {"perfil": perfil.to_dict(), "seg": seg, "alt": alt, "parking": a["parking"], "N": N, "arr": int(arr), "dep": int(dep)})


def _carga(S, ctx, rng, E_dia_kwh):
    """Coste anual (€ con impuestos) y emisiones de la carga doméstica óptima y de la carga al llegar.

    Devuelve (coste_opt, coste_base, kg_opt, kg_base, kwh_no_cubiertos_dia) para E_dia_kwh (n,) energía de red al día."""
    r = ref()
    n = len(E_dia_kwh)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    p = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None])
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    PP = (p * imp).reshape(n, 365, 24)
    ext = np.concatenate([PP, np.roll(PP, -1, axis=1)], axis=2)
    idx = carga.ventana_horas(ctx["arr"], ctx["dep"])
    Pw = ext[:, :, idx]
    ef = emisiones.ef_mes_hora()
    from core.calendario import calendario_tipico
    mes_dia = calendario_tipico()["mes"].reshape(365, 24)[:, 0]
    EFw = ef[mes_dia[:, None], (idx % 24)[None, :]][None].astype(np.float32)
    Pch = float(np.median(S["P_ch"]))
    orden = np.argsort(Pw, axis=2)
    Ps = np.take_along_axis(Pw, orden, axis=2)
    c_opt, falta, w_opt = carga.coste_voraz(Ps, Pch, E_dia_kwh[:, None], ordenar=False)
    EFs = np.take_along_axis(np.broadcast_to(EFw, Pw.shape), orden, axis=2)
    kg_opt = (w_opt * EFs).sum(2) * Pch
    c_base, _, w_b = carga.coste_voraz(Pw, Pch, E_dia_kwh[:, None], ordenar=False)
    kg_base = (w_b * np.broadcast_to(EFw, Pw.shape)).sum(2) * Pch
    return c_opt.sum(1), c_base.sum(1), kg_opt.sum(1), kg_base.sum(1), falta.mean(1)


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["km_lab"])
    K = 52 * r.get("ve.laborables_semana") * S["km_lab"] + S["km_fds"] + S["n_viajes"] * S["d_viaje"]
    K_viajes = S["n_viajes"] * S["d_viaje"]
    c_bat = S["c_ev"] * S["f_real"] * S["f_temp"] / 100.0 / S["eta_ch"]   # kWh de red por km
    phi = np.clip(S["phi"] + (1 - S["phi"]) * K_viajes / np.maximum(K, 1), 0, 1)
    kwh_total = K * c_bat
    E_dia = np.where(ctx["parking"] == "calle", 0.0, kwh_total * (1 - phi) / 365.0)
    c_opt, c_base, kg_opt, kg_base, falta_dia = _carga(S, ctx, rng, np.maximum(E_dia, 1e-6))
    if ctx["parking"] == "calle":
        c_opt = c_base  # sin garaje no hay optimización posible
        kg_opt = kg_base
    # energía que no cabe en la ventana (potencia o tiempo insuficientes) -> carga pública
    kwh_home = np.maximum(E_dia - falta_dia, 0) * 365
    kwh_pub = kwh_total - kwh_home
    N = ctx["N"]
    anios = np.arange(1, N + 1)
    D_flat = np.sum((1 + S["r_desc"][:, None]) ** (-anios), axis=1)
    D_e = np.sum((1 + S["g_elec"][:, None]) ** (anios - 1) / (1 + S["r_desc"][:, None]) ** anios, axis=1)
    D_f = np.sum((1 + S["g_fuel"][:, None]) ** (anios - 1) / (1 + S["r_desc"][:, None]) ** anios, axis=1)
    desc_N = (1 + S["r_desc"]) ** (-N)
    # energía eléctrica por km (€/km) y TCO como función afín de K
    e_km_ev = (c_opt + S["p_pub"] * kwh_pub) / np.maximum(K, 1)
    ded = np.minimum(r.get("ve.ayudas_compra")["deduccion_irpf_fraccion"] * S["precio_ev"], r.get("ve.ayudas_compra")["tope_deduccion_eur"])
    ayuda = S["f_ayuda"] * ded
    fijo_ev = S["precio_ev"] - ayuda + (S["seg_ev"] + S["ivtm"] * (1 - S["bonif_ivtm"])) * D_flat - S["vr_ev"] * S["precio_ev"] * desc_N
    var_ev = S["mant_ev"] * D_flat + e_km_ev * D_e
    # alternativa
    alt = ctx["alt"]
    if alt == "phev":
        fe = mc.muestrear(mc.desde_rango(r.rango("emisiones.phev_fraccion_electrica_uso_real")), n, rng)
        l_km = (1 - fe) * r.get("ice.consumo_l_100km")["hibrido"][ctx["seg"]][1] * S["f_real"] / 100.0
        e_km_alt_e = fe * c_bat * (c_opt / np.maximum(kwh_total * (1 - phi), 1e-9) * (1 - phi) + S["p_pub"] * phi)
    else:
        l_km = S["c_alt"] * S["f_real"] / 100.0
        e_km_alt_e = 0.0
        fe = np.zeros(n)
    var_alt = S["mant_alt"] * D_flat + l_km * S["p_fuel"] * D_f + e_km_alt_e * D_e
    fijo_alt = S["precio_alt"] + (S["seg_alt"] + S["ivtm"]) * D_flat - S["vr_alt"] * S["precio_alt"] * desc_N
    tco_ev, tco_alt = fijo_ev + var_ev * K, fijo_alt + var_alt * K
    crf = fin.crf(S["r_desc"], N)
    with np.errstate(divide="ignore", invalid="ignore"):
        k_eq = np.where(var_alt > var_ev, (fijo_ev - fijo_alt) / (var_alt - var_ev), np.nan)
    ef_fuel = r.get("emisiones.pozo_a_rueda_diesel_kgco2_l" if alt == "diesel" else "emisiones.pozo_a_rueda_gasolina_kgco2_l")
    ef_pub = float(np.mean(emisiones.ef_mes_hora()))
    co2_ev = (kg_opt * (kwh_home / np.maximum(E_dia * 365, 1e-9)) + kwh_pub * ef_pub) / 1000.0
    co2_alt = (K * l_km * ef_fuel + fe * K * c_bat * ef_pub) / 1000.0
    return {"dtco": tco_alt - tco_ev, "ckm_ev": tco_ev * crf / K, "ckm_alt": tco_alt * crf / K, "ahorro_carga": c_base - c_opt,
            "k_eq": k_eq, "tco_ev": tco_ev, "tco_alt": tco_alt, "K": K, "co2_ev": co2_ev, "co2_alt": co2_alt}


KPIS = [
    {"id": "dtco", "nombre": "Ahorro total del VE frente a la alternativa (TCO)", "unidad": "€", "clave": "dtco", "tipo": "ahorro",
     "prob": ("Probabilidad de que el VE sea más barato", lambda v: v > 0)},
    {"id": "ckm_ev", "nombre": "Coste por km del VE (con CRF)", "unidad": "€/km", "clave": "ckm_ev", "tipo": "coste", "fmt": "{:.3f}"},
    {"id": "ahorro_carga", "nombre": "Ahorro de la carga optimizada", "unidad": "€/año", "clave": "ahorro_carga", "tipo": "ahorro"},
    {"id": "ckm_alt", "nombre": "Coste por km de la alternativa", "unidad": "€/km", "clave": "ckm_alt", "tipo": "coste", "fmt": "{:.3f}"},
    {"id": "k_eq", "nombre": "Km anuales de equilibrio", "unidad": "km/año", "clave": "k_eq"},
    {"id": "K", "nombre": "Kilómetros al año", "unidad": "km/año", "clave": "K"},
    {"id": "tco_ev", "nombre": "TCO del VE", "unidad": "€", "clave": "tco_ev", "tipo": "coste"},
    {"id": "tco_alt", "nombre": "TCO de la alternativa", "unidad": "€", "clave": "tco_alt", "tipo": "coste"},
    {"id": "co2_ev", "nombre": "CO₂ del VE (pozo a rueda)", "unidad": "t/año", "clave": "co2_ev", "fmt": "{:.2f}"},
    {"id": "co2_alt", "nombre": "CO₂ de la alternativa (pozo a rueda)", "unidad": "t/año", "clave": "co2_alt", "fmt": "{:.2f}"},
]


def graficos(out, ctx):
    b = [mc.p10_50_90(out["tco_ev"]), mc.p10_50_90(out["tco_alt"])]
    g = [{"tipo": "barras", "titulo": "TCO en valor presente (P10–P90)", "ylabel": "€", "categorias": ["Eléctrico", "Alternativa"],
          "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]
    # plan de carga de un día típico resuelto como LP con HiGHS
    ys, M = __import__("core.datos", fromlist=["x"]).omie_matriz()
    perfil_h = M.mean(axis=0).reshape(365, 24).mean(axis=0) / 1000.0 + precios.peajes_cargos_energia()[2]
    idx = carga.ventana_horas(ctx["arr"], ctx["dep"])
    ext = np.concatenate([perfil_h, perfil_h])
    Pch = ref().sub("ve.potencia_cargador_kw", ctx["parking"])
    E = float(np.median(out["K"])) * ref().get("ve.consumo_wltp_kwh_100km")[ctx["seg"]][1] / 100.0 / 365
    x, _ = carga.plan_lp(ext[idx], np.ones(len(idx)), Pch, min(E, Pch * len(idx)))
    if x is not None:
        base = np.zeros(len(idx))
        resto = min(E, Pch * len(idx))
        for i in range(len(idx)):
            base[i] = min(Pch, resto)
            resto -= base[i]
        g.append({"tipo": "lineas", "titulo": "Plan de carga de un día típico (LP): óptimo frente a cargar al llegar",
                  "xlabel": "Hora (desde la llegada)", "ylabel": "kWh por hora",
                  "series": [{"nombre": "Óptimo", "x": [int(h % 24) for h in idx], "y": x.tolist()},
                             {"nombre": "Al llegar", "x": [int(h % 24) for h in idx], "y": base.tolist()}], "categorico": True})
    return g


def notas(out, ctx):
    n = ["El valor residual es la mayor fuente de incertidumbre; las ayudas (IRPF, sucesor del MOVES) son volátiles.",
         "Emisiones del pozo a la rueda: electricidad con la intensidad horaria del sistema y combustibles con el factor upstream+combustión."]
    if ctx["parking"] == "calle":
        n.append("Sin garaje no hay carga doméstica optimizable: la mayor parte de la energía se paga en carga pública.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="dtco", graficos=graficos, notas=notas)
