"""T20 — Curvas agregadas de oferta y demanda del mercado diario: formación del precio marginal."""
from __future__ import annotations

import numpy as np

from core import datos, montecarlo as mc
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref

ID = "t20"
NOMBRE = "Curvas agregadas OMIE"
DESCRIPCION = "Cómo se forma el precio marginal y qué lo mueve: gas, renovables y demanda."


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("franja", "Franja del día", "select", [("madrugada", "Madrugada (4 h)"), ("mediodia", "Mediodía (14 h)"), ("noche", "Noche (21 h)")], "mediodia"),
        Pregunta("estacion", "Estación", "select", [("invierno", "Invierno"), ("primavera", "Primavera"), ("verano", "Verano"), ("otono", "Otoño")], "primavera"),
        Pregunta("gas", "Choque de precio del gas", "select", [("ninguno", "Ninguno"), ("mas50", "+50 %"), ("mas100", "+100 %"), ("menos30", "−30 %")], "ninguno"),
        Pregunta("renovable", "Choque de disponibilidad solar y eólica", "select", [("ninguno", "Ninguno"), ("menos25", "−25 %"), ("menos50", "−50 %"), ("mas25", "+25 %")], "ninguno"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"franja": "mediodia", "estacion": "primavera", "gas": "ninguno", "renovable": "ninguno"}
    a.update(respuestas or {})
    gas = r.get("lcoe.precio_gas_ttf_eur_mwh")
    p = {"f_gas": Param("f_gas", "Precio del gas respecto del de las curvas", "×", mc.tri(gas[0] / gas[1], 1.0, gas[2] / gas[1])),
         "f_ren": Param("f_ren", "Disponibilidad renovable (factor)", "×", mc.logn(1, r.get("curvas.sg_renovable"))),
         "f_dem": Param("f_dem", "Demanda (factor)", "×", mc.norm(1, r.get("curvas.sd_demanda"), *r.get("curvas.demanda_min_max"))),
         "choque_gas": Param("choque_gas", "Choque de gas aplicado", "×", mc.fijo(r.sub("curvas.choque_gas", a["gas"]))),
         "choque_ren": Param("choque_ren", "Choque renovable aplicado", "×", mc.fijo(r.sub("curvas.choque_renovable", a["renovable"])))}
    return Parametros(p, {"perfil": perfil.to_dict(), "hora": int(r.sub("curvas.horas", a["franja"])), "meses": r.sub("curvas.meses", a["estacion"]), **a})


def _registros(ctx):
    regs = [c for c in datos.curvas_omie() if c["hora"] == ctx["hora"] and int(c["fecha"][5:7]) in ctx["meses"]]
    return regs or [c for c in datos.curvas_omie() if c["hora"] == ctx["hora"]] or datos.curvas_omie()


def _matrices(regs, S, n, rng):
    r = ref()
    gas_t, ren_t = set(r.get("curvas.tecnologias_gas")), set(r.get("curvas.tecnologias_renovables"))
    nb = max(len(c["oferta"]) for c in regs)
    idx = rng.integers(0, len(regs), n)
    MW, PR, TEC = np.zeros((n, nb)), np.full((n, nb), np.inf), np.full((n, nb), "", dtype=object)
    for i, c in enumerate(regs):
        m = idx == i
        if not m.any():
            continue
        for j, b in enumerate(c["oferta"]):
            MW[m, j] = b["mw"]
            PR[m, j] = b["precio"]
            TEC[m, j] = b["tecnologia"]
    dem = np.array([regs[i]["demanda_mw"] for i in idx], float)
    f_gas = S["f_gas"] * S["choque_gas"]
    f_ren = S["f_ren"] * S["choque_ren"]
    for j in range(nb):
        g = np.array([t in gas_t for t in TEC[:, j]])
        rn = np.array([t in ren_t for t in TEC[:, j]])
        PR[:, j] = np.where(g, PR[:, j] * f_gas, PR[:, j])
        MW[:, j] = np.where(rn, MW[:, j] * f_ren, MW[:, j])
    return MW, PR, TEC, dem * S["f_dem"]


def modelo(S, ctx, rng):
    n = len(S["f_gas"])
    regs = _registros(ctx)
    MW, PR, TEC, dem = _matrices(regs, S, n, rng)
    orden = np.argsort(PR, axis=1)
    MWs, PRs = np.take_along_axis(MW, orden, 1), np.take_along_axis(PR, orden, 1)
    TECs = np.take_along_axis(TEC, orden, 1)
    cum = np.cumsum(MWs, axis=1)
    cubre = cum >= dem[:, None]
    j = np.where(cubre.any(axis=1), cubre.argmax(axis=1), cum.shape[1] - 1)
    techo = ref().get("curvas.precio_techo")
    precio = np.where(cubre.any(axis=1), PRs[np.arange(n), j], techo)
    marg = TECs[np.arange(n), j]
    ren = sum(np.where(np.isin(TECs, list(ref().get("curvas.tecnologias_renovables"))), np.minimum(MWs, np.maximum(dem[:, None] - (cum - MWs), 0)), 0.0).sum(axis=1)
              for _ in [0]) / dem * 100
    return {"precio": precio, "ren": ren, "dem": dem, "_marg": marg, "_MW": MWs[0], "_PR": PRs[0], "_TEC": TECs[0], "_dem0": float(dem[0])}


KPIS = [
    {"id": "precio", "nombre": "Precio marginal de casación", "unidad": "€/MWh", "clave": "precio", "fmt": "{:,.1f}"},
    {"id": "ren", "nombre": "Cuota de solar y eólica en el despacho", "unidad": "%", "clave": "ren", "fmt": "{:.0f}"},
    {"id": "dem", "nombre": "Demanda casada", "unidad": "MW", "clave": "dem"},
]


def graficos(out, ctx):
    MW, PR, dem = out["_MW"], out["_PR"], out["_dem0"]
    x, y = [0.0], [PR[0]]
    acum = 0.0
    for m, p in zip(MW, PR):
        if not np.isfinite(p):
            continue
        y.append(p)
        x.append(acum)
        acum += m
        y.append(p)
        x.append(acum)
    series = [{"nombre": "Oferta (orden de mérito)", "x": x, "y": y}, {"nombre": "Demanda", "x": [dem, dem], "y": [0, max(y)]}]
    marg = out["_marg"]
    nombres, cuentas = np.unique(marg, return_counts=True)
    frec = cuentas / cuentas.sum() * 100
    return [{"tipo": "lineas", "titulo": "Curva de oferta y demanda de un día representativo", "xlabel": "MW acumulados", "ylabel": "€/MWh", "series": series},
            {"tipo": "barras", "titulo": "Tecnología marginal (% de escenarios)", "ylabel": "%", "categorias": nombres.tolist(), "p10": frec.tolist(), "p50": frec.tolist(), "p90": frec.tolist()}]


def tabla(out, ctx):
    nombres, cuentas = np.unique(out["_marg"], return_counts=True)
    return [{"Tecnología marginal": str(k), "Frecuencia": f"{c / cuentas.sum():.0%}"} for k, c in sorted(zip(nombres, cuentas), key=lambda x: -x[1])]


def notas(out, ctx):
    n = ["Modelo de orden de mérito: el precio lo fija la última tecnología necesaria para cubrir la demanda; sin elasticidad ni ofertas estratégicas."]
    if datos.es_sintetico():
        n.append("Las curvas almacenadas son sintéticas (escalera de tecnologías); con datos reales de OMIE las curvas serán las ofertadas en el mercado diario.")
    return n


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="precio", graficos=graficos, tabla=tabla, notas=notas)
