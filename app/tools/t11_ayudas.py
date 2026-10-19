"""T11 — Ayudas y deducciones: IRPF, IBI, ICIO, IVTM y ayudas directas (Next Generation y sucesoras)."""
from __future__ import annotations

import numpy as np

from core import montecarlo as mc
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref

ID = "t11"
NOMBRE = "Ayudas y deducciones"
DESCRIPCION = "Qué parte de la inversión recuperas por ayudas, IRPF y bonificaciones municipales."
MEDIDAS = {"fv": "Fotovoltaica", "bateria": "Batería", "aerotermia": "Aerotermia", "bdc": "Bomba de calor ACS", "envolvente": "Envolvente",
           "ve": "Vehículo eléctrico", "punto": "Punto de recarga"}
SI_NO = [("si", "Sí"), ("no", "No"), ("nose", "No lo sé")]


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("medidas", "¿Qué vas a hacer?", "multi", [(k, v) for k, v in MEDIDAS.items()], ["fv"]),
        Pregunta("propietario", "¿Eres propietario de la vivienda?", "select", [("si", "Sí"), ("no", "No")], "si"),
        Pregunta("irpf", "¿Presentas declaración de la renta?", "select", [("si", "Sí"), ("no", "No")], "si"),
        Pregunta("convocatoria", "¿Hay una convocatoria de ayudas directas abierta en tu comunidad?", "select", SI_NO, "nose"),
        Pregunta("ordenanza", "¿Tu ayuntamiento bonifica IBI, ICIO o IVTM?", "select", SI_NO, "nose"),
        Pregunta("cp", "Código postal", "texto", perfil="cp"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"medidas": ["fv"], "propietario": "si", "irpf": "si", "convocatoria": "nose", "ordenanza": "nose"}
    a.update(respuestas or {})
    D = mc.desde_rango
    kwp = r.get("ayudas.kwp_referencia")
    p = {}
    capex_wp = r.rango("fv.capex_residencial_eur_wp")
    inv = {"fv": D(tuple(x * kwp * 1000 for x in capex_wp)),
           "bateria": D(tuple(x * r.get("ayudas.kwh_bateria_referencia") for x in r.rango("almacenamiento.capex_bateria_eur_kwh"))),
           "aerotermia": D(r.rango("calefaccion.bdc_capex_aerotermia_eur")), "bdc": D(r.rango("acs.capex_bdc_acs_eur")),
           "envolvente": D(r.rango("ayudas.capex_envolvente_eur")), "ve": D(r.get("ve.precio_compra_ve_eur")["compacto"]),
           "punto": D(r.get("cargador.precio_wallbox_instalado_eur")["7.4"])}
    for m in a["medidas"]:
        p[f"I_{m}"] = Param(f"I_{m}", f"Inversión: {MEDIDAS[m]}", "€", inv[m])
    p["p_cert"] = Param("p_cert", "Probabilidad de obtener el certificado de mejora energética", "-", D(r.rango("ayudas.prob_certificado_irpf")))
    p["p_conv"] = Param("p_conv", "Probabilidad de ayuda directa disponible", "-", mc.fijo(r.sub("ayudas.prob_convocatoria_abierta", a["convocatoria"])))
    p["p_ord"] = Param("p_ord", "Probabilidad de bonificación municipal", "-", mc.fijo(r.sub("ayudas.prob_ordenanza", a["ordenanza"])))
    p["ibi_cuota"] = Param("ibi_cuota", "Cuota anual del IBI", "€/año", D(r.rango("impuestos.ibi_cuota_media")))
    p["icio_tipo"] = Param("icio_tipo", "Tipo del ICIO", "fracción", D(r.rango("impuestos.icio_tipo")))
    p["ivtm"] = Param("ivtm", "IVTM", "€/año", D(r.rango("impuestos.ivtm_medio_eur")))
    p["ibi_pct"] = Param("ibi_pct", "Bonificación del IBI", "fracción", D(r.get("deducciones.ibi_fv_bonificacion")["porcentaje"]))
    p["ibi_anios"] = Param("ibi_anios", "Años de bonificación del IBI", "años", D(r.get("deducciones.ibi_fv_bonificacion")["duracion_anios"]))
    p["icio_pct"] = Param("icio_pct", "Bonificación del ICIO", "fracción", D(r.rango("deducciones.icio_fv_bonificacion")))
    p["ivtm_pct"] = Param("ivtm_pct", "Bonificación del IVTM", "fracción", D(r.rango("ayudas.ivtm_bonificacion_ve")))
    return Parametros(p, {"perfil": perfil.to_dict(), "medidas": list(a["medidas"]), "propietario": a["propietario"], "irpf": a["irpf"]})


def modelo(S, ctx, rng):
    r = ref()
    n = len(S["p_cert"])
    kwp = r.get("ayudas.kwp_referencia")
    irpf = r.get("deducciones.irpf_autoconsumo")
    ve_d = r.get("ayudas.deduccion_irpf_ve")
    u_cert = rng.random(n) < S["p_cert"]
    u_conv = rng.random(n) < S["p_conv"]
    u_ord = rng.random(n) < S["p_ord"]
    es_prop = ctx["propietario"] == "si"
    es_irpf = ctx["irpf"] == "si"
    out = {}
    tot = {"directas": np.zeros(n), "irpf": np.zeros(n), "ibi": np.zeros(n), "icio": np.zeros(n), "ivtm": np.zeros(n)}
    inv_total = np.zeros(n)
    fila = {}
    for m in ctx["medidas"]:
        I = S[f"I_{m}"]
        if m in ("fv", "bateria"):
            direc = r.rango("ayudas.nextgen_autoconsumo")[1] * kwp * (1.0 if m == "fv" else 0.5)
        elif m == "aerotermia":
            direc = r.rango("ayudas.nextgen_aerotermia")[1]
        elif m == "bdc":
            direc = r.rango("ayudas.nextgen_aerotermia")[1] * r.get("ayudas.fraccion_bdc_vs_aerotermia")
        elif m == "envolvente":
            t = r.get("ayudas.rehabilitacion_envolvente")["ahorro_30"]
            direc = np.minimum(t["porcentaje"] * I, t["tope_eur_vivienda"])
        elif m == "ve":
            direc = r.rango("ayudas.nextgen_ve")[1]
        else:
            direc = np.zeros(n)
        direc = np.where(u_conv & es_prop if m != "ve" else u_conv, np.minimum(direc, I), 0.0)
        base = np.maximum(I - direc, 0)  # la ayuda directa reduce la base de la deducción
        if m in ("fv", "bateria", "aerotermia", "bdc"):
            ded = np.where(u_cert, irpf["mejora_consumo_energia_primaria_no_renovable"]["porcentaje"] * np.minimum(base, irpf["mejora_consumo_energia_primaria_no_renovable"]["limite_eur"]), 0.0)
        elif m == "envolvente":
            ded = np.where(u_cert, irpf["mejora_demanda_calefaccion_refrigeracion"]["porcentaje"] * np.minimum(base, irpf["mejora_demanda_calefaccion_refrigeracion"]["limite_eur"]), 0.0)
        elif m == "ve":
            ded = np.minimum(ve_d["compra_ve"]["porcentaje"] * np.minimum(base, r.get("ve.ayudas_compra")["base_maxima_eur"]), ve_d["compra_ve"]["limite_eur"])
        else:
            ded = np.minimum(ve_d["punto_recarga"]["porcentaje"] * base, ve_d["punto_recarga"]["limite_eur"])
        ded = np.where(es_irpf & es_prop if m not in ("ve", "punto") else es_irpf, ded, 0.0)
        ibi = S["ibi_cuota"] * S["ibi_pct"] * S["ibi_anios"] if m in ("fv", "bdc") else np.zeros(n)
        ibi = np.where(u_ord & es_prop, ibi, 0.0)
        icio = S["icio_tipo"] * I * S["icio_pct"] if m in ("fv", "bateria", "aerotermia", "bdc", "envolvente", "punto") else np.zeros(n)
        icio = np.where(u_ord & es_prop, icio, 0.0)
        ivtm = S["ivtm"] * S["ivtm_pct"] * r.get("ayudas.ivtm_anios") if m == "ve" else np.zeros(n)
        ivtm = np.where(u_ord, ivtm, 0.0)
        tot["directas"] += direc
        tot["irpf"] += ded
        tot["ibi"] += ibi
        tot["icio"] += icio
        tot["ivtm"] += ivtm
        inv_total += I
        fila[m] = {"inv": I, "ben": direc + ded + ibi + icio + ivtm}
    total = sum(tot.values())
    out.update({"total": total, "neta": inv_total - total, "pct": total / np.maximum(inv_total, 1.0) * 100, "inversion": inv_total,
                "_tot": {k: v for k, v in tot.items()}, "_fila": fila})
    for k, v in tot.items():
        out[f"b_{k}"] = v
    return out


KPIS = [
    {"id": "total", "nombre": "Ayudas y beneficios fiscales totales", "unidad": "€", "clave": "total", "tipo": "ahorro"},
    {"id": "pct", "nombre": "Parte de la inversión recuperada", "unidad": "%", "clave": "pct", "tipo": "ahorro", "fmt": "{:.0f}"},
    {"id": "neta", "nombre": "Inversión neta tras ayudas", "unidad": "€", "clave": "neta", "tipo": "coste"},
    {"id": "inversion", "nombre": "Inversión bruta", "unidad": "€", "clave": "inversion", "tipo": "coste"},
    {"id": "b_directas", "nombre": "Ayudas directas", "unidad": "€", "clave": "b_directas"},
    {"id": "b_irpf", "nombre": "Deducción IRPF", "unidad": "€", "clave": "b_irpf"},
    {"id": "b_ibi", "nombre": "Bonificación IBI", "unidad": "€", "clave": "b_ibi"},
    {"id": "b_icio", "nombre": "Bonificación ICIO", "unidad": "€", "clave": "b_icio"},
    {"id": "b_ivtm", "nombre": "Bonificación IVTM", "unidad": "€", "clave": "b_ivtm"},
]


def graficos(out, ctx):
    conc = [("Ayudas directas", "b_directas"), ("Deducción IRPF", "b_irpf"), ("IBI", "b_ibi"), ("ICIO", "b_icio"), ("IVTM", "b_ivtm")]
    b = [mc.p10_50_90(out[k]) for _, k in conc]
    return [{"tipo": "barras", "titulo": "Beneficio por concepto (P10–P90)", "ylabel": "€", "categorias": [c for c, _ in conc],
             "p10": [x[0] for x in b], "p50": [x[1] for x in b], "p90": [x[2] for x in b]}]


def tabla(out, ctx):
    filas = []
    for m, d in out["_fila"].items():
        i, b = mc.p10_50_90(d["inv"]), mc.p10_50_90(d["ben"])
        filas.append({"Medida": MEDIDAS[m], "Inversión P50 (€)": round(i[1]), "Beneficio P10": round(b[0]), "Beneficio P50": round(b[1]), "Beneficio P90": round(b[2])})
    return filas


def notas(out, ctx):
    return ["La disponibilidad de ayudas directas y de bonificaciones municipales es incierta y cambia por comunidad y ayuntamiento: se modela con probabilidades.",
            "Las deducciones del IRPF por eficiencia energética exigen certificado de eficiencia energética y son incompatibles con ayudas públicas sobre la misma base.",
            "Este resultado es orientativo y no sustituye la consulta de la convocatoria vigente, la ordenanza fiscal municipal ni a un asesor fiscal."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="total", graficos=graficos, tabla=tabla, notas=notas)
