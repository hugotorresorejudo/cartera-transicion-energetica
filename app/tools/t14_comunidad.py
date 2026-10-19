"""T14 — Autoconsumo colectivo en un bloque o comunidad energética: coeficientes de reparto y rentabilidad por vecino."""
from __future__ import annotations

import numpy as np

from core import clima, finanzas as fin, fv, montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01, t02_fv as t02

ID = "t14"
NOMBRE = "Autoconsumo colectivo"
DESCRIPCION = "Placas compartidas en un bloque: qué coeficiente de reparto conviene y cuánto ahorra cada vecino."
REPARTOS = {"igual": "Estático igual", "consumo": "Estático por consumo", "dinamico": "Dinámico horario"}


def preguntas() -> list[Pregunta]:
    qs = [Pregunta("vecinos", "Número de vecinos participantes", "select", [("<=10", "10 o menos"), ("11-30", "11–30"), (">30", "Más de 30")], "11-30")]
    qs += [q for q in t02.preguntas() if q.id in ("orientacion", "sombras")]
    qs += [Pregunta("tamano", "Tamaño de la instalación por vecino", "select", [("pequena", "Pequeña (~0,5 kWp)"), ("media", "Media (~1 kWp)"), ("grande", "Grande (~1,8 kWp)")], "media"),
           Pregunta("ocupacion", "¿Quién vive en el bloque?", "select", [("fuera", "Mayoría fuera en horario laboral"), ("mixto", "Mezcla"), ("casa", "Mayoría en casa durante el día")], "mixto"),
           Pregunta("reparto", "Coeficiente de reparto que propones", "select", [(k, v) for k, v in REPARTOS.items()], "dinamico"),
           Pregunta("cp", "Código postal", "texto", perfil="cp")]
    return qs


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"vecinos": "11-30", "orientacion": "S", "sombras": "ninguna", "tamano": "media", "ocupacion": "mixto", "reparto": "dinamico"}
    a.update(respuestas or {})
    D = mc.desde_rango
    b = t02.inferir(perfil, {"orientacion": a["orientacion"], "sombras": a["sombras"], "inclinacion": "plana", "cubierta": "plano"})
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    for k in ("azimut", "inclinacion", "L_sh", "p_exc", "r_desc", "g_elec", "degradacion", "opex_frac"):
        p[k] = b.params[k]
    p["kwp_vecino"] = Param("kwp_vecino", "Potencia por vecino", "kWp", D(r.sub("comunidad.kwp_por_vecino", a["tamano"])))
    p["capex_wp"] = Param("capex_wp", "CAPEX de la FV comunitaria", "€/Wp", D(r.rango("comunidad.capex_fv_comunitaria_eur_wp")))
    p["gestion"] = Param("gestion", "Gestión anual por participante", "€/año", D(r.rango("comunidad.coste_gestion_anual_eur_participante")))
    p["sg_vecino"] = Param("sg_vecino", "Dispersión del consumo entre vecinos", "desv. geométrica", mc.fijo(r.get("comunidad.sg_consumo_vecino")))
    p["ayuda"] = Param("ayuda", "Ayuda por vecino (ver T11)", "€", mc.fijo(0))
    return Parametros(p, {"perfil": perfil.to_dict(), "vecinos": int(r.sub("comunidad.vecinos", a["vecinos"])), "ocupacion": a["ocupacion"], "reparto": a["reparto"]})


def _perfiles_ocupacion(perfil: Perfil):
    """Perfil horario normalizado (8760, suma 1) de un hogar tipo para cada patrón de ocupación y su consumo anual mediano."""
    out = {}
    for o in ("fuera", "parcial", "casa"):
        pf = Perfil.from_dict({**perfil.to_dict(), "equipos": [], "ocupacion": o})
        F = pc.formas_cached(pf)
        en = pc.energias_inferidas(pf)
        e_t = sum(en[c] * F[c] for c in en)
        out[o] = (e_t / e_t.sum()).astype(np.float32), float(sum(en.values()))
    return out


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n0 = len(S["f_omie"])
    n = min(n0, int(r.get("comunidad.n_max_mc")))
    S = {k: v[:n] for k, v in S.items()}
    K = int(r.get("comunidad.n_simulados"))
    prof = _perfiles_ocupacion(perfil)
    probs = r.get("comunidad.mezcla_ocupacion")[ctx["ocupacion"]]
    orden = ["fuera", "parcial", "casa"]
    ocu = rng.choice(3, size=K, p=probs)
    E = []
    for i in range(K):
        forma, anual = prof[orden[ocu[i]]]
        s = anual * rng.lognormal(0.0, np.log(S["sg_vecino"][0]), n)
        E.append((s[:, None] * forma[None, :]).astype(np.float32))
    Etot = np.sum(E, axis=0)
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    p_e = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None])
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    Gu = fv.generacion_unitaria(perfil.cp, S["azimut"], S["inclinacion"], rng) * (1 - S["L_sh"])[:, None].astype(np.float32)
    G = Gu * (S["kwp_vecino"] * K)[:, None].astype(np.float32)
    p_exc = S["p_exc"][:, None].astype(np.float32)
    N = int(r.get("comunidad.horizonte_anios"))
    out = {}
    capex = S["kwp_vecino"] * 1000 * S["capex_wp"] - S["ayuda"]
    for met in REPARTOS:
        if met == "igual":
            beta = [np.full((n, 1), 1.0 / K, np.float32)] * K
        elif met == "consumo":
            tot = sum(e.sum(axis=1, keepdims=True) for e in E)
            beta = [e.sum(axis=1, keepdims=True) / tot for e in E]
        else:
            beta = [e / np.maximum(Etot, 1e-9) for e in E]
        ahorro_v = np.zeros(n)
        sc_num = np.zeros(n)
        for i in range(K):
            Gi = G * beta[i]
            Si, Xi, Ii = fv.balance(Gi, E[i])
            B = fv.compensacion(Xi, Ii, p_exc, p_e)
            ahorro_v += (Si * p_e).sum(axis=1) * imp + B * imp
            sc_num += Si.sum(axis=1)
        ahorro_v /= K
        sc = sc_num / np.maximum(G.sum(axis=1), 1e-9) * 100
        ah = fin.serie_anual(ahorro_v, N, S["g_elec"], S["degradacion"]) - (S["opex_frac"] * capex + S["gestion"])[:, None]
        cf = fin.flujos_proyecto(capex, ah)
        out[f"ahorro_{met}"] = ahorro_v
        out[f"sc_{met}"] = sc
        out[f"van_{met}"] = fin.van(cf, S["r_desc"])
        out[f"payback_{met}"] = fin.payback(cf)
    out["kwp_total"] = S["kwp_vecino"] * ctx["vecinos"]
    out["capex_vecino"] = capex
    sel = ctx["reparto"]
    for k in ("ahorro", "sc", "van", "payback"):
        out[k] = out[f"{k}_{sel}"]
    return out


KPIS = [
    {"id": "van", "nombre": "VAN por vecino (reparto elegido)", "unidad": "€", "clave": "van", "tipo": "ahorro", "prob": ("Probabilidad de VAN > 0", lambda v: v > 0)},
    {"id": "ahorro", "nombre": "Ahorro anual por vecino", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro"},
    {"id": "sc", "nombre": "Autoconsumo colectivo", "unidad": "%", "clave": "sc", "fmt": "{:.0f}"},
    {"id": "payback", "nombre": "Plazo de recuperación", "unidad": "años", "clave": "payback", "fmt": "{:.1f}", "inf_ok": True},
    {"id": "kwp_total", "nombre": "Potencia instalada de la comunidad", "unidad": "kWp", "clave": "kwp_total", "fmt": "{:.1f}"},
    {"id": "capex_vecino", "nombre": "Inversión por vecino", "unidad": "€", "clave": "capex_vecino", "tipo": "coste"},
]


def graficos(out, ctx):
    ks = list(REPARTOS)
    b = [mc.p10_50_90(out[f"van_{k}"]) for k in ks]
    s = [mc.p10_50_90(out[f"sc_{k}"]) for k in ks]
    return [{"tipo": "barras", "titulo": "VAN por vecino según el coeficiente de reparto (P10–P90)", "ylabel": "€", "categorias": [REPARTOS[k] for k in ks],
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]},
            {"tipo": "barras", "titulo": "Autoconsumo colectivo según el coeficiente (P10–P90)", "ylabel": "%", "categorias": [REPARTOS[k] for k in ks],
             "p10": [x[0] for x in s], "p50": [x[1] for x in s], "p90": [x[2] for x in s]}]


def tabla(out, ctx):
    return [{"Reparto": v, "Autoconsumo P50 (%)": round(mc.p10_50_90(out[f"sc_{k}"])[1]), "Ahorro P50 (€/año por vecino)": round(mc.p10_50_90(out[f"ahorro_{k}"])[1]),
             "VAN P50 (€ por vecino)": round(mc.p10_50_90(out[f"van_{k}"])[1])} for k, v in REPARTOS.items()]


def notas(out, ctx):
    return ["Requisitos: participantes a menos de 500 m de la instalación (hasta 2.000 m para FV en cubierta o suelo industrial) y acuerdo de reparto notificado a la distribuidora (RD 244/2019, RDL 29/2021).",
            "El coeficiente dinámico (Orden TED/1247/2021) maximiza el autoconsumo pero exige gestión horaria; el estático es más sencillo y reparte peor.",
            "Se simulan 8 participantes representativos con consumos y ocupaciones distintos; el resultado por vecino se extiende al total."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="van", graficos=graficos, tabla=tabla, notas=notas)
