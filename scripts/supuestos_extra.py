"""Supuestos adicionales (se fusionan en gen_supuestos.py)."""
R3 = lambda a, b, c: [a, b, c]  # noqa: E731
S = [
    ("perfil.fraccion_superficie_climatizada_refrig", [0.25, 0.4, 0.7], "fracción", "Parte de la vivienda que se refrigera con aire acondicionado."),
    ("perfil.meses_piscina", [4, 5, 6, 7, 8], "meses (0=enero)", "Mayo a septiembre."),
    ("perfil.edad_vivienda_defecto", "1980-2006", "-", "Tramo de antigüedad por defecto para escalar la demanda térmica."),
]
S += [
    ("tarifa.sg_f_consumo", 1.05, "desviación geométrica", "Incertidumbre residual del consumo anual (factor global)."),
    ("tarifa.sg_f_omie", 1.15, "desviación geométrica", "Incertidumbre del nivel medio del precio OMIE respecto del histórico."),
    ("tarifa.potencia_sin_dato", [3, 4, 5], "índices de tarifa.potencias_normalizadas", "Rango de potencia contratada probable si el usuario responde 'no sé' (mínimo, moda, máximo)."),
    ("tarifa.pmax_muestras", 500, "muestras", "Muestras de simultaneidad para la demanda máxima."),
]
S += [
    ("fv.inclinacion_muy_inclinada", [30, 35, 45], "grados", "Cubierta muy inclinada (>25º)."),
    ("fv.economia_escala_exponente", -0.12, "-", "CAPEX unitario ∝ (P/P_ref)^exponente: instalaciones pequeñas son más caras por Wp."),
    ("fv.potencia_capex_ref_kwp", 4, "kWp", "Potencia de referencia del rango de CAPEX €/Wp."),
    ("fv.n_candidatos", 8, "-", "Potencias candidatas en el dimensionado."),
    ("fv.n_muestras_dimensionado", 100, "muestras", "Muestras Monte Carlo usadas en la curva VAN(P_p)."),
    ("fv.horizonte_anios", 25, "años", "Horizonte de evaluación prudente (inferior a la vida útil del módulo)."),
    ("fv.plazas_tamano", {"1": [1, 1, 1], "2": [2, 2, 2], "3+": [3, 3.5, 5], "nose": [1, 2, 3]}, "plazas de garaje",
     "Tamaño útil del tejado expresado en plazas de garaje."),
    ("fv.paso_cuantizacion_az", 15, "grados", "Cuantización de azimut para reutilizar curvas PVGIS."),
    ("fv.paso_cuantizacion_incl", 5, "grados", "Cuantización de inclinación."),
    ("fv.ratio_scop_aerotermia_prevision", 1.0, "-", "Reservado."),
]
S += [
    ("omie.umbral_precio_bajo", 0, "€/MWh", "Umbral por defecto para contar horas con precio no positivo."),
    ("omie.n_spread_horas", 4, "horas", "Ventana por defecto del spread diario."),
    ("omie.dias_semana", 7, "días", "Longitud del bloque del bootstrap por ventana."),
    ("omie.ventana_dias", {"semana": 7, "mes": 30, "anio": 365}, "días", "Ventanas de la vista simple."),
    ("omie.tilt_mi_fv", 30, "º", "Inclinación de 'mi FV' en el explorador si no se ha hecho T02."),
]
S += [
    ("ve.horarios", {"a": [17, 8], "b": [19, 8], "c": [21, 7], "d": [19, 10]}, "[hora de llegada, hora de salida]",
     "Franjas de respuesta: a) llego ~17 h y salgo ~8 h; b) ~19 h/~8 h; c) ~21 h/~7 h; d) ~19 h/~10 h."),
    ("ve.km_laborable", {"<20": R3(8, 15, 20), "20-50": R3(20, 35, 50), "50-100": R3(50, 70, 100), ">100": R3(100, 120, 180)}, "km/día",
     "Tramos de respuesta de km en un día laborable."),
    ("ve.viajes_largos", {"ninguno": R3(0, 0, 0), "1-5": R3(1, 3, 5), "6-15": R3(6, 10, 15), ">15": R3(15, 22, 35)}, "viajes/año",
     "Tramos de respuesta de viajes largos."),
    ("ve.anios_tenencia", {"3-5": 4, "6-9": 8, "10+": 11}, "años", "Años de tenencia por tramo (valor central)."),
    ("ve.potencia_cargador_kw", {"garaje_propio": 7.4, "garaje_comunitario": 3.7, "calle": 3.7}, "kW",
     "Potencia de cargador doméstico supuesta por tipo de aparcamiento."),
    ("ve.laborables_semana", 5, "días/semana", "Días laborables por semana para anualizar los km."),
    ("ve.f_ayuda", [0, 0.5, 1], "fracción", "Fracción de la deducción IRPF por compra de VE efectivamente aprovechada."),
    ("ve.sg_precio_energia", 1.0, "-", "Reservado."),
]
S += [
    ("acs.duchas_persona_dia", {"<1": R3(0.4, 0.6, 0.9), "1": R3(0.9, 1.0, 1.1), ">1": R3(1.2, 1.5, 2.0)}, "duchas/persona·día", "Tramos de respuesta."),
    ("acs.banera_freq_dia", {"nunca": R3(0, 0, 0), "semanal": R3(0.1, 0.143, 0.2), "diario": R3(0.7, 1.0, 1.0)}, "baños/día", "Tramos de respuesta."),
    ("acs.volumenes_comerciales_l", [50, 80, 100, 150, 200, 300], "L", "Volúmenes comerciales de depósito."),
    ("acs.dt_ref_perdidas_k", 45, "K", "Salto de temperatura al que se refieren las pérdidas en espera tabuladas."),
    ("acs.t_interior_c", R3(18, 20, 23), "ºC", "Temperatura de un cuarto interior de la vivienda."),
    ("acs.bdc_potencia_electrica_kw", R3(0.4, 0.5, 0.7), "kW", "Potencia eléctrica del compresor de una bomba de calor de ACS."),
    ("gas.bombona_kg", 12.5, "kg", "Contenido de la bombona de butano doméstica."),
    ("gas.cuota_fija_evitable", R3(0, 0, 0), "€/año", "Cuota fija de gas que se evita al abandonar el gas (0 si quedan otros usos de gas)."),
    ("acs.horas_deposito_tipo", 24, "h", "Horizonte diario de la programación."),
]
S += [
    ("almacenamiento.reposicion_factor", 0.6, "fracción del CAPEX", "Coste de reponer la batería al final de su vida respecto del CAPEX inicial (bajada de precios)."),
    ("almacenamiento.capacidades_candidatas_kwh", [0, 5, 10, 15], "kWh", "Capacidades evaluadas en el dimensionado de la batería (0 = sin batería)."),
    ("almacenamiento.dim_fv_factor", 1.0, "-", "La FV de partida de T06 cubre este múltiplo del consumo anual (limitada por el área disponible)."),
    ("almacenamiento.n_muestras_dimensionado", 60, "muestras", "Muestras Monte Carlo para la curva VAN(capacidad)."),
]
