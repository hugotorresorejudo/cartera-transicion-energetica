"""Carga óptima de un almacenamiento/VE: programa lineal min Σ p_t·x_t, y su solución voraz vectorizada equivalente."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog


def plan_lp(precios, disponible, p_max_kw, energia_kwh, dt: float = 1.0):
    """Resuelve con HiGHS (scipy.optimize.linprog): min Σ p_t x_t s.a. Σ x_t = E, 0 ≤ x_t ≤ P·Δt·a_t.

    Devuelve (x (T,), coste) o (None, nan) si es infactible."""
    p = np.asarray(precios, float)
    a = np.asarray(disponible, float)
    res = linprog(c=p, A_eq=np.ones((1, p.size)), b_eq=[energia_kwh], bounds=[(0.0, p_max_kw * dt * ai) for ai in a],
                  method="highs")
    if not res.success:
        return None, float("nan")
    return res.x, float(res.fun)


def coste_voraz(precios_ventana, p_max_kw, energia_kwh, dt: float = 1.0, ordenar: bool = True):
    """Coste mínimo (o en orden temporal si ordenar=False) de cargar `energia_kwh` en las horas de la ventana.

    precios_ventana: (..., k) €/kWh de las horas disponibles; energia_kwh: escalar o broadcast a (...,).
    Es la solución exacta del LP anterior (el óptimo llena las horas más baratas hasta la potencia máxima).
    Devuelve (coste (...,), energia_no_cubierta (...,))."""
    P = np.sort(precios_ventana, axis=-1) if ordenar else np.asarray(precios_ventana)
    k = P.shape[-1]
    q = np.asarray(energia_kwh, float) / (p_max_kw * dt)  # horas equivalentes a plena potencia
    q = np.broadcast_to(q, P.shape[:-1]) if np.ndim(q) else np.full(P.shape[:-1], float(q))
    w = np.clip(q[..., None] - np.arange(k), 0.0, 1.0)  # fracción de cada hora que se usa
    coste = (w * P).sum(-1) * p_max_kw * dt
    no_cubierta = np.maximum(q - k, 0.0) * p_max_kw * dt
    return coste, no_cubierta, w


def ventana_horas(llegada: int, salida: int) -> np.ndarray:
    """Horas (0..47 sobre dos días) disponibles desde la llegada hasta la salida del día siguiente."""
    fin = 24 + salida if salida <= llegada else salida
    return np.arange(llegada, fin)
