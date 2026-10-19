"""Despacho horario de una batería doméstica: prioriza el autoconsumo (carga con excedentes, descarga para cubrir la demanda)."""
from __future__ import annotations

import numpy as np


def despacho(G, E, cap_kwh, p_kw, eta_rt, dod=1.0):
    """Simula la batería hora a hora para n muestras en paralelo.

    G, E: (n, T) kWh generados y consumidos; cap_kwh, p_kw, eta_rt: escalares o (n,). La energía útil es cap·dod y la
    eficiencia de ida y vuelta se reparte a partes iguales entre carga y descarga.
    Devuelve (S_total, X, I, ciclos): autoconsumo directo + descarga (n,T), excedente (n,T), importación (n,T) y ciclos
    equivalentes por año (n,)."""
    G = np.asarray(G, dtype=np.float32)
    E = np.asarray(E, dtype=np.float32)
    n, T = G.shape
    util = np.broadcast_to(np.asarray(cap_kwh, dtype=np.float32) * np.float32(dod), (n,)).copy()
    pmax = np.broadcast_to(np.asarray(p_kw, dtype=np.float32), (n,)).copy()
    eta = np.sqrt(np.broadcast_to(np.asarray(eta_rt, dtype=np.float32), (n,)))
    Gt, Et = np.ascontiguousarray(G.T), np.ascontiguousarray(E.T)
    soc = np.zeros(n, dtype=np.float32)
    X = np.empty_like(Gt)
    I = np.empty_like(Gt)
    Sdir = np.minimum(Gt, Et)
    energia_cargada = np.zeros(n, dtype=np.float32)
    for t in range(T):
        sobra = Gt[t] - Sdir[t]
        falta = Et[t] - Sdir[t]
        carga = np.minimum(np.minimum(sobra, pmax), (util - soc) / eta)
        soc = soc + carga * eta
        energia_cargada += carga
        desc = np.minimum(np.minimum(falta, pmax), soc * eta)
        soc = soc - desc / eta
        X[t] = sobra - carga
        I[t] = falta - desc
    S_total = Et - I
    ciclos = energia_cargada * eta / np.maximum(util, 1e-9)
    return S_total.T, X.T, I.T, ciclos
