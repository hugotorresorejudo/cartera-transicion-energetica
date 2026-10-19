"""Motor fotovoltaico común: producción horaria PVGIS, balance neto horario y compensación mensual de excedentes."""
from __future__ import annotations

import numpy as np

from . import clima
from .calendario import calendario_tipico
from .termico import DIAS_MES

_MES = None
_INI_MES = None


def dist_azimut(orientacion: str) -> dict:
    """Distribución del azimut (convención PVGIS) para la respuesta de orientación."""
    from .referencias import ref
    return dict(ref().sub("fv.azimut_orientacion", orientacion))


def mes_hora() -> np.ndarray:
    global _MES
    if _MES is None:
        _MES = calendario_tipico()["mes"]
    return _MES


def inicios_mes() -> np.ndarray:
    return np.concatenate([[0], np.cumsum(DIAS_MES * 24)[:-1]])


def suma_mensual(x: np.ndarray) -> np.ndarray:
    """(n, 8760) -> (n, 12)."""
    return np.add.reduceat(x, inicios_mes(), axis=-1)


def generacion_unitaria(cp, az, tilt, rng, paso_az=15.0, paso_incl=5.0) -> np.ndarray:
    """(n, 8760) kWh por kWp y hora para n pares (azimut, inclinación) muestreados, multiplicada por el factor
    mensual de un año meteorológico elegido al azar entre los años PVGIS disponibles."""
    az, tilt = np.atleast_1d(az).astype(float), np.atleast_1d(tilt).astype(float)
    n = az.size
    qa = np.round(az / paso_az) * paso_az
    qt = np.round(tilt / paso_incl) * paso_incl
    pares, inv = np.unique(np.stack([qa, qt], axis=1), axis=0, return_inverse=True)
    Y = np.stack([clima.pv_normalizado(cp, a, t) for a, t in pares])
    fy = clima.factores_anuales_pv(cp)
    anio = rng.integers(0, fy.shape[0], n)
    f = fy[anio][:, mes_hora()]  # (n, 8760)
    return (Y[inv.ravel()] * f).astype(np.float32)


def balance(G: np.ndarray, E: np.ndarray):
    """S = min(G,E), X = G−S (excedente), I = E−S (importación)."""
    S = np.minimum(G, E)
    return S, G - S, E - S


def compensacion(X, I, p_exc, p_energia) -> np.ndarray:
    """Compensación simplificada mensual (€ por muestra): min(Σ X·p_exc, Σ I·p_energía) por mes (RD 244/2019)."""
    ing = suma_mensual(X * p_exc)
    tope = suma_mensual(I * p_energia)
    return np.minimum(ing, tope).sum(axis=-1)


def indicadores(S, G, E):
    """Autoconsumo SC = ΣS/ΣG y autosuficiencia SS = ΣS/ΣE."""
    s = S.sum(axis=-1, dtype=np.float64)
    return s / np.maximum(G.sum(axis=-1, dtype=np.float64), 1e-9), s / np.maximum(E.sum(axis=-1, dtype=np.float64), 1e-9)
