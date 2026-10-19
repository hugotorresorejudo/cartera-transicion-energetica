"""T06 — Batería doméstica asociada a una instalación fotovoltaica (usa el motor de T02 y T01)."""
from __future__ import annotations

import numpy as np

from core import bateria, finanzas as fin, fv, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t02_fv as t02

ID = "t06"
NOMBRE = "Batería doméstica"
DESCRIPCION = "¿Compensa añadir almacenamiento a tus placas? Capacidad recomendada y retorno."


def preguntas() -> list[Pregunta]:
    qs = [q for q in t02.preguntas() if q.id in ("orientacion", "inclinacion", "sombras", "tamano")]
    qs.append(Pregunta("capacidad", "Capacidad de batería", "select",
                       [("auto", "Que la herramienta la recomiende"), ("5", "5 kWh"), ("10", "10 kWh"), ("15", "15 kWh")], "auto"))
    return qs


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = dict(respuestas or {})
    base = t02.inferir(perfil, {k: a[k] for k in ("orientacion", "inclinacion", "sombras", "tamano") if k in a})
    p = {k: v for k, v in base.params.items() if k not in ("ayudas",)}
    cap = a.get("capacidad", "auto")
    D = mc.desde_rango
    p["cap_fija"] = Param("cap_fija", "Capacidad fija de la batería (0 = recomendar)", "kWh", mc.fijo(0 if cap == "auto" else float(cap)))
    p["capex_kwh"] = Param("capex_kwh", "CAPEX de la batería instalada", "€/kWh", D(r.rango("almacenamiento.capex_bateria_eur_kwh")))
    p["eta_rt"] = Param("eta_rt", "Eficiencia de ida y vuelta", "-", D(r.rango("almacenamiento.eficiencia_ciclo")))
    p["dod"] = Param("dod", "Profundidad de descarga útil", "-", mc.fijo(r.get("almacenamiento.dod_util")))
    p["p_bat"] = Param("p_bat", "Potencia del inversor híbrido", "kW", D(r.rango("almacenamiento.potencia_inversor_hibrido_kw")))
    p["deg_bat"] = Param("deg_bat", "Degradación anual de la batería", "fracción", D(r.rango("almacenamiento.degradacion_anual_bateria")))
    p["vida_ciclos"] = Param("vida_ciclos", "Vida en ciclos", "ciclos", mc.fijo(r.get("almacenamiento.vida_ciclos")))
    p["vida_cal"] = Param("vida_cal", "Vida calendario", "años", mc.fijo(r.get("almacenamiento.vida_calendario_anios")))
    p["ayuda_bat"] = Param("ayuda_bat", "Ayudas a la batería", "€", mc.fijo(0))
    return Parametros(p, dict(base.ctx))


def modelo(S, ctx, rng):
    r = ref()
    perfil, pext = Perfil.from_dict(ctx["perfil"]), Perfil.from_dict(ctx["perfil_ext"])
    n = len(S["f_omie"])
    E, _ = t02._consumo(S, ctx, rng, perfil, pext)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    per = precios.periodos()
    p_e, mod = t02._precio(S, omie, per)
    pot = precios.potencia_precios(mod, S["pot_fija_dia"] if mod == "fija" else None)
    P1, P2, bono = S["P1"], S["P1"] + S["P2_delta"], S["bono"]
    p_exc = np.where(S["modo_exc"][:, None] > 0.5, np.maximum(omie, 0) / 1000.0, S["p_exc"][:, None]).astype(np.float32)
    Gu = fv.generacion_unitaria(perfil.cp, S["azimut"], S["inclinacion"], rng) * (1 - S["L_sh"])[:, None].astype(np.float32)
    P_max = np.minimum(S["plazas"] * S["m2_plaza"] / S["m2_kwp"], r.get("fv.compensacion_simplificada_potencia_max_kw"))
    Pp = np.where(S["P_p_fija"] > 0, S["P_p_fija"],
                  np.minimum(P_max, r.get("almacenamiento.dim_fv_factor") * E.sum(1) / np.maximum(Gu.sum(1), 1e-6)))
    G = Gu * Pp[:, None].astype(np.float32)

    def coste(I, X):
        B = fv.compensacion(X, I, p_exc, p_e)
        return precios.factura(I, p_e, P1, P2, pot, bono, credito=B)["total"]

    S0, X0, I0 = fv.balance(G, E)
    sin = coste(I0, X0)
    N = ctx["horizonte"]
    anios = np.arange(1, N + 1)

    def van_cap(cap, idx):
        Sb, Xb, Ib, ciclos = bateria.despacho(G[idx], E[idx], cap, S["p_bat"][idx], S["eta_rt"][idx], S["dod"][idx])
        pe = p_e if p_e.ndim == 1 else p_e[idx]
        B = fv.compensacion(Xb, Ib, p_exc[idx], pe)
        con = precios.factura(Ib, pe, P1[idx], P2[idx], pot, bono[idx], credito=B)["total"]
        a1 = sin[idx] - con
        capex = cap * S["capex_kwh"][idx]
        vida = np.minimum(S["vida_cal"][idx], S["vida_ciclos"][idx] / np.maximum(ciclos, 1.0))
        ah = fin.serie_anual(a1, N, S["g_elec"][idx], S["deg_bat"][idx])
        extras = np.zeros_like(ah)
        k = np.clip(np.round(vida).astype(int), 1, N) - 1
        reposicion = (vida < N) & (cap > 0)
        extras[np.arange(ah.shape[0]), k] = np.where(reposicion, -capex * r.get("almacenamiento.reposicion_factor"), 0.0)
        cf = fin.flujos_proyecto(capex - S["ayuda_bat"][idx], ah, 0.0, extras)
        return fin.van(cf, S["r_desc"][idx]), cf, a1, Sb, Ib, ciclos

    cap_fija = float(np.median(S["cap_fija"]))
    cands = [cap_fija] if cap_fija > 0 else [float(c) for c in r.get("almacenamiento.capacidades_candidatas_kwh")]
    sub = slice(0, min(n, int(r.get("almacenamiento.n_muestras_dimensionado"))))
    curva = np.stack([van_cap(c, sub)[0] if c > 0 else np.zeros(min(n, sub.stop)) for c in cands], axis=1)
    cap_star = cands[int(np.argmax(curva.mean(axis=0)))]
    if cap_star > 0:
        van, cf, a1, Sb, Ib, ciclos = van_cap(cap_star, slice(None))
        sc, ss = fv.indicadores(Sb, G, E)
        pay = fin.payback(cf)
    else:
        van = np.zeros(n)
        a1 = np.zeros(n)
        Sb = S0
        ciclos = np.zeros(n)
        sc, ss = fv.indicadores(S0, G, E)
        pay = np.full(n, np.nan)
    sc0, ss0 = fv.indicadores(S0, G, E)
    return {"van": van, "ahorro1": a1, "payback": pay, "cap": np.full(n, cap_star), "ciclos": ciclos, "sc": sc * 100, "ss": ss * 100,
            "sc0": sc0 * 100, "ss0": ss0 * 100, "Pp": Pp, "curva": curva, "cands": np.array(cands)}


KPIS = [
    {"id": "van", "nombre": "VAN de la batería a 25 años", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "ahorro1", "nombre": "Ahorro adicional del primer año", "unidad": "€/año", "clave": "ahorro1", "tipo": "ahorro"},
    {"id": "cap", "nombre": "Capacidad recomendada", "unidad": "kWh", "clave": "cap", "fmt": "{:.0f}"},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}"},
    {"id": "ss", "nombre": "Autosuficiencia con batería", "unidad": "%", "clave": "ss", "fmt": "{:.0f}"},
    {"id": "ss0", "nombre": "Autosuficiencia sin batería", "unidad": "%", "clave": "ss0", "fmt": "{:.0f}"},
    {"id": "sc", "nombre": "Autoconsumo con batería", "unidad": "%", "clave": "sc", "fmt": "{:.0f}"},
    {"id": "ciclos", "nombre": "Ciclos equivalentes al año", "unidad": "ciclos", "clave": "ciclos", "fmt": "{:.0f}"},
    {"id": "Pp", "nombre": "FV de partida (T02)", "unidad": "kWp", "clave": "Pp", "fmt": "{:.1f}"},
]


def graficos(out, ctx):
    b = np.nanpercentile(out["curva"], [10, 50, 90], axis=0)
    return [{"tipo": "abanico", "titulo": "VAN de la batería según su capacidad (P10–P90)", "xlabel": "Capacidad (kWh)", "ylabel": "VAN (€)",
             "x": out["cands"].tolist(), "p10": b[0].tolist(), "p50": b[1].tolist(), "p90": b[2].tolist()}]


def notas(out, ctx):
    n = []
    if float(out["cap"][0]) <= 0:
        n.append("Con los precios actuales ninguna capacidad candidata tiene VAN esperado positivo: la batería no compensa económicamente.")
    n.append("Despacho de autoconsumo hora a hora; no se modela el arbitraje con la red ni el respaldo ante cortes.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, notas=notas)
