"""Motor de precios y factura 2.0TD: PVPC, precio fijo, indexado; escenarios de precio por block bootstrap."""
from __future__ import annotations

import numpy as np

from . import datos
from .calendario import ANIO_TIPO, calendario
from .referencias import ref

SEMANA = 168


def anio_precios() -> int:
    """Año de aplicación de la ponderación de futuros del PVPC (año de los datos, acotado a la tabla)."""
    anios = [int(k) for k in ref().get("tarifa.pvpc_peso_futuros")]
    fecha = datos.meta().get("actualizado") or ""
    a = int(fecha[:4]) if fecha[:4].isdigit() else max(anios)
    return min(max(a, min(anios)), max(anios))


def periodos() -> np.ndarray:
    """Periodo 2.0TD (0=P1, 1=P2, 2=P3) de cada hora del año tipo."""
    return calendario(ANIO_TIPO)["periodo"]


def peajes_cargos_energia() -> np.ndarray:
    """(3,) €/kWh: peaje + cargo de energía de P1, P2 y P3."""
    r = ref()
    return np.array([r.get(f"tarifa.peaje_energia_p{i}") + r.get(f"tarifa.cargo_energia_p{i}") for i in (1, 2, 3)])


def potencia_regulada() -> np.ndarray:
    """(2,) €/kW·año: peaje + cargo de potencia en P1 y P2."""
    r = ref()
    return np.array([r.get(f"tarifa.peaje_potencia_p{i}") + r.get(f"tarifa.cargo_potencia_p{i}") for i in (1, 2)])


def _mod(rango_clave: str, valor):
    return ref().rango(rango_clave)[1] if valor is None else valor


def precio_pvpc(omie, per=None, anio=None, c_aj=None, perdidas=None) -> np.ndarray:
    """Término de energía del PVPC (€/kWh) con la mezcla spot/futuros de RD 446/2023.

    p_t = [(1-w)·OMIE_t + w·F + c_aj]·(1+λ)/1000 + π_k(t).  F se aproxima por la media anual del escenario de OMIE."""
    per = periodos() if per is None else per
    w = ref().sub("tarifa.pvpc_peso_futuros", anio or anio_precios())
    om = np.asarray(omie, dtype=np.float32)
    fut = om.mean(axis=-1, keepdims=True)
    mezcla = (1.0 - w) * om + w * fut
    c = _mod("tarifa.indexada_servicios_ajuste", c_aj)
    lam = _mod("tarifa.indexada_perdidas", perdidas)
    return ((mezcla + c) * (1.0 + lam) / 1000.0 + peajes_cargos_energia()[per]).astype(np.float32)


def precio_indexado(omie, per=None, margen=None, c_aj=None, perdidas=None) -> np.ndarray:
    """p_t = (OMIE_t + c_aj)(1+λ)/1000 + μ/1000 + π_k(t)  (€/kWh)."""
    per = periodos() if per is None else per
    om = np.asarray(omie, dtype=np.float32)
    c = _mod("tarifa.indexada_servicios_ajuste", c_aj)
    lam = _mod("tarifa.indexada_perdidas", perdidas)
    mu = _mod("tarifa.indexada_margen", margen)
    return ((om + c) * (1.0 + lam) / 1000.0 + mu / 1000.0 + peajes_cargos_energia()[per]).astype(np.float32)


def precio_fijo(precio=None, por_periodos=False, per=None) -> np.ndarray:
    """Precio fijo (€/kWh) de 8760 valores, con `precio` escalar o (n,) -> (8760,) o (n, 8760).

    Con `por_periodos` aplica la relación entre periodos de las ofertas con discriminación, normalizada para
    que el precio medio ponderado por horas coincida con el precio único."""
    per = periodos() if per is None else per
    p = np.asarray(_mod("tarifa.oferta_fija_energia_tipica", precio), dtype=np.float32)
    if not por_periodos:
        return (p[..., None] * np.ones(per.shape, np.float32)).astype(np.float32)
    r = ref().get("tarifa.ratio_periodos_fija")
    rel = np.array([r["P1"], r["P2"], r["P3"]])
    norm = float(np.sum(np.bincount(per, minlength=3) / per.size * rel))
    return (p[..., None] * (rel[per] / norm)).astype(np.float32)


def potencia_precios(modalidad: str, precio_dia: float | None = None):
    """(2,) €/kW·año de P1 y P2. PVPC: regulado + margen de comercialización; fija: €/kW·día × 365; indexada: regulado + margen."""
    reg = potencia_regulada()
    if modalidad == "pvpc":
        return reg + np.array([ref().get("tarifa.pvpc_margen_comercializacion"), 0.0])
    if modalidad == "fija":
        p = _mod("tarifa.oferta_fija_potencia_tipica", precio_dia) * ref().get("tarifa.dias_anio")
        return np.array([p, p * reg[1] / reg[0]])
    return reg


def factura(E, p_e, P1, P2, pot_precios, bono: float = 0.0, credito=0.0) -> dict:
    """Factura anual 2.0TD. E: (n,8760) kWh; p_e: (n,8760) o (8760,) €/kWh; P1, P2: kW (escalar o (n,)).

    Devuelve CE, CP, IEE, contador, total (con IVA) y energía total, cada uno de forma (n,)."""
    r = ref()
    E = np.asarray(E, dtype=np.float32)
    ce = np.sum(E * p_e, axis=-1, dtype=np.float64)
    cp = np.asarray(P1) * pot_precios[0] + np.asarray(P2) * pot_precios[1]
    cp = np.broadcast_to(cp, ce.shape).astype(np.float64)
    e_tot = E.sum(axis=-1, dtype=np.float64)
    ce = np.maximum(ce - credito, 0.0)  # compensación de excedentes (nunca por encima del término de energía)
    bono = np.asarray(bono, dtype=np.float64)
    ce, cp = ce * (1 - bono), cp * (1 - bono)
    iee = np.maximum(r.get("tarifa.iee_tipo") / 100.0 * (ce + cp), r.get("tarifa.iee_minimo_domestico") * e_tot)
    cont = r.get("tarifa.alquiler_contador") * 12
    total = (ce + cp + iee + cont) * (1.0 + r.get("tarifa.iva_electricidad") / 100.0)
    return {"CE": ce, "CP": cp, "IEE": iee, "contador": np.full(ce.shape, cont), "total": total, "E": e_tot}


def invertir_factura(importe_mes, P_kw, p_medio_kwh, pot_precios):
    """Energía anual E_a (kWh) tal que C_tot(E_a) = 12·importe, con precio medio de energía conocido."""
    r = ref()
    anual = np.asarray(importe_mes) * 12.0 / (1.0 + r.get("tarifa.iva_electricidad") / 100.0)
    sin_cont = (anual - r.get("tarifa.alquiler_contador") * 12) / (1.0 + r.get("tarifa.iee_tipo") / 100.0)
    cp = P_kw * (pot_precios[0] + pot_precios[1])
    return np.maximum((sin_cont - cp) / p_medio_kwh, 1.0)


def escenarios_omie(n: int, rng, zona: str = "es") -> np.ndarray:
    """(n, 8760) €/MWh: block bootstrap semanal de los años completos disponibles."""
    _, M = datos.omie_matriz(zona)
    k = M.shape[0]
    out = np.empty((n, M.shape[1]), dtype=np.float32)
    bloques = list(range(0, M.shape[1], SEMANA))
    elegido = rng.integers(0, k, size=(n, len(bloques)))
    for j, ini in enumerate(bloques):
        sl = slice(ini, min(ini + SEMANA, M.shape[1]))
        out[:, sl] = M[elegido[:, j], sl]
    return out


def pvpc_observado():
    """Serie PVPC horaria real del último año (€/kWh) si existe en REData, o None."""
    try:
        df = datos.redata()
    except FileNotFoundError:
        return None
    cols = [c for c in df.columns if "PVPC" in c.upper()]
    if not cols:
        return None
    return df[["ts", cols[0]]].rename(columns={cols[0]: "pvpc"})
