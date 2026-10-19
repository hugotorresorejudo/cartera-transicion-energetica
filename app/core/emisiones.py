"""Intensidad de emisiones de la electricidad por mes y hora (REData) y factores de combustibles."""
from __future__ import annotations

import numpy as np

from . import datos
from .referencias import ref


def ef_mes_hora() -> np.ndarray:
    """(12, 24) kgCO₂/kWh: emisiones medias del sistema por mes y hora (REData); si no hay datos, factor medio constante."""
    try:
        e = datos.redata_perfil_mes_hora("tCO2")
        d = datos.redata_perfil_mes_hora("demanda")
    except FileNotFoundError:
        e = d = None
    if e is None or d is None or not np.all(d > 0):
        return np.full((12, 24), ref().rango("emisiones.factor_electricidad_mix_medio")[1])
    return e / d  # tCO₂/MWh = kgCO₂/kWh


def ef_anual_8760() -> np.ndarray:
    """(8760,) kgCO₂/kWh por hora del año tipo."""
    from .calendario import calendario_tipico
    c = calendario_tipico()
    return ef_mes_hora()[c["mes"], c["hora"]]
