"""T15 — Desplazamiento de cargas (lavadora, lavavajillas, secadora, termo): cuándo ponerlas."""
from __future__ import annotations

import numpy as np

from core import emisiones, montecarlo as mc, perfiles_carga as pc, precios
from core.calendario import calendario_tipico
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t15"
NOMBRE = "Desplazamiento de cargas"
DESCRIPCION = "Cuándo poner lavadora, lavavajillas, secadora o termo para pagar menos."
APARATOS = {"lavadora": "Lavadora", "lavavajillas": "Lavavajillas", "secadora": "Secadora", "termo": "Termo eléctrico"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("aparatos", "¿Qué aparatos tienes?", "multi", [(k, v) for k, v in APARATOS.items()], ["lavadora", "lavavajillas"]),
        Pregunta("habitual", "¿Cuándo los pones normalmente?", "select", [("manana", "Por la mañana"), ("tarde", "Por la tarde"), ("noche", "Por la noche"),
                                                                           ("cuando", "Cuando toca")], "noche"),
        Pregunta("ventana", "¿Cuándo aceptarías ponerlos?", "select", [("noche", "De noche (23–7 h, programados)"), ("solar", "Horas centrales del día (10–18 h)"),
                                                                       ("cualquiera", "A cualquier hora")], "cualquiera"),
        Pregunta("tarifa", "Tu tarifa", "select", [("pvpc", "PVPC"), ("idx", "Indexada"), ("fija_per", "Fija por periodos (punta, llano, valle)"), ("fija", "Precio fijo único")], "pvpc"),
        Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"aparatos": ["lavadora", "lavavajillas"], "habitual": "noche", "ventana": "cualquiera", "tarifa": "pvpc"}
    a.update(respuestas or {})
    D = mc.desde_rango
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas", "margen_idx", "p_fija")}
    npers = pc.n_personas(perfil)
    ciclos = r.get("electrodomesticos.ciclo_energia_kwh")
    usos = r.get("electrodomesticos.usos_semana_por_persona")
    mapa_c = r.get("desplazamiento.ciclo_aparato")
    for ap in a["aparatos"]:
        if ap == "termo":
            p["kwh_termo"] = Param("kwh_termo", "Energía diaria del termo", "kWh/día", D(r.get("desplazamiento.kwh_dia_termo_defecto")))
        else:
            p[f"E_{ap}"] = Param(f"E_{ap}", f"Energía por ciclo: {APARATOS[ap]}", "kWh/ciclo", D(ciclos[mapa_c[ap]]))
            p[f"u_{ap}"] = Param(f"u_{ap}", f"Usos por semana: {APARATOS[ap]}", "usos/semana", D(usos[f"{ap}_por_hogar"]))
    return Parametros(p, {"perfil": perfil.to_dict(), "aparatos": list(a["aparatos"]), "habitual": a["habitual"], "ventana": a["ventana"], "tarifa": a["tarifa"]})


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["f_omie"])
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    per = precios.periodos()
    tar = ctx["tarifa"]
    ca, lam = S["c_aj"][:, None], S["perdidas"][:, None]
    if tar == "pvpc":
        p = precios.precio_pvpc(omie, per, c_aj=ca, perdidas=lam)
    elif tar == "idx":
        p = precios.precio_indexado(omie, per, S["margen_idx"][:, None], ca, lam)
    elif tar == "fija_per":
        p = np.broadcast_to(precios.precio_fijo(S["p_fija"], True, per), (n, 8760))
    else:
        p = np.broadcast_to(precios.precio_fijo(S["p_fija"], False, per), (n, 8760))
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    P = (np.asarray(p, np.float32) * imp).reshape(n, 365, 24)
    hab = np.asarray(r.get("desplazamiento.horas_habituales")[ctx["habitual"]])
    ven = np.asarray(r.get("desplazamiento.ventanas")[ctx["ventana"]])
    p_hab = P[:, :, hab].mean(axis=2)          # precio a la hora habitual
    Pv = P[:, :, ven]
    p_best = Pv.min(axis=2)                     # precio en la mejor hora de la ventana
    mejor_h = ven[Pv.argmin(axis=2)]            # hora elegida cada día
    ef = emisiones.ef_mes_hora()
    mes_dia = calendario_tipico()["mes"].reshape(365, 24)[:, 0]
    ef_hab = ef[mes_dia[:, None], hab[None, :]].mean(axis=1)
    ahorro_tot = np.zeros(n)
    ciclos_tot = np.zeros(n)
    kwh_tot = np.zeros(n)
    co2 = np.zeros(n)
    por_aparato = {}
    ef_best_dia = ef[mes_dia[None, :], mejor_h]  # (n,365)
    for ap in ctx["aparatos"]:
        if ap == "termo":
            e_dia = S["kwh_termo"][:, None]
            uso_dia = r.get("desplazamiento.usos_semana_termo") / 7.0
            kwh = S["kwh_termo"] * 365
            ciclos = np.full(n, 365.0)
        else:
            e_dia = S[f"E_{ap}"][:, None]
            uso_dia = S[f"u_{ap}"][:, None] / 7.0
            kwh = S[f"E_{ap}"] * S[f"u_{ap}"] * 52
            ciclos = S[f"u_{ap}"] * 52
        a = (e_dia * uso_dia * (p_hab - p_best)).sum(axis=1)
        c = (e_dia * uso_dia * (ef_hab[None, :] - ef_best_dia)).sum(axis=1)
        por_aparato[ap] = a
        ahorro_tot += a
        co2 += c
        ciclos_tot += ciclos
        kwh_tot += kwh
    hist = np.bincount(mejor_h.ravel(), minlength=24) / mejor_h.size * 100
    return {"ahorro": ahorro_tot, "co2": co2, "ciclos": ciclos_tot, "kwh": kwh_tot, "por_ciclo": ahorro_tot / np.maximum(ciclos_tot, 1),
            "pct": ahorro_tot / np.maximum(kwh_tot * np.mean(P, axis=(1, 2)), 1e-9) * 100, "_ap": por_aparato, "_hist": hist}


KPIS = [
    {"id": "ahorro", "nombre": "Ahorro anual desplazando las cargas", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro", "fmt": "{:,.1f}",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 0)},
    {"id": "co2", "nombre": "Emisiones evitadas", "unidad": "kg CO₂/año", "clave": "co2", "fmt": "{:,.1f}"},
    {"id": "pct", "nombre": "Ahorro sobre el coste de esos aparatos", "unidad": "%", "clave": "pct", "fmt": "{:.0f}"},
    {"id": "por_ciclo", "nombre": "Ahorro por ciclo", "unidad": "€", "clave": "por_ciclo", "fmt": "{:.3f}"},
    {"id": "kwh", "nombre": "Energía de los aparatos considerados", "unidad": "kWh/año", "clave": "kwh"},
]


def graficos(out, ctx):
    ap = list(out["_ap"])
    b = [mc.p10_50_90(out["_ap"][k]) for k in ap]
    g = [{"tipo": "barras", "titulo": "Ahorro anual por aparato (P10–P90)", "ylabel": "€/año", "categorias": [APARATOS[k] for k in ap],
          "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]
    h = out["_hist"]
    g.append({"tipo": "barras", "titulo": "Hora más barata elegida (% de los días)", "ylabel": "%", "categorias": [str(i) for i in range(24)],
              "p10": h.tolist(), "p50": h.tolist(), "p90": h.tolist()})
    return g


def tabla(out, ctx):
    return [{"Aparato": APARATOS[k], "Ahorro P10 (€/año)": round(mc.p10_50_90(v)[0], 1), "P50": round(mc.p10_50_90(v)[1], 1), "P90": round(mc.p10_50_90(v)[2], 1)}
            for k, v in out["_ap"].items()]


def notas(out, ctx):
    n = ["Con precio fijo único no hay ahorro por desplazar; con PVPC o indexada el ahorro depende de la variación horaria del mercado."]
    if ctx["ventana"] == "noche":
        n.append("Los aparatos programados de noche requieren programación diferida y no dejar ropa húmeda en la lavadora.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="ahorro", graficos=graficos, tabla=tabla, notas=notas)
