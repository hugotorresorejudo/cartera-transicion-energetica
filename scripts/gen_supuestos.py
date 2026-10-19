#!/usr/bin/env python3
"""Genera docs/refs/supuestos.yaml: hipótesis de modelado del autor (verificado: false) que no son datos de una fuente.

Cada tupla: (clave, valor, unidad, nota). Re-ejecutar y luego scripts/merge_refs.py."""
from pathlib import Path

import yaml

R = lambda a, b, c: [a, b, c]  # noqa: E731
ONES = [1.0] * 24

S = [
    # --- perfil del hogar
    ("perfil.personas", {"1": R(1, 1, 1), "2": R(2, 2, 2), "3-4": R(3, 3.5, 4), "5+": R(5, 5, 6)}, "personas",
     "Respuesta cualitativa traducida a rango numérico."),
    ("perfil.superficie_m2", {"piso_<70": R(40, 60, 70), "piso_70_120": R(70, 90, 120), "piso_>120": R(120, 140, 200),
                              "unif_<120": R(80, 100, 120), "unif_>120": R(120, 160, 250)}, "m²",
     "Superficie útil por tramo de respuesta; el valor central es el punto medio aproximado del tramo."),
    ("perfil.factura_mes_eur", {"<40": R(20, 32, 40), "40-70": R(40, 55, 70), "70-120": R(70, 95, 120), ">120": R(120, 150, 230)},
     "€/mes con impuestos", "Tramos de respuesta de la pregunta de la factura media mensual."),
    ("perfil.sg_prior_consumo", 1.35, "desviación geométrica", "Incertidumbre del consumo anual sin dato de factura."),
    ("perfil.sg_factura", 1.12, "desviación geométrica", "Incertidumbre del consumo anual inferido de un tramo de factura."),
    ("perfil.sg_componente", 1.25, "desviación geométrica", "Dispersión de cada componente del consumo."),
    ("perfil.t_base_calefaccion_c", 15, "ºC", "Temperatura base para repartir la calefacción eléctrica en el año."),
    ("perfil.t_base_refrigeracion_c", 24, "ºC", "Temperatura base para repartir la refrigeración en el año."),
    ("perfil.ve_km_dia", R(15, 35, 70), "km/día", "Uso por defecto del VE en el perfil si no se ha hecho T04."),
    ("perfil.piscina_horas_dia", R(4, 6, 8), "h/día", "Horas de depuración."),
    ("perfil.piscina_dias", R(120, 180, 240), "días/año", "Temporada de piscina."),
    ("perfil.exponente_personas", 0.6, "-", "El consumo de actividad escala con (personas/2,5)^exponente."),
    ("perfil.personas_referencia", 2.5, "personas", "Hogar medio de referencia (INE)."),
    ("perfil.acs_duchas_persona_dia", R(0.8, 1.0, 1.3), "duchas/persona·día", "Uso por defecto para el consumo eléctrico del termo."),
    ("perfil.acs_ducha_min", R(4, 7, 10), "min", "Duración por defecto de ducha."),
    ("perfil.estacionalidad_actividad", [1.12, 1.08, 1.03, 1.0, 0.97, 0.95, 0.95, 0.95, 0.98, 1.03, 1.08, 1.12], "-",
     "Iluminación y uso interior algo mayores en invierno."),
    # --- formas horarias normalizables
    ("forma.actividad_fuera", [.4, .35, .3, .3, .3, .4, .9, 1.4, 1, .5, .4, .4, .5, .5, .5, .5, .6, .9, 1.3, 1.8, 2, 1.9, 1.4, .8], "-",
     "Forma diaria laborable de la actividad eléctrica general con la casa vacía en horario laboral."),
    ("forma.actividad_parcial", [.4, .35, .3, .3, .3, .4, .8, 1.2, 1.1, 1, 1, 1, 1.1, 1.1, 1, .9, .9, 1, 1.3, 1.6, 1.8, 1.7, 1.3, .7], "-",
     "Teletrabajo parcial."),
    ("forma.actividad_casa", [.4, .35, .3, .3, .3, .4, .7, 1, 1.1, 1.2, 1.2, 1.2, 1.3, 1.4, 1.2, 1.1, 1.1, 1.1, 1.3, 1.5, 1.7, 1.6, 1.2, .7], "-",
     "Casi siempre en casa."),
    ("forma.actividad_finde", [.4, .35, .3, .3, .3, .3, .5, .7, 1, 1.3, 1.4, 1.4, 1.5, 1.5, 1.3, 1.2, 1.2, 1.2, 1.4, 1.6, 1.7, 1.6, 1.2, .7], "-",
     "Fines de semana y festivos."),
    ("forma.cocina", [0, 0, 0, 0, 0, 0, .2, .5, .4, .2, .3, .8, 1.6, 1.8, .8, .3, .3, .4, .7, 1.5, 1.9, 1.2, .4, .1], "-", "Picos de comida y cena."),
    ("forma.acs", [.1, .05, .05, .05, .1, .4, 1.6, 2, 1.2, .6, .4, .4, .5, .5, .4, .4, .5, .7, 1, 1.2, 1.4, 1.5, .9, .3], "-", "Duchas mañana y noche."),
    ("forma.calefaccion", [.6, .5, .5, .5, .6, .9, 1.6, 1.6, 1.1, .7, .6, .6, .7, .7, .6, .6, .8, 1.2, 1.5, 1.7, 1.7, 1.5, 1.2, .8], "-", "Calefacción eléctrica."),
    ("forma.refrigeracion", [.8, .6, .5, .4, .4, .4, .4, .4, .5, .6, .8, 1, 1.3, 1.5, 1.6, 1.7, 1.7, 1.6, 1.5, 1.4, 1.4, 1.3, 1.1, .9], "-", "Refrigeración."),
    ("forma.ve_casa", [1.2, 1.2, 1.1, 1, .9, .6, .2, 0, 0, 0, 0, 0, 0, 0, 0, 0, .1, .4, .9, 1.5, 1.8, 1.8, 1.6, 1.4], "-",
     "Carga doméstica 'conectar al llegar' sin gestión."),
    ("forma.piscina", [0, 0, 0, 0, 0, 0, 0, .2, .8, 1.2, 1.4, 1.4, 1.4, 1.4, 1.4, 1.2, .8, .4, .2, 0, 0, 0, 0, 0], "-", "Depuradora diurna."),
    ("forma.plana", ONES, "-", "Cargas continuas (nevera, standby)."),
    # --- simultaneidad y potencia
    ("simultaneidad.prob_pico_diario", {"induccion": .10, "horno": .05, "termo_electrico": .12, "aire_acondicionado": .30,
                                        "calefaccion_electrica": .35, "ve": .40, "piscina": .20, "lavadora": .03,
                                        "lavavajillas": .03, "secadora": .015, "plancha": .02, "microondas": .05}, "prob./día",
     "Probabilidad de que cada aparato esté en marcha en el cuarto de hora de máxima demanda de un día con uso."),
    ("simultaneidad.potencia_efectiva_kw", {"induccion": R(1.0, 2.2, 4.0), "horno": R(1.2, 1.8, 2.4), "termo_electrico": R(1.2, 1.5, 2.0),
                                            "aire_acondicionado": R(0.5, 1.0, 2.0), "calefaccion_electrica": R(1.0, 2.0, 4.0),
                                            "ve": R(3.7, 3.7, 7.4), "piscina": R(0.4, 0.75, 1.0), "lavadora": R(0.4, 0.9, 2.0),
                                            "lavavajillas": R(0.5, 1.0, 2.0), "secadora": R(0.8, 1.5, 2.5), "plancha": R(0.8, 1.5, 2.2),
                                            "microondas": R(0.6, 1.0, 1.4)}, "kW",
     "Potencia media efectiva en 15 min de cada aparato (inferior a la nominal por ciclado y uso parcial de zonas)."),
    ("simultaneidad.dias_activos", {"aire_acondicionado": 120, "calefaccion_electrica": 110, "piscina": 150}, "días/año",
     "Días de uso estacional; el resto de aparatos se supone todo el año."),
    ("simultaneidad.base_kw", R(0.25, 0.5, 1.0), "kW", "Carga base simultánea (nevera, iluminación, TV, ordenador)."),
    ("simultaneidad.dias_exceso_limitador", {"nunca": R(0, 0, 0), "alguna": R(1, 3, 6), "a_menudo": R(7, 20, 60)}, "días/año",
     "Respuesta '¿salta el limitador?' traducida a días con corte."),
    ("tarifa.alpha_corte", 0.10, "probabilidad", "Probabilidad anual admisible de que la demanda máxima supere la potencia contratada."),
    ("tarifa.ratio_periodos_fija", {"P1": 1.25, "P2": 1.0, "P3": 0.75}, "-",
     "Ofertas con precio por periodo: relación respecto al precio único típico."),
    ("tarifa.sg_precio_nivel", 1.0, "-", "Reservado."),
    ("tarifa.dias_anio", 365, "días", "Año de facturación."),
]

salida = {}
for clave, valor, unidad, nota in S:
    salida[clave] = {"valor": valor, "unidad": unidad, "fuente": "Supuesto del autor (hipótesis de modelado)", "url": "",
                     "fecha_consulta": "2026-10-19", "verificado": False, "nota": nota}

if __name__ == "__main__":
    import importlib.util, sys
    ruta = Path(__file__).resolve().parent.parent / "docs" / "refs"
    ruta.mkdir(parents=True, exist_ok=True)
    extra = ruta.parent.parent / "scripts" / "supuestos_extra.py"
    if extra.exists():
        spec = importlib.util.spec_from_file_location("supuestos_extra", extra)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for clave, valor, unidad, nota in m.S:
            salida[clave] = {"valor": valor, "unidad": unidad, "fuente": "Supuesto del autor (hipótesis de modelado)",
                             "url": "", "fecha_consulta": "2026-10-19", "verificado": False, "nota": nota}
    (ruta / "supuestos.yaml").write_text(yaml.safe_dump(salida, allow_unicode=True, sort_keys=True, width=120), encoding="utf-8")
    print(len(salida), "supuestos")
