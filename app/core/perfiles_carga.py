"""Perfiles horarios sintéticos de consumo del hogar y simultaneidad de aparatos (demanda máxima)."""
from __future__ import annotations

import numpy as np

from . import clima, montecarlo as mc, precios, termico
from .calendario import calendario_tipico
from .herramienta import Param
from .perfil import Perfil
from .referencias import ref

COMPONENTES = ["base", "actividad", "cocina", "acs", "calefaccion", "refrigeracion", "ve", "piscina"]
ETIQUETAS = {"base": "Consumo base (nevera, standby)", "actividad": "Actividad (iluminación, TV, lavado)",
             "cocina": "Cocina", "acs": "Agua caliente eléctrica", "calefaccion": "Calefacción eléctrica",
             "refrigeracion": "Aire acondicionado", "ve": "Vehículo eléctrico", "piscina": "Piscina"}


def n_personas(perfil: Perfil) -> float:
    return ref().sub("perfil.personas", perfil.personas)[1]


def superficie_m2(perfil: Perfil) -> float:
    return ref().sub("perfil.superficie_m2", perfil.vivienda)[1]


def letra_zona(perfil: Perfil) -> str:
    z = clima.zona_cte(perfil.cp)
    return "A" if z.lower().startswith("alfa") else z[0]


def _norm(v):
    v = np.asarray(v, dtype=np.float64)
    s = v.sum()
    return (v / s) if s > 0 else np.full(v.shape, 1.0 / v.size)


def formas(perfil: Perfil) -> dict:
    """Forma horaria anual normalizada (suma 1) de cada componente, 8760 valores."""
    cal = calendario_tipico()
    h, mes, lab = cal["hora"], cal["mes"], cal["laborable"]
    r = ref()
    t = clima.t2m(perfil.cp)
    act_lab = np.asarray(r.get(f"forma.actividad_{perfil.ocupacion}"))
    act_fin = np.asarray(r.get("forma.actividad_finde"))
    est = np.asarray(r.get("perfil.estacionalidad_actividad"))[mes]
    f = {"base": _norm(np.asarray(r.get("forma.plana"))[h]),
         "actividad": _norm(np.where(lab, act_lab[h], act_fin[h]) * est),
         "cocina": _norm(np.asarray(r.get("forma.cocina"))[h])}
    tred = clima.t_red_mensual(perfil.cp)[mes]
    f["acs"] = _norm(np.asarray(r.get("forma.acs"))[h] * np.maximum(r.get("acs.t_uso_ducha_c")[1] - tred, 1.0))
    f["calefaccion"] = _norm(np.asarray(r.get("forma.calefaccion"))[h] * np.maximum(r.get("perfil.t_base_calefaccion_c") - t, 0))
    f["refrigeracion"] = _norm(np.asarray(r.get("forma.refrigeracion"))[h] * np.maximum(t - r.get("perfil.t_base_refrigeracion_c"), 0))
    f["ve"] = _norm(np.asarray(r.get("forma.ve_casa"))[h])
    mp = np.isin(mes, r.get("perfil.meses_piscina"))
    f["piscina"] = _norm(np.asarray(r.get("forma.piscina"))[h] * mp)
    return f


def energias_inferidas(perfil: Perfil) -> dict:
    """Mediana anual (kWh) de cada componente aplicable al hogar, a partir de referencias."""
    r = ref()
    ea = r.get("electrodomesticos.consumo_anual")
    npers = n_personas(perfil)
    fp = (npers / r.get("perfil.personas_referencia")) ** r.get("perfil.exponente_personas")
    m2 = superficie_m2(perfil)
    zl = letra_zona(perfil)
    eq = set(perfil.equipos)
    out = {}
    out["base"] = ea["nevera_combi"][1] + (ea["congelador"][1] if perfil.unifamiliar else 0.0) \
        + r.get("electrodomesticos.consumo_standby_hogar")[1] * 8.76
    out["actividad"] = fp * sum(ea[k][1] for k in ("lavadora", "lavavajillas", "television", "iluminacion_hogar", "ordenador"))
    if "induccion" in eq:
        out["cocina"] = r.get("cocina.induccion_consumo_kwh_ano_persona")[1] * npers + (ea["horno"][1] if "horno" in eq else 0.0)
    else:
        out["cocina"] = ea["horno"][1] if "horno" in eq else ea["horno"][0]
    if "termo_electrico" in eq:
        out["acs"] = acs_electrico_kwh(perfil, npers)
    if "calefaccion_electrica" in eq:
        out["calefaccion"] = m2 * r.get("calefaccion.demanda_kwh_m2_ano_por_zona")[zl][1] \
            * r.get("calefaccion.demanda_vs_anio_construccion")[r.get("perfil.edad_vivienda_defecto")]
    if "aire_acondicionado" in eq:
        out["refrigeracion"] = m2 * r.get("perfil.fraccion_superficie_climatizada_refrig")[1] \
            * r.get("refrigeracion.demanda_kwh_m2_ano_por_zona")[zl][1] / r.get("refrigeracion.seer_split")[1]
    if "ve" in eq:
        c = r.get("ve.consumo_wltp_kwh_100km")["compacto"][1] * r.get("ve.factor_consumo_real_vs_wltp")[1]
        out["ve"] = r.get("perfil.ve_km_dia")[1] * 365 * c / 100.0 / r.get("ve.eficiencia_carga_domestica")[1]
    if "piscina" in eq:
        out["piscina"] = r.get("electrodomesticos.potencia_nominal_kw")["bomba_piscina"][1] \
            * r.get("perfil.piscina_horas_dia")[1] * r.get("perfil.piscina_dias")[1]
    return out


def acs_electrico_kwh(perfil: Perfil, npers: float) -> float:
    """Consumo anual de un termo eléctrico con hábitos por defecto (T05 refina estos valores)."""
    r = ref()
    v = termico.volumen_uso_dia(npers, r.get("perfil.acs_duchas_persona_dia")[1], r.get("perfil.acs_ducha_min")[1],
                                r.get("acs.caudal_alcachofa_l_min")["estandar"][1], 0.0, 0.0, r.get("acs.otros_usos_l_persona_dia")[1])
    q = termico.energia_util_mensual(np.array([v]), r.get("acs.t_uso_ducha_c")[1], clima.t_red_mensual(perfil.cp))[0]
    util = float(np.sum(q * termico.DIAS_MES))
    perd = float(termico.perdidas_espera_kwh_dia(80, r.get("acs.perdidas_espera_termo_kwh_24h")["80"][1]) * 365)
    return util / r.get("acs.rendimiento_termo_electrico")["rendimiento_fraccion"][1] + perd


def inferir_componentes(perfil: Perfil) -> dict:
    """Parametros Param 'E_<componente>' (lognormal) con la energía anual de cada uso."""
    sg = ref().get("perfil.sg_componente")
    return {f"E_{c}": Param(f"E_{c}", f"Consumo anual: {ETIQUETAS[c]}", "kWh/año", mc.logn(med, sg))
            for c, med in energias_inferidas(perfil).items()}


def matriz_consumo(S: dict, F: dict, escala=None) -> np.ndarray:
    """E_t (n, 8760) float32 = Σ_c E_c · forma_c(t), con `escala` (n,) opcional (calibración con factura)."""
    cs = [c for c in COMPONENTES if f"E_{c}" in S]
    A = np.stack([np.asarray(S[f"E_{c}"], dtype=np.float32) for c in cs], axis=1)  # (n, C)
    if escala is not None:
        A = A * np.asarray(escala, dtype=np.float32)[:, None]
    B = np.stack([F[c] for c in cs]).astype(np.float32)  # (C, 8760)
    return A @ B


def escala_factura(perfil: Perfil, S: dict, rng, P_kw=None) -> np.ndarray | None:
    """Factor (n,) que lleva el consumo anual a su posterior combinando el prior por componentes con la inversión de la factura."""
    if perfil.factura == "nose":
        return None
    r = ref()
    n = len(next(iter(S.values())))
    prior = sum(np.asarray(S[k], float) for k in S if k.startswith("E_"))
    lo, mo, hi = r.sub("perfil.factura_mes_eur", perfil.factura)
    importe = rng.triangular(lo, mo, hi, n)
    pp = precios.potencia_precios("pvpc")
    P = perfil.potencia or r.get("tarifa.potencias_normalizadas")[4]
    om = np.mean([precios.datos.omie_anual(y)[:8760] for y in precios.datos.anios_completos()], axis=0)
    p_medio = float(np.mean(precios.precio_pvpc(om)))
    e_obs = precios.invertir_factura(importe, P, p_medio, pp)
    sg_p, sg_o = r.get("perfil.sg_prior_consumo"), r.get("perfil.sg_factura")
    wp, wo = 1 / np.log(sg_p) ** 2, 1 / np.log(sg_o) ** 2
    post = np.exp((wp * np.log(prior) + wo * np.log(e_obs)) / (wp + wo))
    return post / prior


def simular_pmax(perfil_equipos, n: int, rng, dias: int = 365, limitador: str | None = None, P_actual: float | None = None):
    """Demanda máxima anual (kW, cuartohoraria) por simultaneidad de aparatos. Devuelve (pmax (n,), pesos (n,)).

    Cada día cada aparato está en el pico con probabilidad p·(días activos/365). Si se conoce la respuesta sobre el limitador y la
    potencia actual, se ponderan las muestras por la coherencia entre los días con exceso simulados y la respuesta."""
    r = ref()
    pot = r.get("electrodomesticos.potencia_nominal_kw")
    prob = r.get("simultaneidad.prob_pico_diario")
    activos = r.get("simultaneidad.dias_activos")
    mapa = {"induccion": "induccion_3_fuegos", "horno": "horno", "termo_electrico": "termo_electrico",
            "aire_acondicionado": "split_aire_acondicionado", "calefaccion_electrica": "calefaccion_radiadores",
            "ve": "cargador_ve", "piscina": "bomba_piscina"}
    siempre = {"lavadora": "lavadora", "lavavajillas": "lavavajillas", "secadora": "secadora", "plancha": "plancha",
               "microondas": "microondas"}
    nombres = [k for k in mapa if k in perfil_equipos] + list(siempre)
    base = mc.muestrear(mc.tri(*r.get("simultaneidad.base_kw")), n, rng)
    total = np.broadcast_to(base[:, None], (n, dias)).copy()
    for k in nombres:
        clave = mapa.get(k) or siempre[k]
        lo, mo, hi = pot[clave]
        p_k = mc.muestrear(mc.tri(lo, mo, hi), n, rng)[:, None]
        pr = prob[k] * (activos.get(k, dias) / dias if k in activos else 1.0)
        total += (rng.random((n, dias)) < pr) * p_k
    pmax = total.max(axis=1)
    w = np.ones(n)
    if limitador and P_actual:
        exceso = (total > P_actual).sum(axis=1)
        lo, _, hi = r.sub("simultaneidad.dias_exceso_limitador", limitador)
        w = np.where((exceso >= lo) & (exceso <= hi), 1.0, 0.05)
    return pmax, w / w.sum()


def potencia_optima(pmax, pesos, alpha, normalizadas):
    """Menor potencia normalizada P con Pr(P_max > P) <= alpha (probabilidades ponderadas)."""
    for P in normalizadas:
        if float(np.sum(pesos[pmax > P])) <= alpha:
            return P
    return normalizadas[-1]
