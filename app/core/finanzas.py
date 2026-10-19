"""Matemática financiera común: VAN, TIR, payback, CRF y flujos con degradación e inflación."""
from __future__ import annotations

import numpy as np


def factor_descuento(r, n):
    return (1.0 + np.asarray(r, dtype=float)) ** (-np.asarray(n, dtype=float))


def van(flujos, r):
    """VAN de flujos (..., N+1) con el flujo 0 al inicio. r escalar o broadcastable a (...)."""
    f = np.asarray(flujos, dtype=float)
    n = np.arange(f.shape[-1])
    r = np.asarray(r, dtype=float)
    d = (1.0 + r[..., None]) ** (-n) if r.ndim else (1.0 + r) ** (-n)
    return np.sum(f * d, axis=-1)


def tir(flujos, lo=-0.9, hi=1.0, it=60):
    """TIR por bisección vectorizada; NaN si no hay cambio de signo en [lo, hi]."""
    f = np.atleast_2d(np.asarray(flujos, dtype=float))
    a = np.full(f.shape[0], lo)
    b = np.full(f.shape[0], hi)
    fa, fb = van(f, a), van(f, b)
    ok = fa * fb < 0
    for _ in range(it):
        m = 0.5 * (a + b)
        fm = van(f, m)
        izq = fa * fm <= 0
        b = np.where(izq, m, b)
        a = np.where(izq, a, m)
        fa = np.where(izq, fa, fm)
    out = np.where(ok, 0.5 * (a + b), np.nan)
    return out if np.asarray(flujos).ndim > 1 else out[0]


def payback(flujos):
    """Año (interpolado) en que el flujo acumulado pasa a ser >= 0; NaN si no se recupera."""
    f = np.atleast_2d(np.asarray(flujos, dtype=float))
    acum = np.cumsum(f, axis=-1)
    out = np.full(f.shape[0], np.nan)
    for i in range(f.shape[0]):
        k = np.nonzero(acum[i] >= 0)[0]
        if k.size and k[0] > 0:
            j = k[0]
            out[i] = (j - 1) + (-acum[i, j - 1]) / f[i, j]
        elif k.size:
            out[i] = 0.0
    return out if np.asarray(flujos).ndim > 1 else out[0]


def crf(r, n):
    """Factor de recuperación de capital."""
    r = np.asarray(r, dtype=float)
    n = np.asarray(n, dtype=float)
    pequeno = np.abs(r) < np.finfo(float).eps
    r_s = np.where(pequeno, 1.0, r)
    return np.where(pequeno, 1.0 / n, r_s * (1 + r_s) ** n / ((1 + r_s) ** n - 1))


def serie_anual(base, n_anios, inflacion=0.0, degradacion=0.0):
    """base * (1+inflacion)^(n-1) * (1-degradacion)^(n-1) para n=1..N; base escalar o (m,)."""
    n = np.arange(n_anios)
    b = np.asarray(base, dtype=float)[..., None]
    infl = np.asarray(inflacion, dtype=float)
    deg = np.asarray(degradacion, dtype=float)
    infl = infl[..., None] if infl.ndim else infl
    deg = deg[..., None] if deg.ndim else deg
    return b * ((1 + infl) ** n) * ((1 - deg) ** n)


def flujos_proyecto(capex, ahorros, opex=0.0, extras=None):
    """Compone [-capex, a1-opex1+e1, ...]. ahorros: (..., N); extras: (..., N) opcional (p. ej. reposiciones)."""
    a = np.asarray(ahorros, dtype=float)
    o = np.asarray(opex, dtype=float)
    o = o[..., None] if o.ndim else o
    cf = a - o
    if extras is not None:
        cf = cf + np.asarray(extras, dtype=float)
    c0 = -np.asarray(capex, dtype=float)[..., None] if np.ndim(capex) else -float(capex)
    c0 = np.broadcast_to(c0, cf.shape[:-1] + (1,))
    return np.concatenate([c0, cf], axis=-1)


def lcoe(capex, opex_anual, energia_anual, r, n, degradacion=0.0):
    """LCOE = (CAPEX + sum OPEX/(1+r)^t) / sum E_t/(1+r)^t."""
    t = np.arange(1, int(n) + 1)
    d = (1 + r) ** (-t)
    e = energia_anual * (1 - degradacion) ** (t - 1)
    return (capex + np.sum(opex_anual * d)) / np.sum(e * d)
