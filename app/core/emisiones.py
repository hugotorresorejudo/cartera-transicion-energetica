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


def serie_ef_8760() -> np.ndarray:
    """(8760,) kgCO₂/kWh horario del último año de REData (promedio por mes-día-hora), o la constante media si no hay datos."""
    import pandas as pd
    from .calendario import calendario_tipico
    try:
        df = datos.redata()
        e = [c for c in df.columns if "tco2" in c.lower()]
        d = [c for c in df.columns if "demanda" in c.lower()]
        if not e or not d:
            raise FileNotFoundError
        t = pd.to_datetime(df["ts"])
        ef = (df[e[0]].astype(float) / df[d[0]].astype(float)).replace([np.inf, -np.inf], np.nan)
        clave = t.dt.month.astype(int) * 10000 + t.dt.day.astype(int) * 100 + t.dt.hour.astype(int)
        tab = ef.groupby(clave).mean()
        cal = calendario_tipico()
        mes, hora = cal["mes"] + 1, cal["hora"]
        dia = np.tile(np.repeat(np.arange(365), 1), 1)
        dias_mes = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        dom = cal["dia_anio"] - dias_mes[cal["mes"]] + 1
        k = mes * 10000 + dom * 100 + hora
        out = tab.reindex(k).to_numpy(dtype=float)
        if np.isnan(out).all():
            raise FileNotFoundError
        return pd.Series(out).ffill().bfill().to_numpy()
    except FileNotFoundError:
        return np.full(8760, ref().rango("emisiones.factor_electricidad_mix_medio")[1])


def mix_por_hora():
    """({tecnología: (24,)} generación media por hora del día, orden) a partir de las columnas de generación de REData, o None."""
    try:
        df = datos.redata()
    except FileNotFoundError:
        return None
    cols = [c for c in df.columns if c.startswith("g_")]
    if not cols:
        return None
    import pandas as pd
    h = pd.to_datetime(df["ts"]).dt.hour
    tab = df[cols].astype(float).groupby(h).mean()
    return {c[2:]: tab[c].to_numpy() for c in cols}
