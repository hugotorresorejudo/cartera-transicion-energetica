"""T16 — Calibración con la curva horaria de Datadis: sustituye el perfil sintético por el consumo real."""
from __future__ import annotations

import numpy as np

from core import datadis, montecarlo as mc, perfiles_carga as pc
from core.herramienta import Pregunta, Parametros, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t16"
NOMBRE = "Calibración con Datadis"
DESCRIPCION = "Sube tu curva de carga real y compara tarifas y potencia con tus datos."


def preguntas() -> list[Pregunta]:
    return [Pregunta("csv", "Archivo CSV de la curva de carga (descárgalo en datadis.es)", "archivo")]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    base = t01.inferir(perfil, {})
    ctx = dict(base.ctx)
    texto = (respuestas or {}).get("csv")
    ctx["datadis"] = None
    if texto:
        curva, st = datadis.curva_anual(datadis.parsear(texto))
        ctx["curva"] = [round(float(x), 4) for x in curva]
        ctx["datadis"] = st
    return Parametros(base.params, ctx)


def modelo(S, ctx, rng):
    out = t01.modelo(S, ctx, rng)
    perfil = Perfil.from_dict(ctx["perfil"])
    sint = sum(np.asarray(S[k]) for k in S if k.startswith("E_"))
    st = ctx.get("datadis")
    n = len(S["f_omie"])
    if st:
        out["E_real"] = np.full(n, st["E_anual"])
        out["error"] = (sint / st["E_anual"] - 1.0) * 100
        out["pmax_obs"] = np.full(n, st["pmax_kw"])
        for k in ("P1", "P2", "P3"):
            out[k] = np.full(n, st[k] * 100)
    else:
        out["E_real"] = out["E_anual"]
        out["error"] = np.full(n, np.nan)
        out["pmax_obs"] = np.full(n, np.nan)
        for k in ("P1", "P2", "P3"):
            out[k] = np.full(n, np.nan)
    return out


KPIS = t01.KPIS[:2] + [
    {"id": "E_real", "nombre": "Consumo anual (curva real o estimado)", "unidad": "kWh/año", "clave": "E_real"},
    {"id": "error", "nombre": "Error del perfil sintético frente a tus datos", "unidad": "%", "clave": "error", "fmt": "{:+.0f}"},
    {"id": "pmax_obs", "nombre": "Máxima demanda horaria observada", "unidad": "kW", "clave": "pmax_obs", "fmt": "{:.2f}"},
    {"id": "ahorro_pot", "nombre": "Ahorro por ajustar la potencia (PVPC)", "unidad": "€/año", "clave": "ahorro_pot", "tipo": "ahorro"},
    {"id": "P1", "nombre": "Consumo en P1 (punta)", "unidad": "%", "clave": "P1", "fmt": "{:.0f}"},
    {"id": "P2", "nombre": "Consumo en P2 (llano)", "unidad": "%", "clave": "P2", "fmt": "{:.0f}"},
    {"id": "P3", "nombre": "Consumo en P3 (valle)", "unidad": "%", "clave": "P3", "fmt": "{:.0f}"},
]


def notas(out, ctx):
    n = t01.notas(out, ctx)
    st = ctx.get("datadis")
    if st:
        n.append(f"Curva leída: {st['dias']} días medidos" + ("" if st["completo"] else " (año incompleto: se completa con el perfil medio por mes, tipo de día y hora)") + ".")
    else:
        n.append("Aún no has subido ningún archivo: se muestra el resultado con el perfil sintético. Sube tu CSV de Datadis para calibrar.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="coste_mejor", graficos=t01.graficos, tabla=t01.tabla, notas=notas)
