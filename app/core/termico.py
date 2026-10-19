"""Modelo térmico común: ACS (volumen, energía, pérdidas), COP de bomba de calor y demanda de calefacción/refrigeración."""
from __future__ import annotations

import numpy as np

from .referencias import ref

RHO_CP = 1.163  # Wh/(L·K), constante física del agua
K0 = 273.15  # K
DIAS_MES = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def volumen_uso_dia(n_pers, duchas, minutos, caudal, banera_l, banera_freq, otros_l_pers):
    """V_uso (L/día a T_uso) = n·(d·t·q) + V_bañera·frecuencia + n·V_otros. Todos broadcastables."""
    return n_pers * (duchas * minutos * caudal + otros_l_pers) + banera_l * banera_freq


def energia_util_mensual(v_uso, t_uso, t_red_mes):
    """Q (kWh/día) por mes con t_red_mes (12,) y v_uso/t_uso (n,)."""
    v = np.asarray(v_uso, float)[..., None]
    tu = np.asarray(t_uso, float)[..., None]
    return RHO_CP * v * np.maximum(tu - t_red_mes, 0.0) / 1000.0


def cop_carnot(t_aire, t_ac, eta_c):
    """COP = η_C · T_h / (T_h − T_c), T_h = T_ac y T_c = T_aire (en K), acotado a un rango físico razonable."""
    th = np.asarray(t_ac, float) + K0
    tc = np.asarray(t_aire, float) + K0
    dt = np.maximum(th - tc, 5.0)
    return np.clip(eta_c * th / dt, 1.0, 7.0)


def eta_carnot_desde_cop_nominal(cop_nom, t_aire_nom, t_ac_nom):
    """Calibra η_C para que COP(t_aire_nom, t_ac_nom) = cop_nom (condiciones de ensayo EN 16147)."""
    return cop_nom * (t_ac_nom - t_aire_nom) / (t_ac_nom + K0)


def perdidas_espera_kwh_dia(volumen_l, ua_ref_kwh_24h_100l):
    """Pérdidas en espera (kWh/día) escaladas con el volumen^(2/3) (superficie del depósito)."""
    return ua_ref_kwh_24h_100l * (np.asarray(volumen_l, float) / 100.0) ** (2.0 / 3.0)


def demanda_ref_cte_l_dia(n_pers):
    """Demanda de referencia CTE DB-HE 4 a 60 ºC (L/día) para contraste."""
    return ref().get("acs.demanda_referencia_l_persona_dia_60c") * n_pers


def v60_equivalente(v_uso, t_uso, t_red_anual, t_ref):
    """Volumen equivalente a T_ref: V·(T_uso − T_red)/(T_ref − T_red)."""
    return v_uso * (t_uso - t_red_anual) / (t_ref - t_red_anual)
