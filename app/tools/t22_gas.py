"""T22 — Gas: TUR frente a mercado libre y butano."""
from __future__ import annotations

import numpy as np

from core import emisiones, montecarlo as mc, perfiles_carga as pc, termico
from core.herramienta import Param, Parametros, Pregunta, ejecutar, tri_rel
from core.perfil import Perfil
from core.referencias import ref

ID = "t22"
NOMBRE = "Tarifa de gas y butano"
DESCRIPCION = "TUR, mercado libre o butano: cuál te sale más barato."
ALTERNATIVAS = {"tur": "TUR (regulada)", "libre": "Mercado libre", "butano": "Butano"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("usos", "¿Para qué usas el gas?", "multi", [("cocina", "Cocina"), ("acs", "Agua caliente"), ("calefaccion", "Calefacción")], ["cocina", "acs"]),
        Pregunta("actual", "Tu suministro actual", "select", [("tur", "Gas natural, TUR"), ("libre", "Gas natural, mercado libre"),
                                                             ("butano", "Butano"), ("nose", "No lo sé")], "tur"),
        Pregunta("factura", "Importe medio de la factura de gas al mes", "select",
                 [("<20", "Menos de 20 €"), ("20-40", "20–40 €"), ("40-80", "40–80 €"), (">80", "Más de 80 €"), ("nose", "No lo sé")], "nose"),
        Pregunta("personas", "Personas en casa", "select", [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")], perfil="personas"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", [("piso_<70", "Piso <70 m²"), ("piso_70_120", "Piso 70–120 m²"), ("piso_>120", "Piso >120 m²"),
                                                                   ("unif_<120", "Unifamiliar <120 m²"), ("unif_>120", "Unifamiliar >120 m²")], perfil="vivienda"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"usos": ["cocina", "acs"], "actual": "tur", "factura": "nose"}
    a.update(respuestas or {})
    usos = set(a["usos"])
    npers = pc.n_personas(perfil)
    sg = r.get("perfil.sg_componente")
    D = mc.desde_rango
    p = {}
    eta = r.rango("acs.rendimiento_calentador_gas")
    p["eta_acs"] = Param("eta_acs", "Rendimiento del equipo de ACS (PCS)", "-", D(eta))
    if "cocina" in usos:
        p["E_cocina"] = Param("E_cocina", "Gas para cocinar", "kWh/año", mc.logn(r.get("cocina.gas_consumo_kwh_ano_persona")[1] * npers, sg))
    if "acs" in usos:
        p["E_acs"] = Param("E_acs", "Gas para agua caliente", "kWh/año", mc.logn(pc.acs_util_cte_kwh(perfil) / eta[1], sg))
    if "calefaccion" in usos:
        d = pc.demanda_calefaccion_util(perfil)
        uso = r.get("calefaccion.fraccion_uso_calefaccion")
        eta_c = r.get("calefaccion.caldera_gas_rendimiento_estacional_pcs")[1]
        p["E_calefaccion"] = Param("E_calefaccion", "Gas para calefacción", "kWh/año", mc.logn(d[1] * uso[1] / eta_c, r.get("calefaccion.sg_demanda")))
    if not any(k.startswith("E_") for k in p):
        p["E_cocina"] = Param("E_cocina", "Gas para cocinar", "kWh/año", mc.logn(r.get("cocina.gas_consumo_kwh_ano_persona")[1] * npers, sg))
    p["f_gas"] = Param("f_gas", "Nivel de precios del gas (factor)", "-", mc.logn(1, r.get("gas.sg_precio")))
    for k, clave in (("tur1", "tur1"), ("tur2", "tur2")):
        p[f"fijo_{k}"] = Param(f"fijo_{k}", f"Término fijo {k.upper()}", "€/mes", mc.fijo(r.get(f"gas.tur_termino_fijo_{clave}")))
        p[f"var_{k}"] = Param(f"var_{k}", f"Término variable {k.upper()}", "€/kWh", mc.fijo(r.get(f"gas.tur_termino_variable_{clave}")))
    p["var_libre"] = Param("var_libre", "Término variable de la oferta libre", "€/kWh", D(r.rango("gas.oferta_libre_tipica")))
    p["fijo_libre_ratio"] = Param("fijo_libre_ratio", "Término fijo libre / TUR", "×", D(r.get("gas.fijo_libre_ratio")))
    pb = r.get("gas.butano_precio_bombona")
    p["bombona"] = Param("bombona", "Precio de la bombona de butano (12,5 kg)", "€", tri_rel(pb, r.get("gas.banda_bombona")))
    p["alquiler"] = Param("alquiler", "Alquiler del contador", "€/mes", mc.fijo(r.get("gas.alquiler_contador")))
    p["ih"] = Param("ih", "Impuesto de hidrocarburos", "€/kWh", mc.fijo(r.get("gas.gas_natural_impuesto_hidrocarburos")))
    return Parametros(p, {"perfil": perfil.to_dict(), "actual": "tur" if a["actual"] == "nose" else a["actual"], "factura": a["factura"]})


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["f_gas"])
    comp = sum(S[k] for k in S if k.startswith("E_"))
    iva = 1 + r.get("gas.iva") / 100.0
    fijo_t = np.where(comp <= r.get("gas.umbral_tur1_kwh"), S["fijo_tur1"], S["fijo_tur2"])
    var_t = np.where(comp <= r.get("gas.umbral_tur1_kwh"), S["var_tur1"], S["var_tur2"]) * S["f_gas"]
    # calibración con la factura (si hay): combina el prior por usos con la inversión de la factura de la TUR
    E = comp
    if ctx["factura"] != "nose":
        lo, mo, hi = r.sub("gas.factura_mes_eur", ctx["factura"])
        imp = rng.triangular(lo, mo, hi, n)
        e_obs = np.maximum((imp * 12 / iva - (fijo_t + S["alquiler"]) * 12) / (var_t + S["ih"]), 1.0)
        wp, wo = 1 / np.log(r.get("perfil.sg_prior_consumo")) ** 2, 1 / np.log(r.get("perfil.sg_factura")) ** 2
        E = np.exp((wp * np.log(comp) + wo * np.log(e_obs)) / (wp + wo))
    c_tur = (12 * (fijo_t + S["alquiler"]) + E * (var_t + S["ih"])) * iva
    var_l = S["var_libre"] * S["f_gas"]
    c_lib = (12 * (fijo_t * S["fijo_libre_ratio"] + S["alquiler"]) + E * (var_l + S["ih"])) * iva
    c_but = E / (r.get("gas.bombona_kg") * r.get("gas.butano_pcs")) * S["bombona"]
    costes = {"tur": c_tur, "libre": c_lib, "butano": c_but}
    actual = costes[ctx["actual"]]
    mejor = np.minimum(c_tur, np.minimum(c_lib, c_but))
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    out = {"E": E, "ahorro": actual - mejor, "libre_mejor": (c_lib < c_tur).astype(float), "mejor": mejor,
           "co2": E / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci"), "actual": actual}
    out.update({f"c_{k}": v for k, v in costes.items()})
    return out


KPIS = [
    {"id": "ahorro", "nombre": "Ahorro cambiando a la opción más barata", "unidad": "€/año", "clave": "ahorro", "tipo": "ahorro",
     "prob": ("Probabilidad de ahorrar", lambda v: v > 1)},
    {"id": "c_tur", "nombre": "Coste anual con la TUR", "unidad": "€/año", "clave": "c_tur", "tipo": "coste"},
    {"id": "c_libre", "nombre": "Coste anual en mercado libre", "unidad": "€/año", "clave": "c_libre", "tipo": "coste",
     },
    {"id": "c_butano", "nombre": "Coste anual con butano", "unidad": "€/año", "clave": "c_butano", "tipo": "coste"},
    {"id": "E", "nombre": "Consumo de gas estimado", "unidad": "kWh/año", "clave": "E"},
    {"id": "co2", "nombre": "CO₂ del gas natural", "unidad": "kg/año", "clave": "co2"},
]


def graficos(out, ctx):
    b = [mc.p10_50_90(out[f"c_{k}"]) for k in ALTERNATIVAS]
    return [{"tipo": "barras", "titulo": "Coste anual por suministro (P10–P90)", "ylabel": "€/año", "categorias": list(ALTERNATIVAS.values()),
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    return [{"Suministro": nombre, "P10 (€/año)": round(mc.p10_50_90(out[f"c_{k}"])[0]), "P50": round(mc.p10_50_90(out[f"c_{k}"])[1]),
             "P90": round(mc.p10_50_90(out[f"c_{k}"])[2]), "Prob. más barato": f"{float(np.mean(out[f'c_{k}'] <= np.minimum(np.minimum(out['c_tur'], out['c_libre']), out['c_butano']) + 1e-9)):.0%}"}
            for k, nombre in ALTERNATIVAS.items()]


def notas(out, ctx):
    return ["La TUR se revisa cada trimestre y el butano cada dos meses (BOE): los precios de referencia son los últimos publicados.",
            "El butano se compara por kWh de energía PCS; para calefacción no es una alternativa práctica.",
            "La oferta libre usa un precio típico de comparadores; un precio concreto puede editarse en Avanzado."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="ahorro", graficos=graficos, tabla=tabla, notas=notas)
