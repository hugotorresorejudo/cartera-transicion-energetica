"""T07 — Cargador doméstico y potencia contratada (usa el consumo del VE de T04 y la simultaneidad de T01)."""
from __future__ import annotations

import numpy as np

from core import montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01, t04_ve as t04

ID = "t07"
NOMBRE = "Cargador doméstico y potencia"
DESCRIPCION = "Qué cargador instalar y qué potencia contratar para el coche eléctrico."


def preguntas() -> list[Pregunta]:
    qs = [q for q in t04.preguntas() if q.id in ("km_lab", "parking", "horario", "segmento")]
    qs.append(Pregunta("fases", "Tu suministro es", "select", [("mono", "Monofásico"), ("tri", "Trifásico"), ("nose", "No lo sé")], "mono"))
    qs.append(Pregunta("gestion", "¿Admite gestión dinámica de potencia (balanceo)?", "select", [("si", "Sí"), ("no", "No"), ("nose", "No lo sé")], "nose"))
    return qs


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"km_lab": "20-50", "parking": "garaje_propio", "horario": "b", "segmento": "compacto", "fases": "mono", "gestion": "nose"}
    a.update(respuestas or {})
    b = t04.inferir(perfil, {k: a[k] for k in ("km_lab", "parking", "horario", "segmento")})
    p = {k: b.params[k] for k in ("km_lab", "km_fds", "c_ev", "f_real", "f_temp", "eta_ch", "f_omie", "c_aj", "perdidas")}
    p["P_actual"] = Param("P_actual", "Potencia contratada actual", "kW", mc.fijo(perfil.potencia) if perfil.potencia else
                          mc.fijo(r.get("tarifa.potencias_normalizadas")[r.get("tarifa.potencia_sin_dato")[1]]))
    p["p_base_noche"] = Param("p_base_noche", "Carga base nocturna", "kW", mc.desde_rango(r.rango("cargador.p_base_noche_kw")))
    p["alpha"] = Param("alpha", "Probabilidad anual de corte admitida", "-", mc.fijo(r.get("tarifa.alpha_corte")))
    return Parametros(p, {"perfil": perfil.to_dict(), "parking": a["parking"], "arr": b.ctx["arr"], "dep": b.ctx["dep"], "fases": a["fases"],
                          "gestion": a["gestion"]})


def _configuraciones(ctx):
    pots = [float(x) for x in ref().get("cargador.potencias_kw")]
    if ctx["fases"] == "mono":
        pots = [x for x in pots if x <= ref().get("cargador.monofasico_max_kw")]
    return [(pc_, g) for pc_ in pots for g in (False, True)]


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["km_lab"])
    km_anual = 52 * 5 * S["km_lab"] + S["km_fds"]
    e_dia = km_anual * S["c_ev"] * S["f_real"] * S["f_temp"] / 100.0 / S["eta_ch"] / 365.0  # kWh de red por día
    ventana = len(np.arange(ctx["arr"], 24 + ctx["dep"] if ctx["dep"] <= ctx["arr"] else ctx["dep"]))
    norm = np.asarray(r.get("tarifa.potencias_normalizadas"), float)
    sin_ve = set(perfil.equipos) - {"ve"}
    n_pm = int(r.get("tarifa.pmax_muestras"))
    rng2 = np.random.default_rng(mc.SEMILLA + 3)
    pmax_otros, _ = pc.simular_pmax(sin_ve, n_pm, rng2)
    pot = precios.potencia_regulada()
    tasa = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    out, cands = {}, _configuraciones(ctx)
    quant = r.get("cargador.cuantil_potencia")
    P_act = float(np.median(S["P_actual"]))
    mejor, mejor_coste = None, np.inf
    tabla = []
    for pch, gest in cands:
        if gest:
            req = np.maximum(pmax_otros, pch + float(np.median(S["p_base_noche"])))
        else:
            pm_ve, _ = pc.simular_pmax(sin_ve | {"ve"}, n_pm, np.random.default_rng(mc.SEMILLA + 4), potencias={"ve": [pch, pch, pch]})
            req = pm_ve
        p_req = norm[np.minimum(np.searchsorted(norm, req), len(norm) - 1)]
        p_rec = float(np.quantile(p_req, quant))
        horas = e_dia / pch
        ok = float(np.mean(horas <= ventana))
        extra = max(p_rec - P_act, 0.0) * (pot[0] + pot[1]) / 2 * tasa
        tabla.append({"Cargador (kW)": pch, "Gestión dinámica": "sí" if gest else "no", "Potencia a contratar (kW)": p_rec,
                      "Horas de carga (P50)": round(float(np.median(horas)), 1), "Completa la carga": f"{ok:.0%}", "Coste extra de potencia (€/año)": round(extra)})
        factible = ok >= r.get("cargador.confianza_horas") and (not gest or ctx["gestion"] != "no")
        if factible and (extra + 0.01 * pch < mejor_coste):
            mejor, mejor_coste = (pch, gest, p_rec, p_req, horas, extra), extra + 0.01 * pch
    if mejor is None:  # sin configuración factible: la de mayor potencia
        pch, gest = cands[-1]
        mejor = (pch, gest, P_act, np.full(n_pm, P_act), e_dia / pch, 0.0)
    pch, gest, p_rec, p_req, horas, extra = mejor
    # el coste extra por muestra: potencia requerida (muestreada) frente a la actual
    pr = rng.choice(p_req, size=n)
    out = {"pch": np.full(n, pch), "p_rec": pr, "horas": e_dia / pch, "extra": np.maximum(pr - S["P_actual"], 0) * (pot[0] + pot[1]) / 2 * tasa,
           "e_dia": e_dia, "p_corte": np.full(n, float(np.mean(p_req > p_rec))), "_tabla": tabla, "_gest": np.full(n, float(gest))}
    return out


KPIS = [
    {"id": "p_rec", "nombre": "Potencia a contratar recomendada", "unidad": "kW", "clave": "p_rec", "fmt": "{:.2f}"},
    {"id": "pch", "nombre": "Potencia del cargador", "unidad": "kW", "clave": "pch", "fmt": "{:.1f}"},
    {"id": "extra", "nombre": "Coste extra de potencia (frente a la actual)", "unidad": "€/año", "clave": "extra", "tipo": "coste"},
    {"id": "horas", "nombre": "Horas de carga por día", "unidad": "h", "clave": "horas", "fmt": "{:.1f}"},
    {"id": "e_dia", "nombre": "Energía diaria a cargar", "unidad": "kWh/día", "clave": "e_dia", "fmt": "{:.1f}"},
]


def tabla(out, ctx):
    return out["_tabla"]


def graficos(out, ctx):
    t = out["_tabla"]
    cats = [f"{f['Cargador (kW)']:g} kW{' + gestión' if f['Gestión dinámica'] == 'sí' else ''}" for f in t]
    return [{"tipo": "barras", "titulo": "Potencia a contratar según configuración", "ylabel": "kW", "categorias": cats,
             "p10": [f["Potencia a contratar (kW)"] for f in t], "p50": [f["Potencia a contratar (kW)"] for f in t],
             "p90": [f["Potencia a contratar (kW)"] for f in t]}]


def notas(out, ctx):
    n = ["La recomendación es el menor coste con carga completa en la ventana de disponibilidad y la probabilidad de corte admitida (α)."]
    if float(out["_gest"][0]) > 0.5:
        n.append("Se recomienda un sistema de gestión dinámica de potencia (ITC-BT-52): el cargador cede potencia a la vivienda.")
    if ctx["parking"] == "calle":
        n.append("Sin plaza propia no hay carga doméstica: usa T04 para ver el coste con carga pública.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="extra", graficos=graficos, tabla=tabla, notas=notas)
