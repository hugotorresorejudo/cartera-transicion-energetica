"""Acceso a los ficheros estáticos de app/data/ (generados por scripts/fetch_data.py)."""
from __future__ import annotations

import io
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parent.parent / "data"
HORAS_ANIO = 8760


@lru_cache(maxsize=None)
def meta() -> dict:
    p = DIR / "meta.json"
    if not p.exists():
        return {"actualizado": None, "sintetico": True, "fuentes": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def es_sintetico() -> bool:
    return bool(meta().get("sintetico", True))


def fecha_datos() -> str:
    return meta().get("actualizado") or "sin datos"


@lru_cache(maxsize=None)
def provincias() -> pd.DataFrame:
    return pd.read_csv(DIR / "provincias.csv", dtype={"codigo": str})


@lru_cache(maxsize=None)
def _omie_df() -> pd.DataFrame:
    return pd.read_csv(DIR / "omie_es_horario.csv.gz", parse_dates=["fecha"])


def _a_8760(df_anio: pd.DataFrame, col: str) -> np.ndarray:
    """Convierte filas (fecha, h=1..25) a 24 h/día, sin 29-feb: promedia la hora repetida y duplica la que falta."""
    out = []
    for fecha, g in df_anio.groupby("fecha", sort=True):
        if fecha.month == 2 and fecha.day == 29:
            continue
        v = g.sort_values("h")[col].to_numpy(dtype=float)
        if v.size == 25:
            v = np.concatenate([v[:2], [0.5 * (v[2] + v[3])], v[4:]])  # hora duplicada del cambio de hora de octubre
        elif v.size == 23:
            v = np.concatenate([v[:2], [v[2]], v[2:]])
        elif v.size != 24:
            v = np.resize(v, 24)
        out.append(v)
    return np.concatenate(out)


def omie_anios() -> list[int]:
    return sorted(int(a) for a in _omie_df()["fecha"].dt.year.unique())


def anios_completos() -> list[int]:
    df = _omie_df()
    cuenta = df.groupby(df["fecha"].dt.year)["fecha"].nunique()
    return [int(a) for a, c in cuenta.items() if c >= 364]


@lru_cache(maxsize=None)
def omie_anual(anio: int, zona: str = "es") -> np.ndarray:
    """Precio marginal del mercado diario (€/MWh), 8760 valores."""
    df = _omie_df()
    return _a_8760(df[df["fecha"].dt.year == anio], zona)


def omie_matriz(zona: str = "es") -> tuple[list[int], np.ndarray]:
    ys = anios_completos()
    return ys, np.stack([omie_anual(y, zona)[:HORAS_ANIO] for y in ys])


@lru_cache(maxsize=None)
def redata() -> pd.DataFrame:
    df = pd.read_csv(DIR / "redata_horario.csv.gz", parse_dates=["ts"])
    return df


@lru_cache(maxsize=None)
def omie_percentiles() -> dict:
    return json.loads((DIR / "omie_percentiles.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def curvas_omie() -> dict:
    return json.loads((DIR / "curvas_omie.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def pvgis(cod: str):
    npz = np.load(DIR / "pvgis" / f"pv_{cod}.npz")
    return {k: npz[k] for k in npz.files}


def leer_csv_texto(txt: str, **kw) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(txt), **kw)


def _dia24(v: np.ndarray) -> np.ndarray:
    if v.size == 25:
        return np.concatenate([v[:2], [0.5 * (v[2] + v[3])], v[4:]])
    if v.size == 23:
        return np.concatenate([v[:3], v[2:]])
    return v if v.size == 24 else np.resize(v, 24)


@lru_cache(maxsize=None)
def omie_dias(zona: str = "es"):
    """(fechas datetime64[D] (nd,), precios (nd, 24) en €/MWh) de toda la serie, con 29-feb."""
    df = _omie_df().sort_values(["fecha", "h"])
    fechas, filas = [], []
    for f, g in df.groupby("fecha", sort=True):
        fechas.append(f)
        filas.append(_dia24(g[zona].to_numpy(dtype=float)))
    return np.array(fechas, dtype="datetime64[D]"), np.stack(filas)


@lru_cache(maxsize=None)
def redata_perfil_mes_hora(contiene: str):
    """Media por (mes, hora) de la primera columna de REData cuyo nombre contiene `contiene` -> (12, 24) o None."""
    df = redata()
    cols = [c for c in df.columns if contiene.lower() in c.lower()]
    if not cols:
        return None
    s = df[cols[0]].astype(float)
    t = pd.to_datetime(df["ts"])
    tabla = s.groupby([t.dt.month - 1, t.dt.hour]).mean().unstack()
    return tabla.reindex(index=range(12), columns=range(24)).ffill().fillna(0.0).to_numpy()
