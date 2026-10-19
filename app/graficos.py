"""Gráficos matplotlib (estilo sobrio: un acento, neutros y colores semánticos para ahorro y coste)."""
from __future__ import annotations

import textwrap

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ACENTO, AHORRO, COSTE, TEXTO, SUAVE, BORDE = "#0047ab", "#0a2a52", "#7f9ccb", "#1b1f24", "#4b5563", "#d3dbe6"
CICLO = [ACENTO, "#0a2a52", "#6f93cf", "#9aa9bd", "#003a8c"]

from pathlib import Path  # noqa: E402

from matplotlib import font_manager  # noqa: E402

for _f in sorted((Path(__file__).resolve().parent / "www" / "fonts").glob("Roboto_*.ttf")):
    font_manager.fontManager.addfont(str(_f))

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Roboto", "Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 9,
    "axes.edgecolor": BORDE, "axes.labelcolor": SUAVE, "xtick.color": SUAVE, "ytick.color": SUAVE, "text.color": TEXTO,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e3e8ef", "grid.linewidth": 0.8,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": "#0a2a52", "axes.titlelocation": "left", "figure.dpi": 110, "legend.frameon": False,
    "axes.prop_cycle": plt.cycler(color=CICLO),
})


def _fig(h=3.4, bottom=0.17):
    """Figura con márgenes fijos (el layout automático de matplotlib no es compatible con Shiny y falla en pantallas estrechas)."""
    fig, ax = plt.subplots(figsize=(6.4, h))
    fig.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=bottom)
    return fig, ax


def _titulo(fig, ax, texto):
    lineas = textwrap.wrap(texto, 52)
    ax.set_title("\n".join(lineas), fontsize=9)
    if len(lineas) > 1:
        fig.subplots_adjust(top=0.82)


def _envolver(etiquetas, ancho=13):
    return ["\n".join(textwrap.wrap(str(e), ancho)) or str(e) for e in etiquetas]


def dibujar(g: dict):
    t = g["tipo"]
    if t == "barras":
        muchas = len(g["categorias"]) > 8
        fig, ax = _fig(bottom=0.12 if muchas else 0.30)
        x = np.arange(len(g["categorias"]))
        p10, p50, p90 = (np.asarray(g[k], float) for k in ("p10", "p50", "p90"))
        ax.bar(x, p50, color=ACENTO, width=0.55, zorder=2)
        ax.errorbar(x, p50, yerr=[np.maximum(p50 - p10, 0), np.maximum(p90 - p50, 0)], fmt="none", ecolor=TEXTO, capsize=4, lw=1.2)
        if not muchas:
            for xi, v in zip(x, p50):
                ax.annotate(f"{v:,.0f}".replace(",", "."), (xi, 0), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="white", fontweight="bold")
        if muchas:
            ax.set_xticks(x[::2], [str(c) for c in g["categorias"]][::2])
        else:
            ax.set_xticks(x, _envolver(g["categorias"]), fontsize=8)
        ax.set_ylabel(g.get("ylabel", ""))
        _titulo(fig, ax, g["titulo"])
        ax.grid(axis="x", visible=False)
        return fig
    if t in ("abanico", "abanico_multi"):
        fig, ax = _fig()
        series = g["series"] if t == "abanico_multi" else [{"nombre": "", "x": g["x"], "p10": g["p10"], "p50": g["p50"], "p90": g["p90"]}]
        for i, s in enumerate(series):
            c = CICLO[i % len(CICLO)]
            ax.fill_between(s["x"], s["p10"], s["p90"], color=c, alpha=0.18, lw=0)
            ax.plot(s["x"], s["p50"], color=c, lw=2, label=s["nombre"] or None)
        ax.set_xlabel(g.get("xlabel", ""))
        ax.set_ylabel(g.get("ylabel", ""))
        _titulo(fig, ax, g["titulo"])
        if t == "abanico_multi" and len(series) > 1:
            ax.legend()
        return fig
    if t == "lineas":
        fig, ax = _fig()
        for i, s in enumerate(g["series"]):
            ax.plot(s["x"], s["y"], color=CICLO[i % len(CICLO)], lw=1.8, label=s["nombre"])
        ax.set_xlabel(g.get("xlabel", ""))
        ax.set_ylabel(g.get("ylabel", ""))
        _titulo(fig, ax, g["titulo"])
        if len(g["series"]) > 1:
            ax.legend()
        return fig
    if t == "heatmap":
        fig, ax = _fig(3.8, bottom=0.14)
        z = np.asarray(g["z"], float)
        im = ax.imshow(z, aspect="auto", cmap="Blues", origin="upper")
        ax.set_xlabel(g.get("xlabel", ""))
        ax.set_ylabel(g.get("ylabel", ""))
        _titulo(fig, ax, g["titulo"])
        ax.grid(False)
        fig.colorbar(im, ax=ax, label=g.get("unidad", ""))
        return fig
    if t == "barras_apiladas":
        fig, ax = _fig(bottom=0.14)
        x = np.arange(len(g["categorias"]))
        base = np.zeros(len(x))
        for i, s in enumerate(g["series"]):
            ax.bar(x, s["y"], bottom=base, label=s["nombre"], color=CICLO[i % len(CICLO)], width=0.55)
            base = base + np.asarray(s["y"], float)
        ax.set_xticks(x[::2] if len(x) > 8 else x, [str(c) for c in (g["categorias"][::2] if len(x) > 8 else g["categorias"])])
        ax.set_ylabel(g.get("ylabel", ""))
        _titulo(fig, ax, g["titulo"])
        ax.legend(fontsize=7, ncol=2)
        ax.grid(axis="x", visible=False)
        return fig
    raise ValueError(f"tipo de gráfico desconocido: {t}")


def tornado(filas: list, titulo: str = "Sensibilidad (parámetro en P10 / P90)", unidad: str = ""):
    filas = filas[:8][::-1]
    fig, ax = plt.subplots(figsize=(6.4, 0.45 * len(filas) + 1.2))
    fig.subplots_adjust(left=0.5, right=0.96, top=0.8 if len(filas) > 4 else 0.62, bottom=0.2)
    base = filas[0]["base"] if filas else 0
    for i, f in enumerate(filas):
        lo, hi = f["bajo"], f["alto"]
        ax.barh(i, lo - base, left=base, color=ACENTO, height=0.55)
        ax.barh(i, hi - base, left=base, color=COSTE, height=0.55)
    ax.axvline(base, color=TEXTO, lw=1)
    ax.set_yticks(range(len(filas)), _envolver([f.get("etiqueta", f["parametro"])[:48] for f in filas], 20), fontsize=7)
    ax.set_xlabel(unidad)
    ax.set_title("\n".join(textwrap.wrap(titulo, 44)), fontsize=8.5, loc="left")
    ax.grid(axis="y", visible=False)
    return fig
