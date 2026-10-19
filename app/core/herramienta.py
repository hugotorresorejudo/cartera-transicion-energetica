"""Tipos y ejecutor comunes de todas las herramientas (sin dependencia de Shiny)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable

import numpy as np

from . import datos, montecarlo as mc
from .referencias import ref


@dataclass
class Pregunta:
    id: str
    texto: str
    tipo: str  # select | multi | numero | texto | archivo
    opciones: list = field(default_factory=list)  # [(valor, etiqueta)]
    defecto: Any = None
    perfil: str | None = None  # campo del perfil del que hereda su valor por defecto
    ayuda: str = ""


@dataclass
class Param:
    id: str
    etiqueta: str
    unidad: str
    dist: dict
    origen: str = "inferido"  # inferido | editado
    fuente: str = ""

    @property
    def central(self) -> float:
        return mc.central(self.dist)


@dataclass
class Parametros:
    params: dict
    ctx: dict = field(default_factory=dict)

    def dists(self) -> dict:
        return {k: p.dist for k, p in self.params.items()}

    def editar(self, k: str, valor: float):
        p = self.params[k]
        p.dist = mc.fijo(valor)
        p.origen = "editado"

    def editados(self) -> dict:
        return {k: p.dist["v"] for k, p in self.params.items() if p.origen == "editado"}

    def to_dict(self) -> dict:
        return {"params": {k: asdict(p) for k, p in self.params.items()}, "ctx": self.ctx}


@dataclass
class KPI:
    id: str
    nombre: str
    unidad: str
    p10: float
    p50: float
    p90: float
    tipo: str = "neutro"  # ahorro | coste | neutro
    fmt: str = "{:,.0f}"
    prob: float | None = None
    prob_texto: str = ""


@dataclass
class Resultados:
    herramienta: str
    kpis: list
    graficos: list = field(default_factory=list)
    tornado: list = field(default_factory=list)
    tabla: list = field(default_factory=list)
    notas: list = field(default_factory=list)
    refs_pendientes: list = field(default_factory=list)
    sintetico: bool = False
    n_mc: int = 0
    semilla: int = 0
    extra: dict = field(default_factory=dict)

    def kpi(self, id_: str) -> KPI:
        return next(k for k in self.kpis if k.id == id_)

    def to_dict(self) -> dict:
        return asdict(self)


def _a_lista(x):
    return np.asarray(x).tolist()


def ejecutar(herr_id: str, parametros: Parametros, modelo: Callable, kpis: list, n_mc: int = 500, seed: int = mc.SEMILLA,
             tornado_kpi: str | None = None, graficos: Callable | None = None, tabla: Callable | None = None,
             notas: Callable | None = None) -> Resultados:
    """Ejecuta Monte Carlo vectorizado.

    modelo(S, ctx, rng) -> dict nombre -> ndarray (n,) o (n, m).
    kpis: lista de dicts {id, nombre, unidad, clave, tipo, fmt, prob: (texto, cond)}.
    graficos(out, ctx) -> lista de especificaciones; tabla(out, ctx) -> lista de filas; notas(out, ctx) -> lista de textos."""
    with ref().rastrear() as usadas:
        rng = np.random.default_rng(seed)
        S = mc.muestras(parametros.dists(), n_mc, rng=rng)
        out = modelo(S, parametros.ctx, rng)
        lista = []
        for d in kpis:
            x = np.asarray(out[d["clave"]], dtype=float)
            a, b, c = mc.p10_50_90(x, d.get("inf_ok", False))
            k = KPI(d["id"], d["nombre"], d["unidad"], a, b, c, d.get("tipo", "neutro"), d.get("fmt", "{:,.0f}"))
            if d.get("prob"):
                k.prob_texto, cond = d["prob"]
                k.prob = mc.prob(x, cond)
            lista.append(k)
        torn = []
        if tornado_kpi:
            clave = next(d["clave"] for d in kpis if d["id"] == tornado_kpi)

            def modelo_t(s):
                return modelo(s, parametros.ctx, np.random.default_rng(seed))

            torn = mc.tornado(modelo_t, parametros.dists(), clave, seed)[:8]
            for f in torn:
                f["etiqueta"] = parametros.params[f["parametro"]].etiqueta
        res = Resultados(
            herr_id, lista, graficos=graficos(out, parametros.ctx) if graficos else [], tornado=torn,
            tabla=tabla(out, parametros.ctx) if tabla else [], notas=notas(out, parametros.ctx) if notas else [],
            sintetico=datos.es_sintetico(), n_mc=n_mc, semilla=seed)
    res.refs_pendientes = ref().pendientes(usadas)
    res.extra["refs_usadas"] = sorted(usadas)
    res.extra["kpi_tornado"] = tornado_kpi
    return res


def tri_rel(valor, banda):
    """Triangular alrededor de `valor` con una banda relativa (min, moda, max) de referencias.yaml."""
    return mc.tri(valor * banda[0], valor * banda[1], valor * banda[2])


def banda(x, axis=0):
    """Percentiles 10/50/90 de un array (n, m) -> dict de listas."""
    a = np.asarray(x, dtype=float)
    p = np.nanpercentile(a, [10, 50, 90], axis=axis)
    return {"p10": _a_lista(p[0]), "p50": _a_lista(p[1]), "p90": _a_lista(p[2])}
