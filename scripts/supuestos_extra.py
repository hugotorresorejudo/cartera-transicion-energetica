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
S += [
    ("gas.umbral_tur1_kwh", 5000, "kWh/año", "Límite de consumo anual de la TUR1 (por encima se aplica la TUR2)."),
    ("gas.sg_precio", 1.10, "desviación geométrica", "Incertidumbre del precio del gas por las revisiones trimestrales de la TUR."),
    ("gas.factura_mes_eur", {"<20": R3(10, 15, 20), "20-40": R3(20, 30, 40), "40-80": R3(40, 60, 80), ">80": R3(80, 110, 180)}, "€/mes con impuestos",
     "Tramos de respuesta para la factura media mensual de gas."),
    ("gas.fijo_libre_ratio", R3(0.8, 1.0, 1.3), "×", "Término fijo de las ofertas libres respecto del de la TUR."),
    ("calefaccion.factor_scop_emisores", {"alta": 0.75, "media": 0.9, "suelo": 1.0}, "×", "Penalización del SCOP según temperatura de emisión (radiadores de alta temperatura, mixtos o suelo radiante)."),
    ("calefaccion.fraccion_uso_calefaccion", R3(0.5, 0.8, 1.0), "fracción", "Parte de la demanda de referencia que se atiende realmente (uso intermitente o parcial)."),
]
S += [
    ("calefaccion.sg_demanda", 1.4, "desviación geométrica", "Incertidumbre de la demanda de calefacción inferida (muy dependiente del edificio)."),
    ("calefaccion.potencia_extra_aerotermia_kw", R3(0, 1.15, 3.45), "kW", "Potencia contratada adicional necesaria al electrificar la calefacción desde gas."),
    ("calefaccion.uso", {"todo": R3(0.8, 1.0, 1.2), "tardes": R3(0.5, 0.7, 0.9), "ocasional": R3(0.2, 0.4, 0.6)}, "× demanda de referencia",
     "Uso real de la calefacción respecto de la demanda de referencia de la zona."),
    ("calefaccion.edad", {"pre1980": "pre-1980", "1980": "1980-2006", "2007": "2007+", "nose": "1980-2006"}, "-", "Respuesta de antigüedad -> clave de calefaccion.demanda_vs_anio_construccion."),
]
S += [
    ("cargador.p_min_gestion_kw", 1.4, "kW", "Potencia mínima de carga con gestión dinámica (6 A monofásico)."),
    ("cargador.p_base_noche_kw", R3(0.2, 0.4, 0.8), "kW", "Carga base nocturna de la vivienda durante la carga del VE."),
    ("cargador.confianza_horas", 0.95, "probabilidad", "Probabilidad mínima de completar la carga diaria dentro de la ventana de disponibilidad."),
    ("cargador.cuantil_potencia", 0.90, "probabilidad", "Cuantil de la potencia necesaria que se recomienda contratar (1 − probabilidad de corte)."),
    ("cargador.monofasico_max_kw", 7.4, "kW", "Potencia máxima de cargador en suministro monofásico."),
]
S += [
    ("cocina.rendimiento_vitro", R3(0.7, 0.75, 0.8), "fracción", "Rendimiento de una vitrocerámica radiante."),
    ("cocina.frecuencia", {"poco": R3(0.5, 0.7, 0.9), "normal": R3(0.9, 1.0, 1.1), "mucho": R3(1.1, 1.4, 1.8)}, "× consumo medio", "Frecuencia de cocinado."),
    ("cocina.menaje_eur", R3(0, 100, 300), "€", "Coste de menaje compatible con inducción si el actual no lo es."),
    ("cocina.vida_util", 15, "años", "Vida útil de la placa."),
    ("cocina.potencia_extra_kw", R3(0, 0, 2.3), "kW", "Potencia contratada adicional por pasar a inducción."),
    ("impuestos.ibi_cuota_media", R3(150, 350, 700), "€/año", "Cuota anual del IBI de una vivienda."),
    ("impuestos.icio_tipo", R3(0.02, 0.03, 0.04), "fracción de la obra", "Tipo del ICIO municipal."),
    ("ayudas.prob_convocatoria_abierta", {"si": 1.0, "no": 0.0, "nose": 0.3}, "probabilidad", "Probabilidad de que haya una convocatoria de ayudas directas abierta."),
    ("ayudas.prob_ordenanza", {"si": 1.0, "no": 0.0, "nose": 0.4}, "probabilidad", "Probabilidad de que el municipio bonifique IBI/ICIO/IVTM."),
    ("ayudas.prob_certificado_irpf", R3(0.3, 0.5, 0.8), "probabilidad", "Probabilidad de obtener el certificado de mejora energética que da acceso a la deducción IRPF."),
    ("ayudas.capex_envolvente_eur", R3(3000, 6000, 12000), "€", "Inversión típica en envolvente de una vivienda."),
    ("huella.vuelos_ano", {"ninguno": R3(0, 0, 0), "1-2": R3(1, 1.5, 2), "3-6": R3(3, 4, 6), ">6": R3(7, 9, 14)}, "vuelos de ida y vuelta/año", "Tramos de respuesta."),
    ("huella.tipo_vuelo_corto_fraccion", R3(0.4, 0.6, 0.8), "fracción", "Fracción de vuelos cortos/medios; el resto largos."),
    ("huella.km_dia_coche", {"<20": R3(8, 15, 20), "20-50": R3(20, 35, 50), "50-100": R3(50, 70, 100), ">100": R3(100, 120, 180)}, "km/día", "Tramos de respuesta."),
    ("huella.palanca_fv_kwp", 3, "kWp", "Instalación FV de referencia para la palanca de reducción."),
]
S += [
    ("ayudas.ivtm_anios", 5, "años", "Duración típica de la bonificación del IVTM."),
    ("ayudas.fraccion_bdc_vs_aerotermia", 0.5, "×", "Ayuda de la bomba de calor de ACS respecto de la de aerotermia."),
    ("ayudas.kwp_referencia", 4, "kWp", "Instalación FV de referencia en el cálculo de ayudas."),
    ("ayudas.kwh_bateria_referencia", 10, "kWh", "Batería de referencia en el cálculo de ayudas."),
]
