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
S += [
    ("desplazamiento.horas_habituales", {"manana": [8, 9, 10, 11], "tarde": [15, 16, 17, 18], "noche": [20, 21, 22], "cuando": [9, 13, 19, 21]}, "horas del día",
     "Horas habituales en que se pone el aparato."),
    ("desplazamiento.ventanas", {"noche": [23, 0, 1, 2, 3, 4, 5, 6, 7], "solar": [10, 11, 12, 13, 14, 15, 16, 17], "cualquiera": list(range(24))}, "horas del día",
     "Horas en que se acepta poner el aparato."),
    ("desplazamiento.ciclo_aparato", {"lavadora": "lavadora_eco_40_60", "lavavajillas": "lavavajillas_eco", "secadora": "secadora_bomba_calor"}, "-",
     "Ciclo de referencia de cada aparato en electrodomesticos.ciclo_energia_kwh."),
    ("desplazamiento.usos_semana_termo", 7, "usos/semana", "El termo calienta cada día; su desplazamiento programa el calentamiento."),
    ("desplazamiento.kwh_dia_termo_defecto", R3(2.5, 3.5, 5), "kWh/día", "Energía diaria del termo eléctrico si no se conoce."),
]
S += [
    ("emisiones.carga_desplazable_kwh_dia", R3(1, 3, 8), "kWh/día", "Energía diaria desplazable para evaluar la reducción de emisiones (lavado + termo + carga)."),
    ("emisiones.estaciones", {"todo": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "invierno": [10, 11, 0, 1, 2], "verano": [5, 6, 7, 8]}, "meses (0=enero)", "Meses de cada estación."),
]
S += [
    ("refrigeracion.fraccion_estancias", {"1": R3(0.1, 0.15, 0.2), "2": R3(0.2, 0.3, 0.4), "3-4": R3(0.4, 0.6, 0.8), "toda": R3(0.9, 1.0, 1.0)}, "fracción de la superficie",
     "Parte de la vivienda climatizada según estancias."),
    ("refrigeracion.uso", {"poco": R3(0.4, 0.6, 0.8), "medio": R3(0.8, 1.0, 1.2), "mucho": R3(1.2, 1.5, 2.0)}, "× demanda de referencia", "Uso del aire acondicionado."),
    ("refrigeracion.factor_soleada", {"si": R3(1.1, 1.3, 1.6), "no": R3(0.8, 1.0, 1.1)}, "×", "Vivienda muy soleada (orientación y falta de protección solar)."),
    ("refrigeracion.seer_antiguo", R3(2.5, 3.2, 4.0), "SEER", "Equipo antiguo sin inverter."),
    ("refrigeracion.factor_seer_real", R3(0.7, 0.8, 0.9), "×", "SEER de campo respecto del de etiqueta."),
    ("refrigeracion.factor_reversible", R3(0.9, 0.95, 1.0), "×", "SEER de un multisplit reversible respecto del split individual."),
    ("refrigeracion.capex_reversible_factor", R3(1.1, 1.25, 1.5), "× por estancia", "Sobrecoste de un equipo reversible frente a un split solo frío."),
    ("refrigeracion.vida_util", 15, "años", "Vida útil de un split."),
    ("refrigeracion.estancias_equipos", {"1": 1, "2": 2, "3-4": 3, "toda": 4}, "equipos", "Número de splits o unidades interiores."),
    ("refrigeracion.potencia_electrica_eer", R3(2.8, 3.3, 4.0), "EER", "Relación potencia frigorífica/eléctrica a plena carga para el pico."),
]
S += [
    ("electrodomesticos.factor_edad", {"nuevos": R3(0.7, 0.8, 0.9), "medios": R3(0.9, 1.0, 1.1), "antiguos": R3(1.1, 1.3, 1.6)}, "× consumo medio", "Antigüedad de los electrodomésticos."),
    ("electrodomesticos.horas_tv", {"<2": R3(1, 1.5, 2), "2-4": R3(2, 3, 4), ">4": R3(4, 5.5, 8)}, "h/día", "Tramos de respuesta de horas de TV."),
    ("electrodomesticos.horas_tv_referencia", 3, "h/día", "Horas de TV a las que se refiere el consumo anual tabulado."),
    ("electrodomesticos.factor_standby", {"si": R3(0.4, 0.5, 0.7), "aveces": R3(0.8, 1.0, 1.2), "no": R3(1.2, 1.5, 2.0)}, "× stand-by medio", "¿Apagas del todo los aparatos?"),
    ("electrodomesticos.n_tv", {"1": 1, "2": 2, "3+": 3}, "unidades", "Número de televisores."),
]
S += [
    ("lcoe.tecnologias", {"solar_fv_utility": "FV a gran escala", "solar_fv_residencial": "FV residencial", "eolica_terrestre": "Eólica terrestre",
                          "eolica_marina": "Eólica marina", "ciclo_combinado": "Ciclo combinado", "nuclear_existente_ampliacion": "Nuclear (nueva o ampliación)",
                          "hidraulica_bombeo": "Bombeo"}, "-", "Nombres de las tecnologías del explorador de LCOE."),
    ("lcoe.escenario_gas", {"bajo": 0, "medio": 1, "alto": 2}, "índice del rango", "Escenario de precio del gas y del CO₂ (mínimo, moda, máximo del rango de referencia)."),
    ("lcoe.factor_wacc", {"bajo": 0.8, "medio": 1.0, "alto": 1.25}, "×", "Escenario de coste de capital sobre el WACC de referencia."),
    ("lcoe.mwh_por_kw_mwh", 8.76, "MWh/kW·año a FC=1", "Horas anuales / 1000."),
    ("lcoe.perfil_captura", {"solar_fv_utility": "solar", "solar_fv_residencial": "solar", "eolica_terrestre": "lica", "eolica_marina": "lica"}, "-", "Columna de REData para el precio capturado de cada tecnología."),
]
S += [
    ("curvas.horas", {"madrugada": 4, "mediodia": 14, "noche": 21}, "hora del día", "Franjas representativas de las curvas almacenadas."),
    ("curvas.meses", {"invierno": [12, 1, 2], "primavera": [3, 4, 5], "verano": [6, 7, 8], "otono": [9, 10, 11]}, "meses", "Estaciones."),
    ("curvas.choque_gas", {"ninguno": 1.0, "mas50": 1.5, "mas100": 2.0, "menos30": 0.7}, "× precio del gas", "Choque de precio del gas."),
    ("curvas.choque_renovable", {"ninguno": 1.0, "menos25": 0.75, "menos50": 0.5, "mas25": 1.25}, "× disponibilidad solar y eólica", "Choque de disponibilidad renovable."),
    ("curvas.sg_renovable", 1.2, "desviación geométrica", "Variabilidad de la disponibilidad renovable entre días."),
    ("curvas.sd_demanda", 0.03, "fracción", "Variabilidad de la demanda entre días."),
    ("curvas.tecnologias_gas", ["Ciclo combinado", "Cogeneración", "Carbón y otras"], "-", "Tecnologías cuyo precio de oferta sigue al del gas y el CO₂."),
    ("curvas.tecnologias_renovables", ["Solar FV", "Eólica"], "-", "Tecnologías afectadas por el choque de disponibilidad renovable."),
    ("curvas.precio_techo", 400, "€/MWh", "Precio de la última unidad si la oferta no cubre la demanda (reserva)."),
]
S += [
    ("solar_termica.pr_fv_proxy", 0.80, "-", "Rendimiento global del sistema FV de PVGIS usado para recuperar la irradiancia sobre el plano inclinado a partir de la producción por kWp."),
    ("solar_termica.eta_sistema", R3(0.7, 0.8, 0.9), "-", "Rendimiento de tuberías, intercambio y acumulación del sistema solar."),
    ("solar_termica.t_colector_c", R3(40, 50, 65), "ºC", "Temperatura media del fluido en el captador."),
    ("solar_termica.sg_demanda", 1.25, "desviación geométrica", "Incertidumbre de la demanda de ACS."),
    ("solar_termica.n_captadores", {"1": 1, "2": 2, "3+": 3}, "captadores", "Número de captadores."),
    ("solar_termica.umbral_g_kw_m2", 0.05, "kW/m²", "Irradiancia mínima para que el captador aporte energía."),
]
S += [
    ("envolvente.factor_ahorro_edad", {"pre1980": 1.15, "1980": 1.0, "2007": 0.5}, "×", "Potencial de ahorro de las medidas según la antigüedad del edificio."),
    ("envolvente.pisos_unifamiliar", 1.5, "plantas", "Plantas medias de una unifamiliar (superficie de cubierta = superficie útil / plantas)."),
    ("envolvente.cop_electrica", 1.0, "-", "Rendimiento de los radiadores eléctricos."),
    ("envolvente.tipos_edificio", {"intermedio": "piso_intermedio", "ultima": "piso_ultima_o_esquina", "adosada": "unifamiliar_adosada", "aislada": "unifamiliar_aislada"}, "-",
     "Respuesta de tipo de edificio -> clave de envolvente.superficie_fachada_ratio."),
    ("envolvente.tiene_cubierta", {"intermedio": 0, "ultima": 1, "adosada": 1, "aislada": 1}, "0/1", "El edificio tiene cubierta propia aislable."),
    ("envolvente.umbrales_ahorro", {"ahorro_60": 0.6, "ahorro_45": 0.45, "ahorro_30": 0.3}, "fracción", "Umbrales de reducción de la demanda que dan acceso a cada nivel de ayuda de rehabilitación."),
    ("envolvente.horizonte_max", 40, "años", "Horizonte máximo de evaluación."),
]
S += [
    ("comunidad.mezcla_ocupacion", {"fuera": [0.6, 0.3, 0.1], "mixto": [0.35, 0.35, 0.3], "casa": [0.1, 0.3, 0.6]}, "probabilidades [fuera, parcial, casa]", "Mezcla de patrones de ocupación de los vecinos."),
    ("comunidad.vecinos", {"<=10": 8, "11-30": 20, ">30": 50}, "vecinos", "Número de participantes representativo de cada tramo."),
    ("comunidad.kwp_por_vecino", {"pequena": R3(0.4, 0.5, 0.6), "media": R3(0.8, 1.0, 1.2), "grande": R3(1.4, 1.8, 2.2)}, "kWp/vecino", "Tamaño de la instalación por participante."),
    ("comunidad.n_simulados", 8, "participantes", "Número de participantes distintos simulados (representan a toda la comunidad)."),
    ("comunidad.n_max_mc", 120, "muestras", "Máximo de muestras Monte Carlo de esta herramienta (coste de cálculo)."),
    ("comunidad.sg_consumo_vecino", 1.35, "desviación geométrica", "Dispersión del consumo anual entre vecinos."),
    ("comunidad.horizonte_anios", 25, "años", "Horizonte de evaluación."),
    ("comunidad.reparto", {"igual": "Coeficiente estático igual", "consumo": "Coeficiente estático por consumo", "dinamico": "Coeficiente dinámico horario"}, "-", "Tipos de coeficiente de reparto."),
]
S += [
    ("gas.banda_bombona", R3(0.92, 1.0, 1.08), "× precio de referencia", "Rango del precio de la bombona de butano alrededor del último precio publicado (revisión bimestral limitada por regulación)."),
    ("gas.banda_variable", R3(0.9, 1.0, 1.2), "× precio de referencia", "Rango del término variable del gas entre la TUR y las ofertas libres."),
    ("fv.azimut_orientacion", {"S": {"t": "fijo", "v": 0}, "SE_SO": {"t": "disc", "vals": [-45, 45], "p": [0.5, 0.5]}, "E_O": {"t": "disc", "vals": [-90, 90], "p": [0.5, 0.5]},
                               "N": {"t": "fijo", "v": 180}, "nose": {"t": "unif", "min": -90, "max": 90}}, "º (0 = sur, −90 = este, 90 = oeste)", "Respuesta de orientación -> distribución del azimut (convención PVGIS)."),
    ("fv.potencia_min_capex_kwp", 0.1, "kWp", "Potencia mínima para el cálculo de la economía de escala del CAPEX."),
    ("omie.az_mi_fv", R3(-30, 0, 30), "º", "Azimut de «mi FV» en el explorador si no se ha hecho T02."),
    ("omie.incl_mi_fv", R3(15, 30, 45), "º", "Inclinación de «mi FV» en el explorador."),
    ("acs.condiciones_ensayo", {"t_aire_c": 7, "t_agua_c": 55}, "ºC", "Condiciones de ensayo EN 16147 (A7, agua a 55 ºC) a las que se refiere el COP nominal."),
    ("acs.t_acumulacion_bdc_c", 55, "ºC", "Temperatura de acumulación habitual de una bomba de calor de ACS."),
    ("acs.sg_demanda", 1.2, "desviación geométrica", "Incertidumbre de la demanda de ACS según el CTE."),
    ("refrigeracion.sg_superficie", 1.2, "desviación geométrica", "Incertidumbre de la superficie climatizada."),
    ("gas.bombonas_ano_defecto", 6, "bombonas/año", "Una bombona cada dos meses."),
    ("gas.sg_butano", 1.3, "desviación geométrica", "Incertidumbre del consumo de butano."),
    ("huella.palanca_fv_inclinacion", 30, "º", "Inclinación de la FV de referencia de la palanca de reducción (orientación sur)."),
    ("envolvente.reduccion_max", 0.9, "fracción", "Tope de la reducción de la demanda atribuible a una medida."),
    ("emisiones.n_muestras_correlacion", 200, "muestras", "Escenarios usados para la correlación precio–emisiones."),
    ("electrodomesticos.fraccion_evitable_standby", 0.7, "fracción", "Parte del stand-by evitable apagando completamente con regletas."),
    ("curvas.demanda_min_max", [0.8, 1.2], "× demanda base", "Límites del factor de demanda."),
    ("cargador.desempate_eur", 1e-6, "€/kW", "Desempate entre configuraciones de igual coste a favor de la de menor potencia."),
]
