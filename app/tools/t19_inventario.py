"""T19 — Inventario de electrodomésticos y consumo fantasma (stand-by)."""
from __future__ import annotations

import numpy as np

from core import montecarlo as mc, perfiles_carga as pc, precios
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref
from tools import t01_tarifas as t01

ID = "t19"
NOMBRE = "Inventario y consumo fantasma"
DESCRIPCION = "A dónde va tu consumo eléctrico y cuánto es stand-by."
APARATOS = {"nevera_combi": "Nevera", "congelador": "Congelador", "lavadora": "Lavadora", "lavavajillas": "Lavavajillas", "secadora": "Secadora",
            "horno": "Horno", "television": "Televisión", "iluminacion_hogar": "Iluminación", "ordenador": "Ordenador"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("aparatos", "Aparatos que tienes", "multi", [(k, v) for k, v in APARATOS.items()],
                 ["nevera_combi", "lavadora", "lavavajillas", "horno", "television", "iluminacion_hogar", "ordenador"]),
        Pregunta("edad", "Antigüedad de tus electrodomésticos", "select", [("nuevos", "Menos de 5 años"), ("medios", "5–10 años"), ("antiguos", "Más de 10 años")], "medios"),
        Pregunta("tv", "Televisores", "select", [("1", "1"), ("2", "2"), ("3+", "3 o más")], "1"),
        Pregunta("horas_tv", "Horas de TV al día (en total)", "select", [("<2", "Menos de 2"), ("2-4", "2–4"), (">4", "Más de 4")], "2-4"),
        Pregunta("apagas", "¿Apagas del todo los aparatos (regletas)?", "select", [("si", "Sí, casi siempre"), ("aveces", "A veces"), ("no", "No")], "aveces"),
        Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"aparatos": ["nevera_combi", "lavadora", "lavavajillas", "horno", "television", "iluminacion_hogar", "ordenador"], "edad": "medios", "tv": "1",
         "horas_tv": "2-4", "apagas": "aveces"}
    a.update(respuestas or {})
    D = mc.desde_rango
    ea = r.get("electrodomesticos.consumo_anual")
    base = t01.inferir(perfil, {})
    p = {k: base.params[k] for k in ("f_omie", "c_aj", "perdidas")}
    fp = (pc.n_personas(perfil) / r.get("perfil.personas_referencia")) ** r.get("perfil.exponente_personas")
    p["f_edad"] = Param("f_edad", "Factor de antigüedad", "×", D(r.sub("electrodomesticos.factor_edad", a["edad"])))
    for ap in a["aparatos"]:
        if ap == "television":
            ntv = r.sub("electrodomesticos.n_tv", a["tv"])
            h = r.sub("electrodomesticos.horas_tv", a["horas_tv"])
            p["kwh_television"] = Param("kwh_television", "Consumo de una TV a las horas de referencia", "kWh/año", D(ea["television"]))
            p["horas_tv"] = Param("horas_tv", "Horas de TV al día (total)", "h/día", D(h))
            p["n_tv"] = Param("n_tv", "Televisores", "ud", mc.fijo(ntv))
        else:
            escala = fp if ap in ("lavadora", "lavavajillas", "secadora", "ordenador") else 1.0
            p[f"kwh_{ap}"] = Param(f"kwh_{ap}", f"Consumo anual: {APARATOS[ap]}", "kWh/año", D(tuple(x * escala for x in ea[ap])))
    p["w_standby"] = Param("w_standby", "Potencia de stand-by del hogar", "W", D(r.rango("electrodomesticos.consumo_standby_hogar")))
    p["f_standby"] = Param("f_standby", "Factor de hábitos de apagado", "×", D(r.sub("electrodomesticos.factor_standby", a["apagas"])))
    return Parametros(p, {"perfil": perfil.to_dict(), "aparatos": list(a["aparatos"])})


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["f_edad"])
    omie = precios.escenarios_omie(n, rng) * S["f_omie"][:, None].astype(np.float32)
    imp = (1 + r.get("tarifa.iee_tipo") / 100.0) * (1 + r.get("tarifa.iva_electricidad") / 100.0)
    p_medio = precios.precio_pvpc(omie, precios.periodos(), c_aj=S["c_aj"][:, None], perdidas=S["perdidas"][:, None]).mean(axis=1) * imp
    por = {}
    for ap in ctx["aparatos"]:
        if ap == "television":
            ref_h = r.get("electrodomesticos.horas_tv_referencia")
            por[ap] = S["kwh_television"] * S["n_tv"] * (S["horas_tv"] / ref_h / np.maximum(S["n_tv"], 1)) * S["f_edad"]
        else:
            por[ap] = S[f"kwh_{ap}"] * S["f_edad"]
    standby = S["w_standby"] * S["f_standby"] * 8760 / 1000
    total = sum(por.values()) + standby
    perfil = Perfil.from_dict(ctx["perfil"])
    comp = pc.energias_inferidas(perfil)
    t01_total = sum(comp.values())
    out = {"total": total, "standby": standby, "standby_eur": standby * p_medio, "pct_standby": standby / total * 100,
           "ahorro_standby": standby * r.get("electrodomesticos.fraccion_evitable_standby") * p_medio, "cobertura": total / t01_total * 100, "_por": por, "p_medio": p_medio}
    return out


KPIS = [
    {"id": "standby_eur", "nombre": "Coste anual del consumo fantasma", "unidad": "€/año", "clave": "standby_eur", "tipo": "coste", "fmt": "{:,.1f}"},
    {"id": "pct_standby", "nombre": "Stand-by sobre el consumo inventariado", "unidad": "%", "clave": "pct_standby", "fmt": "{:.0f}"},
    {"id": "ahorro_standby", "nombre": "Ahorro apagando con regletas (70 % del stand-by)", "unidad": "€/año", "clave": "ahorro_standby", "tipo": "ahorro", "fmt": "{:,.1f}"},
    {"id": "total", "nombre": "Consumo de los aparatos inventariados", "unidad": "kWh/año", "clave": "total"},
    {"id": "standby", "nombre": "Consumo en stand-by", "unidad": "kWh/año", "clave": "standby"},
    {"id": "cobertura", "nombre": "Inventario sobre el consumo total estimado (T01)", "unidad": "%", "clave": "cobertura", "fmt": "{:.0f}"},
]


def graficos(out, ctx):
    items = [(APARATOS[k], mc.p10_50_90(v)) for k, v in out["_por"].items()] + [("Stand-by", mc.p10_50_90(out["standby"]))]
    items.sort(key=lambda x: -x[1][1])
    return [{"tipo": "barras", "titulo": "Consumo anual por aparato (P10–P90)", "ylabel": "kWh/año", "categorias": [i[0] for i in items],
             "p10": [i[1][0] for i in items], "p50": [i[1][1] for i in items], "p90": [i[1][2] for i in items]}]


def tabla(out, ctx):
    pm = float(np.median(out["p_medio"]))
    filas = [{"Aparato": APARATOS[k], "kWh/año (P50)": round(mc.p10_50_90(v)[1]), "€/año (P50)": round(mc.p10_50_90(v)[1] * pm, 1)} for k, v in out["_por"].items()]
    sb = mc.p10_50_90(out["standby"])[1]
    return filas + [{"Aparato": "Stand-by", "kWh/año (P50)": round(sb), "€/año (P50)": round(sb * pm, 1)}]


def notas(out, ctx):
    return ["El inventario cubre solo los aparatos que has marcado; el resto del consumo (cocina, agua caliente, climatización, coche) se estima en T01, T05, T09 y T18.",
            "Un enchufe inteligente o un vatímetro permite medir el stand-by real de cada aparato."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="standby_eur", graficos=graficos, tabla=tabla, notas=notas)
