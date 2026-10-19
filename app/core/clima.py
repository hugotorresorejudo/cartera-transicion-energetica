"""Código postal -> provincia -> zona CTE; PVGIS normalizado; T2m TMY; temperatura de agua de red."""
from __future__ import annotations

import unicodedata

import numpy as np

from . import datos
from .referencias import ref

TILTS = np.array([0, 15, 30, 45], dtype=float)
AZIMS = np.array([-90, -45, 0, 45, 90], dtype=float)
ESCALA_PV = 1e-4
ESCALA_T = 0.1


def provincia(cp) -> dict:
    """Provincia a partir de los dos primeros dígitos del CP (código INE)."""
    s = str(cp).strip().zfill(5)
    cod = s[:2]
    df = datos.provincias()
    fila = df[df["codigo"] == cod]
    if len(s) != 5 or not s.isdigit() or fila.empty:
        raise ValueError(f"Código postal no válido: {cp}")
    return fila.iloc[0].to_dict()


def zona_cte(cp) -> str:
    return provincia(cp)["zona_cte"]


def pv_normalizado(cp, azimut: float, inclinacion: float) -> np.ndarray:
    """Producción horaria típica (kWh por kWp y hora, 8760 valores) por interpolación bilineal en la rejilla PVGIS.

    azimut: convención PVGIS (0 = sur, -90 = este, 90 = oeste). |azimut| > 90 se extrapola con el factor norte."""
    d = datos.pvgis(provincia(cp)["codigo"])
    y = d["y"].astype(np.float32) * ESCALA_PV  # (tilt, az, h)
    az = float(np.clip(azimut, -90, 90))
    t = float(np.clip(inclinacion, TILTS[0], TILTS[-1]))
    i = int(min(np.searchsorted(TILTS, t, side="right") - 1, len(TILTS) - 2))
    j = int(min(np.searchsorted(AZIMS, az, side="right") - 1, len(AZIMS) - 2))
    wt = (t - TILTS[i]) / (TILTS[i + 1] - TILTS[i])
    wa = (az - AZIMS[j]) / (AZIMS[j + 1] - AZIMS[j])
    v = ((1 - wt) * (1 - wa) * y[i, j] + (1 - wt) * wa * y[i, j + 1]
         + wt * (1 - wa) * y[i + 1, j] + wt * wa * y[i + 1, j + 1])
    if abs(azimut) > 90:
        f = ref().rango("fv.factor_orientacion_norte")[1]
        v = v * (1 - (min(abs(azimut), 180) - 90) / 90 * (1 - f))
    return v.astype(np.float32)


def factores_anuales_pv(cp) -> np.ndarray:
    """Factor mensual por año meteorológico (n_años, 12) respecto del año típico."""
    return datos.pvgis(provincia(cp)["codigo"])["fy"].astype(np.float32)


def t2m(cp) -> np.ndarray:
    return datos.pvgis(provincia(cp)["codigo"])["t2m"].astype(np.float32) * ESCALA_T


def _norm(x: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", x.lower()) if unicodedata.category(c) != "Mn")


def t_red_mensual(cp) -> np.ndarray:
    """Temperatura del agua de red por mes (12) de la capital de provincia (CTE DB-HE 4).

    Si la capital no figura en la tabla se usa la de la capital tabulada de temperatura media anual más próxima."""
    mapa = ref().get("acs.t_red_mensual_capitales")
    nombre = _norm(provincia(cp)["nombre"])
    for k, v in mapa.items():
        if _norm(k) in nombre or nombre in _norm(k):
            return np.asarray(v, dtype=float)
    tm = float(np.mean(t2m(cp)))
    mejor = min(mapa.values(), key=lambda v: abs(np.mean(v) - (tm - 2.0)))
    return np.asarray(mejor, dtype=float)
