"""Gráficos matplotlib (estilo sobrio: un acento, neutros y colores semánticos para ahorro y coste)."""
from __future__ import annotations

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ACENTO, AHORRO, COSTE, TEXTO, SUAVE, BORDE = "#0f5c7a", "#1f8a5b", "#c2571a", "#1d2630", "#5b6773", "#d5dbe1"
CICLO = [ACENTO, COSTE, AHORRO, "#7a5c99", "#8a8f94"]

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"], "font.size": 9,
    "axes.edgecolor": BORDE, "axes.labelcolor": SUAVE, "xtick.color": SUAVE, "ytick.color": SUAVE, "text.color": TEXTO,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#eceff2", "grid.linewidth": 0.8,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.dpi": 110, "legend.frameon": False,
    "axes.prop_cycle": plt.cycler(color=CICLO),
})


def _fig(h=3.4):
    fig, ax = plt.subplots(figsize=(6.4, h))
    fig.set_tight_layout(True)
    return fig, ax


def dibujar(g: dict):
    t = g["tipo"]
    if t == "barras":
        fig, ax = _fig()
        x = np.arange(len(g["categorias"]))
        p10, p50, p90 = (np.asarray(g[k], float) for k in ("p10", "p50", "p90"))
        ax.bar(x, p50, color=ACENTO, width=0.55)
        ax.errorbar(x, p50, yerr=[np.maximum(p50 - p10, 0), np.maximum(p90 - p50, 0)], fmt="none", ecolor=TEXTO, capsize=4, lw=1.2)
        ax.set_xticks(x, g["categorias"], rotation=15 if len(x) > 3 else 0, ha="right" if len(x) > 3 else "center")
        ax.set_ylabel(g.get("ylabel", ""))
        ax.set_title(g["titulo"])
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
        ax.set_title(g["titulo"])
        if t == "abanico_multi" and len(series) > 1:
            ax.legend()
        return fig
    if t == "lineas":
        fig, ax = _fig()
        for i, s in enumerate(g["series"]):
            ax.plot(s["x"], s["y"], color=CICLO[i % len(CICLO)], lw=1.8, label=s["nombre"])
        ax.set_xlabel(g.get("xlabel", ""))
        ax.set_ylabel(g.get("ylabel", ""))
        ax.set_title(g["titulo"])
        if len(g["series"]) > 1:
            ax.legend()
        return fig
    if t == "heatmap":
        fig, ax = _fig(3.8)
        z = np.asarray(g["z"], float)
        im = ax.imshow(z, aspect="auto", cmap="viridis", origin="upper")
        ax.set_xlabel(g.get("xlabel", ""))
        ax.set_ylabel(g.get("ylabel", ""))
        ax.set_title(g["titulo"])
        ax.grid(False)
        fig.colorbar(im, ax=ax, label=g.get("unidad", ""))
        return fig
    if t == "barras_apiladas":
        fig, ax = _fig()
        x = np.arange(len(g["categorias"]))
        base = np.zeros(len(x))
        for i, s in enumerate(g["series"]):
            ax.bar(x, s["y"], bottom=base, label=s["nombre"], color=CICLO[i % len(CICLO)], width=0.55)
            base = base + np.asarray(s["y"], float)
        ax.set_xticks(x, g["categorias"], rotation=15 if len(x) > 4 else 0, ha="right" if len(x) > 4 else "center")
        ax.set_ylabel(g.get("ylabel", ""))
        ax.set_title(g["titulo"])
        ax.legend(fontsize=8)
        ax.grid(axis="x", visible=False)
        return fig
    raise ValueError(f"tipo de gráfico desconocido: {t}")


def tornado(filas: list, titulo: str = "Sensibilidad (parámetro en P10 / P90)", unidad: str = ""):
    filas = filas[:8][::-1]
    fig, ax = plt.subplots(figsize=(6.4, 0.45 * len(filas) + 1.2))
    fig.set_tight_layout(True)
    base = filas[0]["base"] if filas else 0
    for i, f in enumerate(filas):
        lo, hi = f["bajo"], f["alto"]
        ax.barh(i, lo - base, left=base, color=ACENTO, height=0.55)
        ax.barh(i, hi - base, left=base, color=COSTE, height=0.55)
    ax.axvline(base, color=TEXTO, lw=1)
    ax.set_yticks(range(len(filas)), [f.get("etiqueta", f["parametro"])[:42] for f in filas])
    ax.set_xlabel(unidad)
    ax.set_title(titulo)
    ax.grid(axis="y", visible=False)
    return fig
