"""T10 — Huella de carbono doméstica (electricidad, gas, butano, coche y vuelos) y palancas de reducción."""
from __future__ import annotations

import numpy as np

from core import clima, emisiones, fv, montecarlo as mc, perfiles_carga as pc, termico
from core.herramienta import Param, Parametros, Pregunta, ejecutar
from core.perfil import Perfil
from core.referencias import ref

ID = "t10"
NOMBRE = "Huella de carbono doméstica"
DESCRIPCION = "Emisiones anuales de tu hogar y qué palancas las reducen más."
FUENTES = {"elec": "Electricidad", "gas": "Gas natural", "butano": "Butano", "coche": "Coche", "vuelos": "Vuelos"}


def preguntas() -> list[Pregunta]:
    return [
        Pregunta("coche", "Tu coche", "select", [("ninguno", "No tengo"), ("gasolina", "Gasolina"), ("diesel", "Diésel"), ("hibrido", "Híbrido"), ("ve", "Eléctrico")], "gasolina"),
        Pregunta("km_dia", "Km típicos en un día laborable", "select", [("<20", "Menos de 20"), ("20-50", "20–50"), ("50-100", "50–100"), (">100", "Más de 100")], "20-50"),
        Pregunta("vuelos", "Vuelos de ida y vuelta al año", "select", [("ninguno", "Ninguno"), ("1-2", "1–2"), ("3-6", "3–6"), (">6", "Más de 6")], "1-2"),
        Pregunta("gas_usos", "Usos del gas natural", "multi", [("cocina", "Cocina"), ("acs", "Agua caliente"), ("calefaccion", "Calefacción")], []),
        Pregunta("butano", "¿Usas bombonas de butano?", "select", [("no", "No"), ("si", "Sí (1 cada 2 meses aprox.)")], "no"),
        Pregunta("vivienda", "Tipo y tamaño de vivienda", "select", [("piso_<70", "Piso <70 m²"), ("piso_70_120", "Piso 70–120 m²"), ("piso_>120", "Piso >120 m²"),
                                                                   ("unif_<120", "Unifamiliar <120 m²"), ("unif_>120", "Unifamiliar >120 m²")], perfil="vivienda"),
    ]


def inferir(perfil: Perfil, respuestas: dict | None = None) -> Parametros:
    r = ref()
    a = {"coche": "gasolina", "km_dia": "20-50", "vuelos": "1-2", "gas_usos": [], "butano": "no"}
    a.update(respuestas or {})
    D = mc.desde_rango
    p = dict(pc.inferir_componentes(perfil))
    usos = set(a["gas_usos"])
    npers = pc.n_personas(perfil)
    sg = r.get("perfil.sg_componente")
    eta = r.get("acs.rendimiento_calentador_gas")
    if "cocina" in usos:
        p["G_cocina"] = Param("G_cocina", "Gas para cocinar", "kWh/año", mc.logn(r.get("cocina.gas_consumo_kwh_ano_persona")[1] * npers, sg))
    if "acs" in usos:
        p["G_acs"] = Param("G_acs", "Gas para agua caliente", "kWh/año", mc.logn(pc.acs_util_cte_kwh(perfil) / eta[1], sg))
    if "calefaccion" in usos:
        d = pc.demanda_calefaccion_util(perfil)
        p["G_calefaccion"] = Param("G_calefaccion", "Gas para calefacción", "kWh/año",
                                   mc.logn(d[1] * r.get("calefaccion.fraccion_uso_calefaccion")[1] / r.get("calefaccion.caldera_gas_rendimiento_estacional_pcs")[1], r.get("calefaccion.sg_demanda")))
    if a["butano"] == "si":
        p["G_butano"] = Param("G_butano", "Butano", "kWh/año", mc.logn(r.get("gas.bombonas_ano_defecto") * r.get("gas.bombona_kg") * r.get("gas.butano_pcs"), r.get("gas.sg_butano")))
    km = D(r.sub("huella.km_dia_coche", a["km_dia"]))
    p["km_dia"] = Param("km_dia", "Km en día laborable", "km/día", km)
    p["km_fds"] = Param("km_fds", "Km de fines de semana", "km/año", D(r.rango("ve.km_fin_de_semana_ano")))
    p["vuelos"] = Param("vuelos", "Vuelos de ida y vuelta", "vuelos/año", D(r.sub("huella.vuelos_ano", a["vuelos"])))
    p["frac_corto"] = Param("frac_corto", "Fracción de vuelos cortos y medios", "-", D(r.rango("huella.tipo_vuelo_corto_fraccion")))
    p["f_avion"] = Param("f_avion", "Factor de emisión del avión", "kgCO₂/pasajero·km", D(r.rango("huella.factor_avion_kgco2_pkm")))
    p["ef_elec_fija"] = Param("ef_elec_fija", "Factor eléctrico fijo (0 = usar intensidad horaria)", "kgCO₂/kWh", mc.fijo(0))
    p["f_consumo"] = Param("f_consumo", "Factor global de consumo eléctrico", "-", mc.logn(1, r.get("tarifa.sg_f_consumo")))
    return Parametros(p, {"perfil": perfil.to_dict(), "coche": a["coche"]})


def modelo(S, ctx, rng):
    r = ref()
    perfil = Perfil.from_dict(ctx["perfil"])
    n = len(S["f_consumo"])
    npers = pc.n_personas(perfil)
    F = pc.formas_cached(perfil)
    ef8760 = emisiones.ef_anual_8760()
    esc, _ = pc.escala_factura(perfil, S, rng)
    escala = np.ones(n) if esc is None else esc
    ef_c = {c: float(F[c] @ ef8760) for c in F}
    fijo = S["ef_elec_fija"] > 0
    elec = np.zeros(n)
    for c in pc.COMPONENTES:
        if f"E_{c}" in S:
            ef = np.where(fijo, S["ef_elec_fija"], ef_c[c])
            elec += S[f"E_{c}"] * escala * S["f_consumo"] * ef
    pci = r.get("emisiones.gas_conversion_pcs_pci")
    gas = sum(S[k] for k in S if k.startswith("G_") and k != "G_butano") if any(k.startswith("G_") and k != "G_butano" for k in S) else np.zeros(n)
    gas_kg = gas / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci")
    but_kg = (S["G_butano"] / pci * r.get("emisiones.butano_kgco2_kwh_pci")) if "G_butano" in S else np.zeros(n)
    K = 52 * 5 * S["km_dia"] + S["km_fds"]
    ef_med = float(np.mean(emisiones.ef_mes_hora()))
    c = ctx["coche"]
    l100 = r.get("ice.consumo_l_100km")
    if c == "ninguno":
        coche = np.zeros(n)
    elif c in ("gasolina", "diesel"):
        ef_l = r.get("emisiones.pozo_a_rueda_diesel_kgco2_l" if c == "diesel" else "emisiones.pozo_a_rueda_gasolina_kgco2_l")
        coche = K * l100[c]["compacto"][1] * r.rango("ve.factor_consumo_real_vs_wltp")[1] / 100.0 * ef_l
    elif c == "hibrido":
        coche = K * l100["hibrido"]["compacto"][1] * r.rango("ve.factor_consumo_real_vs_wltp")[1] / 100.0 * r.get("emisiones.pozo_a_rueda_gasolina_kgco2_l")
    else:
        coche = K * r.get("ve.consumo_wltp_kwh_100km")["compacto"][1] * r.rango("ve.factor_consumo_real_vs_wltp")[1] / 100.0 / r.rango("ve.eficiencia_carga_domestica")[1] * ef_med
    vk = r.get("huella.vuelos_tipicos_km")
    km_vuelo = S["frac_corto"] * 0.5 * (vk["corto"] + vk["medio"]) + (1 - S["frac_corto"]) * vk["largo"]
    vuelos = S["vuelos"] * 2 * km_vuelo * S["f_avion"]  # ida y vuelta, por pasajero; se multiplica por viajeros adultos
    vuelos = vuelos * max(1.0, min(npers, 2.0))
    total = elec + gas_kg + but_kg + coche + vuelos
    # palancas (kg/año evitados): FV de referencia, cambio de coche a VE, ACS de gas a bomba de calor, un vuelo menos
    yield_kwp = float(clima.pv_normalizado(perfil.cp, 0, r.get("huella.palanca_fv_inclinacion")).sum())
    palanca_fv = r.get("huella.palanca_fv_kwp") * yield_kwp * 0.5 * np.maximum(ef_med, 0)  # la mitad se autoconsume
    ev_kg = K * r.get("ve.consumo_wltp_kwh_100km")["compacto"][1] * r.rango("ve.factor_consumo_real_vs_wltp")[1] / 100.0 / r.rango("ve.eficiencia_carga_domestica")[1] * ef_med
    palanca_ve = np.maximum(coche - ev_kg, 0) if c in ("gasolina", "diesel", "hibrido") else np.zeros(n)
    palanca_acs = np.maximum(((S["G_acs"] / pci * r.get("emisiones.gas_natural_kgco2_kwh_pci")) - (S["G_acs"] * r.get("acs.rendimiento_calentador_gas")[1]) / r.rango("acs.bdc_cop_nominal_acs")[1] * ef_c["acs"]), 0) if "G_acs" in S else np.zeros(n)
    palanca_vuelo = vuelos / np.maximum(S["vuelos"], 1e-9) if c is not None else np.zeros(n)
    palanca_vuelo = np.where(S["vuelos"] > 0, vuelos / np.maximum(S["vuelos"], 1e-9), 0.0)
    return {"total": total / 1000.0, "pers": total / 1000.0 / npers, "elec": elec, "gas": gas_kg, "butano": but_kg, "coche": coche, "vuelos": vuelos,
            "vs_media": total / 1000.0 / r.rango("huella.media_hogar_espana_tco2")[1] * 100,
            "arboles": total / r.rango("huella.arboles_absorcion_kgco2_ano")[1],
            "pal_fv": palanca_fv, "pal_ve": palanca_ve, "pal_acs": palanca_acs, "pal_vuelo": palanca_vuelo}


KPIS = [
    {"id": "total", "nombre": "Huella anual del hogar", "unidad": "t CO₂e/año", "clave": "total", "tipo": "coste", "fmt": "{:.2f}"},
    {"id": "pers", "nombre": "Huella por persona", "unidad": "t CO₂e/año", "clave": "pers", "fmt": "{:.2f}"},
    {"id": "vs_media", "nombre": "Frente a la media de un hogar en España", "unidad": "%", "clave": "vs_media", "fmt": "{:.0f}"},
    {"id": "arboles", "nombre": "Árboles necesarios para absorberla", "unidad": "árboles", "clave": "arboles"},
]


def graficos(out, ctx):
    ks = list(FUENTES)
    b = {k: mc.p10_50_90(out[k]) for k in ks}
    return [{"tipo": "barras", "titulo": "Emisiones por fuente (P10–P90)", "ylabel": "kg CO₂e/año", "categorias": [FUENTES[k] for k in ks],
             "p10": [b[k][0] for k in ks], "p50": [b[k][1] for k in ks], "p90": [b[k][2] for k in ks]}]


def tabla(out, ctx):
    pal = [("Instalar 3 kWp de FV", "pal_fv"), ("Cambiar el coche a eléctrico", "pal_ve"), ("Pasar el ACS de gas a bomba de calor", "pal_acs"),
           ("Un vuelo menos al año", "pal_vuelo")]
    return [{"Palanca": nombre, "Reducción P50 (kg CO₂e/año)": round(mc.p10_50_90(out[k])[1]), "P10": round(mc.p10_50_90(out[k])[0]),
             "P90": round(mc.p10_50_90(out[k])[2])} for nombre, k in pal]


def notas(out, ctx):
    return ["Electricidad con la intensidad horaria real del sistema (REData) ponderada por cuándo consumes; con un contrato sin garantía de origen "
            "el factor de comercializadora sería mayor (en Avanzado puedes fijar el factor).",
            "Coche: emisiones del pozo a la rueda. Vuelos: factor por pasajero-km sin efectos de forzamiento radiativo."]


def calcular(parametros: Parametros, n_mc: int = 500, seed: int = mc.SEMILLA):
    return ejecutar(ID, parametros, modelo, KPIS, n_mc, seed, tornado_kpi="total", graficos=graficos, tabla=tabla, notas=notas)
