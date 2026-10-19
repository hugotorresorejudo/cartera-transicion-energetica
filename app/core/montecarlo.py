"""Muestreo de distribuciones, percentiles y tornado (Monte Carlo vectorizado con numpy)."""
from __future__ import annotations

import numpy as np

SEMILLA = 42


def fijo(v):
    return {"t": "fijo", "v": float(v)}


def tri(mn, moda, mx):
    return {"t": "tri", "min": float(mn), "moda": float(moda), "max": float(mx)}


def unif(mn, mx):
    return {"t": "unif", "min": float(mn), "max": float(mx)}


def norm(mu, sd, mn=None, mx=None):
    return {"t": "norm", "mu": float(mu), "sd": float(sd), "min": mn, "max": mx}


def logn(mediana, sg):
    """Lognormal con mediana y desviación geométrica sg (>1)."""
    return {"t": "logn", "mediana": float(mediana), "sg": float(sg)}


def disc(vals, p=None):
    """Distribución discreta (p uniforme si no se indica)."""
    vals = [float(v) for v in vals]
    p = [1.0 / len(vals)] * len(vals) if p is None else [float(x) for x in p]
    return {"t": "disc", "vals": vals, "p": p}


def desde_rango(r):
    """Rango (min, moda, max) -> triangular, o fijo si es degenerado."""
    mn, mo, mx = r
    return fijo(mo) if mn == mx else tri(mn, mo, mx)


def muestrear(d, n, rng):
    t = d["t"]
    if t == "fijo":
        return np.full(n, d["v"])
    if t == "tri":
        if d["max"] == d["min"]:
            return np.full(n, d["min"])
        return rng.triangular(d["min"], np.clip(d["moda"], d["min"], d["max"]), d["max"], n)
    if t == "unif":
        return rng.uniform(d["min"], d["max"], n)
    if t == "norm":
        x = rng.normal(d["mu"], d["sd"], n)
        if d.get("min") is not None or d.get("max") is not None:
            x = np.clip(x, d.get("min"), d.get("max"))
        return x
    if t == "logn":
        return d["mediana"] * rng.lognormal(0.0, np.log(d["sg"]), n)
    if t == "disc":
        return rng.choice(d["vals"], size=n, p=d["p"])
    raise ValueError(f"distribución desconocida: {t}")


def central(d):
    """Valor central (moda/mediana) de una distribución."""
    t = d["t"]
    return {"fijo": lambda: d["v"], "tri": lambda: d["moda"], "unif": lambda: 0.5 * (d["min"] + d["max"]),
            "norm": lambda: d["mu"], "logn": lambda: d["mediana"],
            "disc": lambda: d["vals"][int(np.argmax(d["p"]))]}[t]()


def cuantil(d, q, n=2001, semilla=SEMILLA):
    return float(np.quantile(muestrear(d, n, np.random.default_rng(semilla)), q))


def p10_50_90(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return (np.nan, np.nan, np.nan)
    a, b, c = np.percentile(x, [10, 50, 90])
    return float(a), float(b), float(c)


def prob(x, cond=lambda v: v > 0):
    x = np.asarray(x, dtype=float)
    return float(np.mean(cond(x)))


def muestras(dists: dict, n: int, seed: int = SEMILLA, rng=None):
    rng = rng or np.random.default_rng(seed)
    return {k: muestrear(d, n, rng) for k, d in dists.items()}


def tornado(modelo, dists: dict, salida: str, seed: int = SEMILLA, n_ref: int = 2001):
    """Sensibilidad una-a-una: cada parámetro en P10/P90 con el resto en su mediana.

    modelo(S) -> dict de arrays; S es dict nombre->array(1,). Devuelve lista ordenada por rango."""
    med = {k: np.array([cuantil(d, 0.5, n_ref, seed)]) for k, d in dists.items()}
    base = float(np.asarray(modelo(med)[salida]).ravel()[0])
    filas = []
    for k, d in dists.items():
        if d["t"] == "fijo":
            continue
        lo, hi = cuantil(d, 0.1, n_ref, seed), cuantil(d, 0.9, n_ref, seed)
        res = []
        for v in (lo, hi):
            s = dict(med)
            s[k] = np.array([v])
            res.append(float(np.asarray(modelo(s)[salida]).ravel()[0]))
        filas.append({"parametro": k, "bajo": res[0], "alto": res[1], "x_bajo": lo, "x_alto": hi, "base": base})
    filas.sort(key=lambda f: -abs(f["alto"] - f["bajo"]))
    return filas
