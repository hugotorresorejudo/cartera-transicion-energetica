# Referencias pendientes de verificar (410 de 419)

Generado por `scripts/listar_pendientes.py`. Una referencia `verificado: false` no tiene todavía una fuente primaria confirmada: la interfaz muestra la etiqueta «pendiente de verificar» junto a cualquier resultado que dependa de ella.

| Clave | Valor | Fuente indicada | Nota |
| --- | --- | --- | --- |
| `acs.banera_freq_dia` | {'diario': [0.7, 1.0, 1.0], 'nunca': [0, 0, 0], 's | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta. |
| `acs.bdc_cop_nominal_acs` | [2.8, 3.3, 3.8] | Fichas de fabricantes de BdC ACS monobloc; UE 812/2013 | Estimación. Rango plausible 2,6-4,2 según modelo. |
| `acs.bdc_eficiencia_carnot_fraccion` | [0.3, 0.4, 0.5] | Literatura técnica (IEA HPT; estudios de campo) | Estimación; la literatura no se consultó en esta sesión. |
| `acs.bdc_perdidas_espera_kwh_24h` | [0.6, 0.9, 1.4] | Fichas de fabricantes; UE 812/2013 | Estimación para depósito de 200 L acumulado a ~55 ºC. |
| `acs.bdc_potencia_electrica_kw` | [0.4, 0.5, 0.7] | Supuesto del autor (hipótesis de modelado) | Potencia eléctrica del compresor de una bomba de calor de ACS. |
| `acs.bdc_tmin_aire_c` | [-10, -7, -5] | Fichas de fabricantes | Algunos modelos operan hasta -15 ºC con apoyo; la mayoría de monobloc de 200 L, -7 a -5 ºC. |
| `acs.capex_bdc_acs_eur` | [1800, 2600, 3800] | Estimación de mercado; IDAE | Sin subvenciones ni deducciones fiscales. Contrastar con presupuestos. |
| `acs.capex_calentador_gas_eur` | [350, 550, 900] | Estimación de mercado | Calentador estanco de 11-14 L/min con instalación. No contrastado. |
| `acs.capex_termo_electrico_eur` | [250, 400, 650] | Estimación de mercado 2025-26 | Termo de 80-100 L con instalación. No contrastado con precios de 2026. |
| `acs.caudal_alcachofa_l_min` | {'ahorradora': [5, 6, 8], 'estandar': [10, 12, 15] | UNE-EN 1112 / etiquetado de griferías (IDAE, Agencia de | Estimación. Una ducha estándar sin limitador suele estar en 10-15 L/min. |
| `acs.condiciones_ensayo` | {'t_agua_c': 55, 't_aire_c': 7} | Supuesto del autor (hipótesis de modelado) | Condiciones de ensayo EN 16147 (A7, agua a 55 ºC) a las que se refiere el COP nominal. |
| `acs.demanda_referencia_l_persona_dia_60c` | 28 | CTE DB-HE 2019 modificado 2022, HE 4 tabla 4.1 y Anejo  | El fragmento de normatia.com (secundaria) cita 28 L/pers·día a 60 ºC para uso residencial privado. No procede de dominio primario. Ocupación |
| `acs.dt_ref_perdidas_k` | 45 | Supuesto del autor (hipótesis de modelado) | Salto de temperatura al que se refieren las pérdidas en espera tabuladas. |
| `acs.duchas_persona_dia` | {'1': [0.9, 1.0, 1.1], '<1': [0.4, 0.6, 0.9], '>1' | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta. |
| `acs.duracion_ducha_min` | {'5a10': [5, 7, 10], 'mas10': [10, 12, 18], 'menos | Tramos de respuesta del usuario; supuesto de la herrami | No es una fuente externa. El tramo mas10 se acota a 18 min. |
| `acs.horas_deposito_tipo` | 24 | Supuesto del autor (hipótesis de modelado) | Horizonte diario de la programación. |
| `acs.mantenimiento_anual_eur` | {'bdc': [40, 80, 150], 'calentador_gas': [60, 90,  | Estimación; el calentador de gas incluye la revisión ob | Estimación. |
| `acs.otros_usos_l_persona_dia` | [8, 10, 14] | Estimación a partir de la demanda de referencia CTE (28 | Estimación. Rango plausible 6-18 L. |
| `acs.perdidas_espera_termo_kwh_24h` | {'100': [1.2, 1.5, 1.9], '150': [1.6, 2.0, 2.6], ' | Reglamento UE 812/2013 (límites de pérdidas por volumen | Estimación para ΔT ~45 K sobre ambiente. Rango según etiqueta B/C. |
| `acs.rendimiento_caldera_condensacion_pcs` | [0.88, 0.92, 0.97] | Estimación; ErP; IDAE (guía de calderas) | Sobre PCI hasta 1,05-1,09, es decir 0,95-0,98 sobre PCS en condiciones óptimas. En servicio real de ACS baja a 0,88-0,92. |
| `acs.rendimiento_caldera_estandar_pcs` | [0.72, 0.78, 0.84] | Estimación; IDAE | Caldera estándar o de baja temperatura. Rendimiento estacional real sobre PCI 80-90 %. |
| `acs.rendimiento_calentador_gas` | [0.78, 0.84, 0.9] | Reglamentos UE 811/2013 y 814/2013; fichas de fabricant | Estimación. Calentador instantáneo estanco: 85-88 % sobre PCI, unos 76-80 % sobre PCS. Caldera mixta de condensación: ver claves siguientes  |
| `acs.rendimiento_termo_electrico` | {'etiqueta_B_perdidas_kwh_24h_100L': [1.2, 1.5, 1. | Reglamentos UE 812/2013 y 814/2013 | Rendimiento de resistencia ~1. La eficiencia ErP perfil M/L, ηwh, ronda 0,35-0,40 sobre energía primaria (coef. 2,5). Pérdidas estimadas, si |
| `acs.sg_demanda` | 1.2 | Supuesto del autor (hipótesis de modelado) | Incertidumbre de la demanda de ACS según el CTE. |
| `acs.t_acumulacion_bdc_c` | 55 | Supuesto del autor (hipótesis de modelado) | Temperatura de acumulación habitual de una bomba de calor de ACS. |
| `acs.t_acumulacion_c` | [60, 60, 70] | RD 487/2022 (legionela); RITE IT 1.1.4.3 | Mínimo 60 ºC en acumulación; 70 ºC para tratamiento térmico periódico. Bomba de calor: uso diario 50-55 ºC ([50,55,60]) con ciclos antilegio |
| `acs.t_interior_c` | [18, 20, 23] | Supuesto del autor (hipótesis de modelado) | Temperatura de un cuarto interior de la vivienda. |
| `acs.t_red_mensual_capitales` | {'A Coruna': [10, 10, 11, 12, 13, 15, 16, 17, 16,  | CTE DB-HE 4, Anejo G (temperatura media del agua fría p | No se encontró la tabla oficial en ningún fragmento de búsqueda (el fragmento secundario indica que está en el Anejo G). Valores reconstruid |
| `acs.t_referencia_c` | 60 | CTE DB-HE 4, Anejo F | Coherente con el fragmento secundario anterior. No visto en dominio primario. |
| `acs.t_uso_ducha_c` | [37, 38, 40] | Práctica habitual; guías IDAE de ahorro en agua calient | Estimación. Rango plausible 36-42 ºC. |
| `acs.vida_util_bdc` | [12, 15, 20] | Estimación; IDAE | Estimación. |
| `acs.vida_util_calentador` | [10, 13, 15] | Estimación; IDAE | Estimación. |
| `acs.vida_util_termo` | [8, 12, 15] | Estimación; IDAE / RITE IT 2 | Depende mucho de la dureza del agua. |
| `acs.volumen_banera_l` | [120, 150, 200] | Estimación; catálogos de fabricantes | Volumen de agua mezclada en un baño típico. Rango plausible 100-250 L. |
| `acs.volumenes_comerciales_l` | [50, 80, 100, 150, 200, 300] | Supuesto del autor (hipótesis de modelado) | Volúmenes comerciales de depósito. |
| `almacenamiento.capacidades_candidatas_kwh` | [0, 5, 10, 15] | Supuesto del autor (hipótesis de modelado) | Capacidades evaluadas en el dimensionado de la batería (0 = sin batería). |
| `almacenamiento.capacidades_comerciales_kwh` | [3.6, 5, 5.12, 7.7, 10, 10.24, 13.5, 15] | Catálogos comerciales de baterías residenciales | Aproximación genérica; no se consultaron catálogos. |
| `almacenamiento.capex_bateria_eur_kwh` | [450, 650, 900] | IDAE / Wood Mackenzie - estimación de mercado 2025-26 | Sin fuente consultada. Las baterías pequeñas (5-10 kWh) quedan en la parte alta. Contexto UNEF: en 2025 el 61 % de las nuevas instalaciones  |
| `almacenamiento.degradacion_anual_bateria` | [0.01, 0.02, 0.03] | Garantias tipicas LFP: 70% a 10-12 anios o 6.000 ciclos | Garantia 70% a 10-12 anios implica 2,5-3%/anio maximo garantizado; degradacion real tipica 1-2%. |
| `almacenamiento.dim_fv_factor` | 1.0 | Supuesto del autor (hipótesis de modelado) | La FV de partida de T06 cubre este múltiplo del consumo anual (limitada por el área disponible). |
| `almacenamiento.dod_util` | 0.9 | Fichas técnicas LFP (90-100 % DoD) | Estimación. Rango plausible 0,8-1,0. |
| `almacenamiento.eficiencia_ciclo` | [0.88, 0.92, 0.95] | Fichas técnicas de baterías LFP residenciales | Estimación; las fichas suelen dar 90-96 % en CC. |
| `almacenamiento.n_muestras_dimensionado` | 60 | Supuesto del autor (hipótesis de modelado) | Muestras Monte Carlo para la curva VAN(capacidad). |
| `almacenamiento.potencia_inversor_hibrido_kw` | [3, 5, 10] | Catalogos (POM 3/5/10 kW; Sungrow SH10T 10 kW trifasico | Fuentes comerciales; rango residencial tipico 3-10 kW (monofasico hasta ~6 kW). |
| `almacenamiento.reposicion_factor` | 0.6 | Supuesto del autor (hipótesis de modelado) | Coste de reponer la batería al final de su vida respecto del CAPEX inicial (bajada de precios). |
| `almacenamiento.vida_calendario_anios` | 12 | Garantías de fabricantes (10-15 años) | Estimación. Rango plausible 10-15 años. |
| `almacenamiento.vida_ciclos` | 6000 | Garantías de fabricantes de LFP residencial (6.000-10.0 | Estimación. |
| `ayudas.capex_envolvente_eur` | [3000, 6000, 12000] | Supuesto del autor (hipótesis de modelado) | Inversión típica en envolvente de una vivienda. |
| `ayudas.deduccion_irpf_ve` | {'compra_ve': {'limite_eur': 3000, 'porcentaje': 0 | RDL 5/2023 (deducciones IRPF por compra de VE y puntos  | Dato de memoria. Una fuente indica que RDL 16/2025 (prórroga de deducciones) no fue convalidado; no se ha comprobado si la deducción VE sigu |
| `ayudas.fraccion_bdc_vs_aerotermia` | 0.5 | Supuesto del autor (hipótesis de modelado) | Ayuda de la bomba de calor de ACS respecto de la de aerotermia. |
| `ayudas.ivtm_anios` | 5 | Supuesto del autor (hipótesis de modelado) | Duración típica de la bonificación del IVTM. |
| `ayudas.ivtm_bonificacion_ve` | [0.25, 0.5, 0.75] | TRLHL art. 95.6 (bonificación hasta 75 % por ordenanza) | Dato de memoria. Depende de la ordenanza municipal. |
| `ayudas.kwh_bateria_referencia` | 10 | Supuesto del autor (hipótesis de modelado) | Batería de referencia en el cálculo de ayudas. |
| `ayudas.kwp_referencia` | 4 | Supuesto del autor (hipótesis de modelado) | Instalación FV de referencia en el cálculo de ayudas. |
| `ayudas.nextgen_aerotermia` | [500, 1500, 3000] | IDAE, programas de renovables térmicas; convocatorias a | No contrastado. Estimación plausible; depende de la comunidad y de la potencia. |
| `ayudas.nextgen_autoconsumo` | [150, 300, 600] | IDAE, ayudas PRTR de autoconsumo y almacenamiento (RD 4 | No contrastado en esta pasada. El PRTR cierra en 2026 y la disponibilidad varía por comunidad. Tratar como opcional. |
| `ayudas.nextgen_ve` | [2000, 4500, 7000] | MOVES III (prorrogado hasta 31-12-2025, sin nuevas soli | No existe un MOVES 2026 confirmado. MOVES III daba hasta 7.000 € con achatarramiento y unos 4.500 € sin él; los expedientes de 2025 aún se r |
| `ayudas.prob_certificado_irpf` | [0.3, 0.5, 0.8] | Supuesto del autor (hipótesis de modelado) | Probabilidad de obtener el certificado de mejora energética que da acceso a la deducción IRPF. |
| `ayudas.prob_convocatoria_abierta` | {'no': 0.0, 'nose': 0.3, 'si': 1.0} | Supuesto del autor (hipótesis de modelado) | Probabilidad de que haya una convocatoria de ayudas directas abierta. |
| `ayudas.prob_ordenanza` | {'no': 0.0, 'nose': 0.4, 'si': 1.0} | Supuesto del autor (hipótesis de modelado) | Probabilidad de que el municipio bonifique IBI/ICIO/IVTM. |
| `ayudas.rehabilitacion_envolvente` | {'ahorro_30': {'porcentaje': 0.4, 'tope_eur_vivien | RD 853/2021 (programas de rehabilitación residencial PR | Porcentajes y topes de memoria, con baja confianza; no contrastado. Varían por convocatoria autonómica. |
| `calefaccion.bdc_capex_aerotermia_eur` | [8000, 12000, 16000] | Estimación de mercado; IDAE | Sin subvención. Con cambio de emisores puede llegar a 18.000 € o más. |
| `calefaccion.bdc_scop_aerotermia` | {'A': [4.2, 4.8, 5.3], 'B': [4.0, 4.5, 5.0], 'C':  | Reglamento UE 813/2013 (clima medio); estudios de campo | El SCOP de etiqueta (clima medio, 35 ºC) suele ser 4,5-5,2. Aquí se descuenta para uso real. Con radiadores a 55 ºC, reducir ~25 %. |
| `calefaccion.caldera_gas_rendimiento_estacional_pcs` | [0.78, 0.86, 0.92] | Estimación; Reglamento UE 813/2013; IDAE | Condensación bien regulada 0,88-0,92. Estándar antigua 0,70-0,78. |
| `calefaccion.capex_caldera_condensacion_eur` | [1800, 2600, 3800] | Estimación de mercado | No contrastado con 2026. |
| `calefaccion.demanda_kwh_m2_ano_por_zona` | {'A': [10, 15, 25], 'B': [20, 30, 45], 'C': [35, 5 | Orden de magnitud de IDAE SPAHOUSEC y CTE | Estimación para el parque medio. Es demanda útil, no consumo final. Depende de la antigüedad (ver multiplicador). |
| `calefaccion.demanda_vs_anio_construccion` | {'1980-2006': 1.0, '2007+': 0.55, 'pre-1980': 1.4} | Estimación; NBE-CT-79, CTE 2006 y CTE 2013/2019 | Estimación. Rango plausible: pre-1980 1,2-1,7; 2007+ 0,4-0,7. |
| `calefaccion.edad` | {'1980': '1980-2006', '2007': '2007+', 'nose': '19 | Supuesto del autor (hipótesis de modelado) | Respuesta de antigüedad -> clave de calefaccion.demanda_vs_anio_construccion. |
| `calefaccion.factor_scop_emisores` | {'alta': 0.75, 'media': 0.9, 'suelo': 1.0} | Supuesto del autor (hipótesis de modelado) | Penalización del SCOP según temperatura de emisión (radiadores de alta temperatura, mixtos o suelo radiante). |
| `calefaccion.fraccion_uso_calefaccion` | [0.5, 0.8, 1.0] | Supuesto del autor (hipótesis de modelado) | Parte de la demanda de referencia que se atiende realmente (uso intermitente o parcial). |
| `calefaccion.mantenimiento_caldera_eur_ano` | [80, 110, 160] | Estimación; RITE IT 3 exige revisión periódica | Estimación. |
| `calefaccion.potencia_extra_aerotermia_kw` | [0, 1.15, 3.45] | Supuesto del autor (hipótesis de modelado) | Potencia contratada adicional necesaria al electrificar la calefacción desde gas. |
| `calefaccion.sg_demanda` | 1.4 | Supuesto del autor (hipótesis de modelado) | Incertidumbre de la demanda de calefacción inferida (muy dependiente del edificio). |
| `calefaccion.uso` | {'ocasional': [0.2, 0.4, 0.6], 'tardes': [0.5, 0.7 | Supuesto del autor (hipótesis de modelado) | Uso real de la calefacción respecto de la demanda de referencia de la zona. |
| `cargador.confianza_horas` | 0.95 | Supuesto del autor (hipótesis de modelado) | Probabilidad mínima de completar la carga diaria dentro de la ventana de disponibilidad. |
| `cargador.cuantil_potencia` | 0.9 | Supuesto del autor (hipótesis de modelado) | Cuantil de la potencia necesaria que se recomienda contratar (1 − probabilidad de corte). |
| `cargador.desempate_eur` | 1e-06 | Supuesto del autor (hipótesis de modelado) | Desempate entre configuraciones de igual coste a favor de la de menor potencia. |
| `cargador.eficiencia` | [0.9, 0.93, 0.95] | Estudios de pérdidas de carga AC (ICCT, INL) | Refuerza ve.eficiencia_carga_domestica. No acumular ambas. |
| `cargador.factor_simultaneidad_ve` | 1.0 | ITC-BT-10 y ITC-BT-52 (RD 842/2002; RD 1053/2014) | La recarga VE se considera con simultaneidad 1 en la previsión de cargas; con gestión dinámica puede justificarse menor. Recordado, sin frag |
| `cargador.monofasico_max_kw` | 7.4 | Supuesto del autor (hipótesis de modelado) | Potencia máxima de cargador en suministro monofásico. |
| `cargador.p_base_noche_kw` | [0.2, 0.4, 0.8] | Supuesto del autor (hipótesis de modelado) | Carga base nocturna de la vivienda durante la carga del VE. |
| `cargador.p_min_gestion_kw` | 1.4 | Supuesto del autor (hipótesis de modelado) | Potencia mínima de carga con gestión dinámica (6 A monofásico). |
| `cargador.potencia_contratada_min_ve` | {3.7: {'con_gestion_dinamica': 5.75, 'sin_gestion_ | RD 1053/2014 ITC-BT-52; gestión dinámica de potencia | Estimación: base del hogar (~3-4 kW) más cargador. Escalones: 5.75, 6.9, 8.05, 9.2, 10.35, 11.5 kW. |
| `cargador.potencias_kw` | [3.7, 7.4, 11] | RD 1053/2014 ITC-BT-52 / catálogo de mercado | Monofásico 3.7 y 7.4; trifásico 11. También existe 22 kW. |
| `cargador.precio_wallbox_instalado_eur` | {3.7: [900, 1100, 1500], 7.4: [1000, 1300, 1800],  | Presupuestos de instaladores / IDAE (supuesto) | 11 kW exige línea trifásica. Instalaciones complejas añaden 500-1500. |
| `cocina.capex_gas_eur` | [150, 250, 500] | Estimación de mercado | Placa de gas, sin instalación. |
| `cocina.capex_induccion_eur` | [250, 450, 900] | Estimación de mercado | Placa de 3 zonas, sin instalación. |
| `cocina.frecuencia` | {'mucho': [1.1, 1.4, 1.8], 'normal': [0.9, 1.0, 1. | Supuesto del autor (hipótesis de modelado) | Frecuencia de cocinado. |
| `cocina.gas_consumo_kwh_ano_persona` | [250, 330, 450] | Estimación derivada de IDAE SPAHOUSEC | Estimación; SPAHOUSEC da cocina por vivienda (~2,5 personas). |
| `cocina.induccion_consumo_kwh_ano_persona` | [150, 200, 270] | Estimación derivada de IDAE SPAHOUSEC | Estimación. |
| `cocina.instalacion_induccion_adicional_eur` | [0, 200, 800] | Estimación de mercado | Línea dedicada y protección; hasta 800 € si hay obra. La ampliación de potencia contratada va aparte. |
| `cocina.menaje_eur` | [0, 100, 300] | Supuesto del autor (hipótesis de modelado) | Coste de menaje compatible con inducción si el actual no lo es. |
| `cocina.potencia_extra_kw` | [0, 0, 2.3] | Supuesto del autor (hipótesis de modelado) | Potencia contratada adicional por pasar a inducción. |
| `cocina.rendimiento_gas_cocina` | [0.35, 0.4, 0.55] | Estudios de laboratorio de eficiencia de cocinado | Típico ~40 %; quemadores eficientes hasta ~55 %. |
| `cocina.rendimiento_induccion` | [0.8, 0.85, 0.9] | Estudios de laboratorio de eficiencia de cocinado | Típico ~84 % de transferencia al recipiente. No se consultó un estudio concreto. |
| `cocina.rendimiento_vitro` | [0.7, 0.75, 0.8] | Supuesto del autor (hipótesis de modelado) | Rendimiento de una vitrocerámica radiante. |
| `cocina.vida_util` | 15 | Supuesto del autor (hipótesis de modelado) | Vida útil de la placa. |
| `combustibles.inflacion_anual` | [0.01, 0.02, 0.04] | Supuesto del modelo | Supuesto. |
| `combustibles.precio_diesel_eur_l` | [1.65, 1.85, 2.05] | Geoportal MITECO (vía Carwow: gasóleo A 1,84 EUR/L el 1 | Corregido de 1.45 a ~1.85. Fuentes secundarias. |
| `combustibles.precio_gasolina_95_eur_l` | [1.65, 1.85, 2.05] | Geoportal MITECO (vía fuel-prices.eu: 1,85 EUR/L el 1-o | Corregido de 1.55 a 1.85 con agregadores secundarios. Hubo rebaja fiscal de carburantes que vencía el 30-sep-2026. Gasolina +4,6% entre 3-ag |
| `comunidad.bonificaciones_ibi_comunidad` | Los ayuntamientos pueden bonificar hasta el 50% de | TRLRHL art. 74.5 (conocimiento general) | No buscado con fragmento; comprobar ordenanza local. |
| `comunidad.capex_fv_comunitaria_eur_wp` | [1.0, 1.25, 1.6] | Estimacion (UNEF/IDAE) | Busqueda sin cifra EUR/Wp; estimacion de mercado. |
| `comunidad.coeficientes_reparto_tipos` | {'estaticos': 'Fijos todo el ano; segun potencia c | Orden TED/1247/2021 (modifica Anexo I RD 244/2019) | Fuentes secundarias coherentes; no dominio primario. |
| `comunidad.coste_gestion_anual_eur_participante` | [15, 30, 60] | Estimacion | Gestor/reparto/administracion; supuesto. |
| `comunidad.distancia_max_autoconsumo_colectivo_m` | {'baja_tension': 'RDL 29/2021 amplia a red BT del  | RD 244/2019; RDL 29/2021; RD 477/2021 (via Osborne Clar | Los resultados citan 500 m y 2000 m para FV en cubierta/suelo industrial (RD 244/2019 original), y que RDL 29/2021 quita el requisito de BT; |
| `comunidad.horizonte_anios` | 25 | Supuesto del autor (hipótesis de modelado) | Horizonte de evaluación. |
| `comunidad.kwp_por_vecino` | {'grande': [1.4, 1.8, 2.2], 'media': [0.8, 1.0, 1. | Supuesto del autor (hipótesis de modelado) | Tamaño de la instalación por participante. |
| `comunidad.mezcla_ocupacion` | {'casa': [0.1, 0.3, 0.6], 'fuera': [0.6, 0.3, 0.1] | Supuesto del autor (hipótesis de modelado) | Mezcla de patrones de ocupación de los vecinos. |
| `comunidad.n_max_mc` | 120 | Supuesto del autor (hipótesis de modelado) | Máximo de muestras Monte Carlo de esta herramienta (coste de cálculo). |
| `comunidad.n_simulados` | 8 | Supuesto del autor (hipótesis de modelado) | Número de participantes distintos simulados (representan a toda la comunidad). |
| `comunidad.numero_tipico_vecinos` | [8, 20, 70] | Supuesto; caso Zaragoza 50 kWp con 70 viviendas | Rango supuesto. |
| `comunidad.potencia_max_compensacion_kw` | 100 | RD 244/2019 art. 4 (compensacion simplificada, potencia | Dato del encargo y conocimiento general; sin fragmento. |
| `comunidad.reparto` | {'consumo': 'Coeficiente estático por consumo', 'd | Supuesto del autor (hipótesis de modelado) | Tipos de coeficiente de reparto. |
| `comunidad.sg_consumo_vecino` | 1.35 | Supuesto del autor (hipótesis de modelado) | Dispersión del consumo anual entre vecinos. |
| `comunidad.vecinos` | {'11-30': 20, '<=10': 8, '>30': 50} | Supuesto del autor (hipótesis de modelado) | Número de participantes representativo de cada tramo. |
| `consumo.electrico_medio_hogar` | 3000 | IDAE SPAHOUSEC / Endesa | Rango 2.700-3.800. |
| `consumo.electrico_por_tipo_vivienda` | {'piso': 2500, 'unifamiliar': 4800} | IDAE SPAHOUSEC (estimación) | Aproximado. |
| `consumo.reparto_usos_hogar` | {'ACS': 0.19, 'calefaccion': 0.47, 'cocina': 0.07, | IDAE SPAHOUSEC II | De memoria; energía total, no solo eléctrica. |
| `curvas.choque_gas` | {'mas100': 2.0, 'mas50': 1.5, 'menos30': 0.7, 'nin | Supuesto del autor (hipótesis de modelado) | Choque de precio del gas. |
| `curvas.choque_renovable` | {'mas25': 1.25, 'menos25': 0.75, 'menos50': 0.5, ' | Supuesto del autor (hipótesis de modelado) | Choque de disponibilidad renovable. |
| `curvas.demanda_min_max` | [0.8, 1.2] | Supuesto del autor (hipótesis de modelado) | Límites del factor de demanda. |
| `curvas.horas` | {'madrugada': 4, 'mediodia': 14, 'noche': 21} | Supuesto del autor (hipótesis de modelado) | Franjas representativas de las curvas almacenadas. |
| `curvas.meses` | {'invierno': [12, 1, 2], 'otono': [9, 10, 11], 'pr | Supuesto del autor (hipótesis de modelado) | Estaciones. |
| `curvas.precio_techo` | 400 | Supuesto del autor (hipótesis de modelado) | Precio de la última unidad si la oferta no cubre la demanda (reserva). |
| `curvas.sd_demanda` | 0.03 | Supuesto del autor (hipótesis de modelado) | Variabilidad de la demanda entre días. |
| `curvas.sg_renovable` | 1.2 | Supuesto del autor (hipótesis de modelado) | Variabilidad de la disponibilidad renovable entre días. |
| `curvas.tecnologias_gas` | ['Ciclo combinado', 'Cogeneración', 'Carbón y otra | Supuesto del autor (hipótesis de modelado) | Tecnologías cuyo precio de oferta sigue al del gas y el CO₂. |
| `curvas.tecnologias_renovables` | ['Solar FV', 'Eólica'] | Supuesto del autor (hipótesis de modelado) | Tecnologías afectadas por el choque de disponibilidad renovable. |
| `datadis.formato_csv_curva_carga` | {'columnas': 'CUPS;Fecha;Hora;Consumo_kWh;Metodo_o | Datadis (conocimiento general); Endesa explica que la c | La busqueda no devolvio ninguna pagina de Datadis; formato de memoria. El parser debe tolerar variantes (columnas extra, fecha YYYY/MM/DD, M |
| `datadis.url_portal` | https://datadis.es | Datadis | No aparecio en resultados; URL del organismo conocido. |
| `deducciones.ibi_fv_bonificacion` | {'duracion_anios': [3, 3, 5], 'porcentaje': [0.0,  | TRLHL art. 74.5 (hasta el 50 % para inmuebles con siste | Confirmado en fuentes municipales y prensa, no en el BOE. Ejemplos: Madrid 50 % durante 5 periodos, Barcelona 3 años. Porcentaje y duración  |
| `deducciones.icio_fv_bonificacion` | [0.0, 0.5, 0.95] | TRLHL art. 103.2.b (hasta el 95 % para construcciones c | Confirmado en fuentes municipales, no en el BOE. Potestativa y dependiente de la ordenanza; algunos municipios la excluyen si la instalación |
| `deducciones.irpf_autoconsumo` | {'incompatible_con_ayudas_publicas': True, 'mejora | RDL 18/2022 (disp. adic. 50.ª LIRPF), prorrogado en 202 | Los porcentajes y plazos proceden de prensa (construible.es, infobae) y no de un fragmento visible de la AEAT. Las fuentes discrepan en el n |
| `desplazamiento.ciclo_aparato` | {'lavadora': 'lavadora_eco_40_60', 'lavavajillas': | Supuesto del autor (hipótesis de modelado) | Ciclo de referencia de cada aparato en electrodomesticos.ciclo_energia_kwh. |
| `desplazamiento.horas_habituales` | {'cuando': [9, 13, 19, 21], 'manana': [8, 9, 10, 1 | Supuesto del autor (hipótesis de modelado) | Horas habituales en que se pone el aparato. |
| `desplazamiento.kwh_dia_termo_defecto` | [2.5, 3.5, 5] | Supuesto del autor (hipótesis de modelado) | Energía diaria del termo eléctrico si no se conoce. |
| `desplazamiento.usos_semana_termo` | 7 | Supuesto del autor (hipótesis de modelado) | El termo calienta cada día; su desplazamiento programa el calentamiento. |
| `desplazamiento.ventanas` | {'cualquiera': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,  | Supuesto del autor (hipótesis de modelado) | Horas en que se acepta poner el aparato. |
| `electrodomesticos.ciclo_energia_kwh` | {'lavadora_40': [0.6, 0.8, 1.0], 'lavadora_60': [0 | Estimacion a partir de Reglamentos UE 2019/2014 y 2019/ | Busqueda confirmo base de 100 ciclos y programa Eco 40-60; no hay cifras kWh por ciclo. Valores tipicos de mercado, estimados. Cons. IDAE: l |
| `electrodomesticos.consumo_anual` | {'congelador': [150, 250, 350], 'horno': [100, 150 | IDAE / UE 2017/1369 (estimación) | Estimaciones plausibles. |
| `electrodomesticos.consumo_standby_hogar` | [15, 25, 50] | IDAE/OCU (estimación) | Endesa: standby ~6,6%. |
| `electrodomesticos.factor_edad` | {'antiguos': [1.1, 1.3, 1.6], 'medios': [0.9, 1.0, | Supuesto del autor (hipótesis de modelado) | Antigüedad de los electrodomésticos. |
| `electrodomesticos.factor_standby` | {'aveces': [0.8, 1.0, 1.2], 'no': [1.2, 1.5, 2.0], | Supuesto del autor (hipótesis de modelado) | ¿Apagas del todo los aparatos? |
| `electrodomesticos.fraccion_evitable_standby` | 0.7 | Supuesto del autor (hipótesis de modelado) | Parte del stand-by evitable apagando completamente con regletas. |
| `electrodomesticos.horas_tv` | {'2-4': [2, 3, 4], '<2': [1, 1.5, 2], '>4': [4, 5. | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta de horas de TV. |
| `electrodomesticos.horas_tv_referencia` | 3 | Supuesto del autor (hipótesis de modelado) | Horas de TV a las que se refiere el consumo anual tabulado. |
| `electrodomesticos.n_tv` | {'1': 1, '2': 2, '3+': 3} | Supuesto del autor (hipótesis de modelado) | Número de televisores. |
| `electrodomesticos.potencia_nominal_kw` | {'bomba_piscina': [0.5, 0.75, 1.5], 'calefaccion_r | Fichas de fabricantes (estimación) | Valores típicos. |
| `electrodomesticos.usos_semana_por_persona` | {'lavadora_por_hogar': [3, 4, 5], 'lavavajillas_po | Supuesto OCU (lavadora y secadora 4/semana, lavavajilla | IDAE no publica frecuencia semanal en lo hallado; son por hogar, no por persona. Estimacion. |
| `electrodomesticos.ventana_programable` | Programar ciclos en horas valle/solares (P3 2.0TD  | Criterio de diseno del proyecto | Nota descriptiva, sin cifra a verificar. |
| `emisiones.acv_por_tecnologia_gco2_kwh` | {'carbon': 820, 'ciclo_combinado': 490, 'eolica_ma | IPCC AR5 WGIII Anexo III (medianas, de memoria; no busc | No se hizo busqueda para este dato; medianas AR5 recordadas, verificar. |
| `emisiones.butano_kgco2_kwh_pci` | 0.254 | Documento reconocido RITE (GLP) | Valor de memoria para GLP. Referido a PCI. Energía primaria no renovable GLP: 1,201 kWh/kWh. |
| `emisiones.carga_desplazable_kwh_dia` | [1, 3, 8] | Supuesto del autor (hipótesis de modelado) | Energía diaria desplazable para evaluar la reducción de emisiones (lavado + termo + carga). |
| `emisiones.diesel_kgco2_l` | 2.65 | MITECO Factores de emisión / RITE; contraste secundario | Corregido de 2.63 a 2.65. Fragmento primario sin valor por litro. Rango 2.50-2.70. |
| `emisiones.electricidad_peninsula_ep_no_renovable_kwh_kwh` | 1.954 | Documento reconocido RITE | Valor de memoria (total 2,368). Ver nota anterior. |
| `emisiones.electricidad_peninsula_rite_kgco2_kwh` | 0.331 | Documento reconocido RITE, electricidad peninsular | Valor de memoria. Factor convencional del RITE; el real del mix actual es bastante menor (~0,10-0,15). No se comprobó si hay una actualizaci |
| `emisiones.estaciones` | {'invierno': [10, 11, 0, 1, 2], 'todo': [0, 1, 2,  | Supuesto del autor (hipótesis de modelado) | Meses de cada estación. |
| `emisiones.factor_electricidad_comercializadora_sin_garantia` | [0.25, 0.28, 0.32] | CNMC, mix residual (comercializadoras sin garantías de  | No contrastado en esta pasada. Estimación de memoria; contrastar con la última publicación de la CNMC. |
| `emisiones.factor_electricidad_mix_medio` | [0.08, 0.1, 0.13] | REE suministra factores a la CNMC; CNMC: media 2024 pen | El dato 2024 (0,080) procede de un artículo académico que cita a la CNMC; no hay cifra oficial de 2025. Moda 0,10 por el repunte de 2025. |
| `emisiones.factor_por_tecnologia_kgco2_mwh` | {'carbon': 950, 'ciclo_combinado': 370, 'cogenerac | Estimacion (REE publica factores por tecnologia en ree. | REE confirma que existe factor t CO2eq/MWh por tecnologia, valores no obtenidos. Rangos plausibles: CC 340-400, carbon 850-1000, cogeneracio |
| `emisiones.fv_evitado_marginal` | [0.33, 0.37, 0.4] | Ciclo combinado de gas (tecnología marginal), MITECO /  | Valor técnico típico de un CCGT (≈0,35-0,40 kg/kWh). Sin fragmento verificado. |
| `emisiones.gas_conversion_pcs_pci` | 1.11 | Relación estándar del gas natural (~1,10-1,11); dato de | Sin fragmento primario. Para el GLP la relación es ~1,085. |
| `emisiones.gas_natural_kgco2_kwh_pci` | 0.252 | Documento reconocido RITE: Factores de emisión de CO2 y | Valor de memoria. La búsqueda confirmó la existencia del documento (copia de 2014; aplicación desde 14-01-2016) pero no el número. Referido  |
| `emisiones.gasolina_kgco2_l` | 2.3 | MITECO Factores de emisión (registro huella de carbono) | El PDF MITECO apareció en resultados pero el fragmento no mostraba el valor por litro. Rango 2.20-2.35. |
| `emisiones.hibrido_reduccion_fraccion` | [0.25, 0.3, 0.38] | IDAE guía de vehículos / estudios ICCT | HEV no enchufable. Mayor ahorro en ciudad. |
| `emisiones.mix_medio_peninsular_ultimo_anio` | 0.08 | CNMC, emisiones directas 2024: 80 gCO2eq/kWh peninsular | Dato 2024, fuente secundaria que cita CNMC. Etiqueta 2025 nacional media 107 g/kWh (Barcelona Energia). |
| `emisiones.mix_residual_cnmc_ultimo_anio` | 0.26 | CNMC etiquetado electricidad; fragmento Barcelona Energ | Valor residual 2025 no hallado en la busqueda. 0,258 es de un comercializador concreto y solo orientativo; rango plausible 0,2-0,3. Consulta |
| `emisiones.n_muestras_correlacion` | 200 | Supuesto del autor (hipótesis de modelado) | Escenarios usados para la correlación precio–emisiones. |
| `emisiones.phev_fraccion_electrica_uso_real` | [0.25, 0.4, 0.55] | ICCT / EEA / Fraunhofer (uso real) | UF de homologación ~0.7-0.8; real europeo 0.25-0.45. |
| `emisiones.pozo_a_rueda_diesel_kgco2_l` | 3.22 | JRC WTT / MITECO | Combustión 2.65 + upstream ~0.57. Rango 3.05-3.35. |
| `emisiones.pozo_a_rueda_gasolina_kgco2_l` | 2.76 | JRC WTT / MITECO | Combustión 2.30 + upstream ~0.46. Rango 2.65-2.90. |
| `envolvente.ahorro_tipico_fraccion` | {'cubierta': [0.1, 0.15, 0.25], 'sate_fachada': [0 | Diario de Avisos 2026 (SATE 25-35%) + rango IDAE de la  | SATE 25-35% en fuente secundaria; resto estimacion. |
| `envolvente.cop_electrica` | 1.0 | Supuesto del autor (hipótesis de modelado) | Rendimiento de los radiadores eléctricos. |
| `envolvente.coste_aislamiento_cubierta_eur_m2` | [25, 45, 90] | Estimacion (Generador de precios / COAC) | No buscado con exito; estimacion. Cubierta plana invertida o trasdosado de falso techo 25-90 EUR/m2 segun solucion. |
| `envolvente.coste_aislamiento_sate_eur_m2` | [65, 95, 140] | Diario de Avisos guia 2026 (EPS 75-115, lana mineral 90 | Fuentes privadas, sin referencia IDAE/COAC. Rango plausible 50-140. |
| `envolvente.coste_ventana_eur_m2` | [250, 400, 700] | Estimacion (Generador de precios / mercado) | Sin fragmento. Rango plausible 250-700. |
| `envolvente.factor_ahorro_edad` | {'1980': 1.0, '2007': 0.5, 'pre1980': 1.15} | Supuesto del autor (hipótesis de modelado) | Potencial de ahorro de las medidas según la antigüedad del edificio. |
| `envolvente.grados_dia_calefaccion_por_zona` | {'A': 800, 'B': 1200, 'C': 1600, 'D': 2200, 'E': 2 | Estimacion a partir de CTE DB-HE / IDAE (documento de z | No hallado fragmento. Valores centrales aproximados; Madrid (D3) ~2000-2200 GD base 15/15; Barcelona (C2) ~1300-1500. Rango +-25%. |
| `envolvente.horizonte_max` | 40 | Supuesto del autor (hipótesis de modelado) | Horizonte máximo de evaluación. |
| `envolvente.pisos_unifamiliar` | 1.5 | Supuesto del autor (hipótesis de modelado) | Plantas medias de una unifamiliar (superficie de cubierta = superficie útil / plantas). |
| `envolvente.reduccion_infiltracion_ventana` | [0.3, 0.5, 0.7] | Estimacion | Supuesto; sin fuente primaria. |
| `envolvente.reduccion_max` | 0.9 | Supuesto del autor (hipótesis de modelado) | Tope de la reducción de la demanda atribuible a una medida. |
| `envolvente.superficie_fachada_ratio` | {'piso_intermedio': [0.5, 0.7, 0.9], 'piso_ultima_ | Supuesto de modelizacion | Supuesto geometrico propio; sin fuente. |
| `envolvente.superficie_huecos_ratio` | [0.12, 0.17, 0.25] | Supuesto de modelizacion | Supuesto: 12-25% de superficie util. |
| `envolvente.tiene_cubierta` | {'adosada': 1, 'aislada': 1, 'intermedio': 0, 'ult | Supuesto del autor (hipótesis de modelado) | El edificio tiene cubierta propia aislable. |
| `envolvente.tipos_edificio` | {'adosada': 'unifamiliar_adosada', 'aislada': 'uni | Supuesto del autor (hipótesis de modelado) | Respuesta de tipo de edificio -> clave de envolvente.superficie_fachada_ratio. |
| `envolvente.transmitancia_u_limite_por_zona` | {'cubiertas_aire': {'A': 0.5, 'B': 0.44, 'C': 0.4, | CTE DB-HE 2019 (RD 732/2019) tabla 3.1.1.a-HE1; muros y | Muros y cubiertas reproducidos en fuentes secundarias (no dominio primario). Fila de huecos cortada en los resultados: valores de memoria; F |
| `envolvente.u_tipica_sin_aislar` | {'cubierta': [1.4, 2.0, 2.6], 'muro_ladrillo_hueco | Estimacion (IDAE guia rehabilitacion / Catalogo Element | No hubo fragmento primario. Rangos tipicos de la bibliografia (catalogo CTE, ficha IDAE de rehabilitacion); depende de espesor y epoca. |
| `envolvente.umbrales_ahorro` | {'ahorro_30': 0.3, 'ahorro_45': 0.45, 'ahorro_60': | Supuesto del autor (hipótesis de modelado) | Umbrales de reducción de la demanda que dan acceso a cada nivel de ayuda de rehabilitación. |
| `envolvente.vida_util_aislamiento` | [30, 40, 50] | Estimacion (fabricantes SATE: 30-50 anos) | Sin fragmento primario. |
| `forma.acs` | [0.1, 0.05, 0.05, 0.05, 0.1, 0.4, 1.6, 2, 1.2, 0.6 | Supuesto del autor (hipótesis de modelado) | Duchas mañana y noche. |
| `forma.actividad_casa` | [0.4, 0.35, 0.3, 0.3, 0.3, 0.4, 0.7, 1, 1.1, 1.2,  | Supuesto del autor (hipótesis de modelado) | Casi siempre en casa. |
| `forma.actividad_finde` | [0.4, 0.35, 0.3, 0.3, 0.3, 0.3, 0.5, 0.7, 1, 1.3,  | Supuesto del autor (hipótesis de modelado) | Fines de semana y festivos. |
| `forma.actividad_fuera` | [0.4, 0.35, 0.3, 0.3, 0.3, 0.4, 0.9, 1.4, 1, 0.5,  | Supuesto del autor (hipótesis de modelado) | Forma diaria laborable de la actividad eléctrica general con la casa vacía en horario laboral. |
| `forma.actividad_parcial` | [0.4, 0.35, 0.3, 0.3, 0.3, 0.4, 0.8, 1.2, 1.1, 1,  | Supuesto del autor (hipótesis de modelado) | Teletrabajo parcial. |
| `forma.calefaccion` | [0.6, 0.5, 0.5, 0.5, 0.6, 0.9, 1.6, 1.6, 1.1, 0.7, | Supuesto del autor (hipótesis de modelado) | Calefacción eléctrica. |
| `forma.cocina` | [0, 0, 0, 0, 0, 0, 0.2, 0.5, 0.4, 0.2, 0.3, 0.8, 1 | Supuesto del autor (hipótesis de modelado) | Picos de comida y cena. |
| `forma.piscina` | [0, 0, 0, 0, 0, 0, 0, 0.2, 0.8, 1.2, 1.4, 1.4, 1.4 | Supuesto del autor (hipótesis de modelado) | Depuradora diurna. |
| `forma.plana` | [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, | Supuesto del autor (hipótesis de modelado) | Cargas continuas (nevera, standby). |
| `forma.refrigeracion` | [0.8, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.5, 0.6, | Supuesto del autor (hipótesis de modelado) | Refrigeración. |
| `forma.ve_casa` | [1.2, 1.2, 1.1, 1, 0.9, 0.6, 0.2, 0, 0, 0, 0, 0, 0 | Supuesto del autor (hipótesis de modelado) | Carga doméstica 'conectar al llegar' sin gestión. |
| `fv.area_por_plaza_garaje_m2` | [15, 15, 15] | CTE DB-SUA (codigotecnico.org) | Dato de memoria, sin fragmento del CTE. |
| `fv.area_tejado_por_kwp_m2` | [5.0, 6.0, 8.0] | Derivado de potencia_modulo_w_m2 más separaciones y est | 1000 W / 210 W/m² ≈ 4,8 m² de módulo por kWp; con pasillos, obstáculos y estructura en cubierta plana 6-8 m²/kWp. |
| `fv.azimut_orientacion` | {'E_O': {'p': [0.5, 0.5], 't': 'disc', 'vals': [-9 | Supuesto del autor (hipótesis de modelado) | Respuesta de orientación -> distribución del azimut (convención PVGIS). |
| `fv.capex_residencial_eur_wp` | [1.2, 1.6, 2.2] | IDAE / UNEF (Anuario FV) - estimación propia a partir d | La búsqueda no devolvió ningún precio en €/Wp de UNEF (solo potencia y nº de viviendas). Rango plausible 1,2-2,2 €/Wp llave en mano; 2-3 kWp |
| `fv.compensacion_simplificada_potencia_max_kw` | 100 | RD 244/2019, art. 4 (compensación simplificada, instala | Los fragmentos recuperados son de fuentes secundarias, no del BOE; por la regla del brief no se marca true. |
| `fv.compensacion_tope` | El valor económico de los excedentes compensados n | RD 244/2019, art. 14. Resumen secundario (Osborne Clark | Fuente secundaria, sin fragmento del BOE. La no acumulación mensual procede de un blog comercial, menos fiable. |
| `fv.degradacion_anual` | [0.003, 0.005, 0.007] | Garantías lineales de fabricantes tier 1 (≈0,4-0,55 %/a | Sin fragmento verificado. Garantías típicas: 30 años con 87-90 % de potencia residual. |
| `fv.economia_escala_exponente` | -0.12 | Supuesto del autor (hipótesis de modelado) | CAPEX unitario ∝ (P/P_ref)^exponente: instalaciones pequeñas son más caras por Wp. |
| `fv.factor_orientacion_norte` | [0.55, 0.65, 0.75] | PVGIS (JRC, ec.europa.eu) - estimación | No se ejecutó PVGIS. Orientación norte con 30º produce típicamente 55-70 % del sur en la península. |
| `fv.horas_equivalentes_espana` | [1300, 1550, 1800] | PVGIS (JRC) / UNEF - estimación | Norte ≈1.250-1.400; centro ≈1.550-1.650; sur y Levante ≈1.650-1.800. |
| `fv.horizonte_anios` | 25 | Supuesto del autor (hipótesis de modelado) | Horizonte de evaluación prudente (inferior a la vida útil del módulo). |
| `fv.inclinacion_estructura_plana` | [15, 25, 35] | Criterio de diseño FV (óptimo ≈30º en la península) | En cubierta plana se usan 10-15º (viento, sombras entre filas) o 30º (máxima producción); 25º como compromiso. |
| `fv.inclinacion_muy_inclinada` | [30, 35, 45] | Supuesto del autor (hipótesis de modelado) | Cubierta muy inclinada (>25º). |
| `fv.inclinacion_tejado_teja` | [18, 22, 25] | Pendiente típica del 30-45 % (arctan 0,30 = 16,7º; 0,40 | Conversión matemática desde la pendiente. |
| `fv.inflacion_electricidad` | [0.0, 0.02, 0.04] | Supuesto de modelización | Supuesto. 2 % alineado con el objetivo del BCE. |
| `fv.n_candidatos` | 8 | Supuesto del autor (hipótesis de modelado) | Potencias candidatas en el dimensionado. |
| `fv.n_muestras_dimensionado` | 100 | Supuesto del autor (hipótesis de modelado) | Muestras Monte Carlo usadas en la curva VAN(P_p). |
| `fv.opex_anual_fraccion_capex` | [0.005, 0.01, 0.015] | Estimación propia (limpieza, seguro, revisiones) | Supuesto. Rango plausible 0,5-1,5 %/año. |
| `fv.paso_cuantizacion_az` | 15 | Supuesto del autor (hipótesis de modelado) | Cuantización de azimut para reutilizar curvas PVGIS. |
| `fv.paso_cuantizacion_incl` | 5 | Supuesto del autor (hipótesis de modelado) | Cuantización de inclinación. |
| `fv.perdidas_sombreado` | {'mucha': [0.2, 0.3, 0.45], 'ninguna': [0.0, 0.02, | IDAE, Pliego de Condiciones Técnicas de instalaciones F | Criterio técnico, no citado literalmente. El pliego IDAE exige en general pérdidas por sombras inferiores al 10 % (de memoria). |
| `fv.plazas_tamano` | {'1': [1, 1, 1], '2': [2, 2, 2], '3+': [3, 3.5, 5] | Supuesto del autor (hipótesis de modelado) | Tamaño útil del tejado expresado en plazas de garaje. |
| `fv.potencia_capex_ref_kwp` | 4 | Supuesto del autor (hipótesis de modelado) | Potencia de referencia del rango de CAPEX €/Wp. |
| `fv.potencia_min_capex_kwp` | 0.1 | Supuesto del autor (hipótesis de modelado) | Potencia mínima para el cálculo de la economía de escala del CAPEX. |
| `fv.potencia_modulo_w_m2` | [190, 210, 225] | Fichas técnicas de módulos mono 400-450 Wp (≈1,72×1,13  | 430 Wp / ≈1,95 m² ≈ 220 W/m²; 210 W/m² como central. |
| `fv.precio_excedentes_medio` | [0.04, 0.07, 0.1] | Ofertas de comercializadoras y PVPC excedentes (referen | La búsqueda no aportó precios de excedentes. Estimación: comercializadoras suelen pagar 0,04-0,10 €/kWh; el PVPC excedentes sigue el mercado |
| `fv.ratio_scop_aerotermia_prevision` | 1.0 | Supuesto del autor (hipótesis de modelado) | Reservado. |
| `fv.sustitucion_inversor_anio` | [10, 13, 17] | Garantías de fabricantes de inversores string | Vida típica 10-15 años; microinversores y optimizadores duran más. Estimación. |
| `fv.sustitucion_inversor_coste_eur_kw` | [120, 200, 300] | Estimación propia a partir de precios de mercado de inv | Rango plausible 120-300 €/kW; se espera que baje con el tiempo. |
| `fv.tasa_descuento_hogar` | [0.02, 0.035, 0.05] | Supuesto de modelización | Supuesto del modelo, no un dato observable. |
| `fv.vida_util` | [25, 30, 35] | Garantías de producto y de rendimiento de fabricantes t | Estimación. Usar 25 años como horizonte financiero prudente. |
| `gas.alquiler_contador` | 1.6 | Orden ITC/3993/2006 (estimación) | Rango 1,4-1,8. |
| `gas.banda_bombona` | [0.92, 1.0, 1.08] | Supuesto del autor (hipótesis de modelado) | Rango del precio de la bombona de butano alrededor del último precio publicado (revisión bimestral limitada por regulación). |
| `gas.banda_variable` | [0.9, 1.0, 1.2] | Supuesto del autor (hipótesis de modelado) | Rango del término variable del gas entre la TUR y las ofertas libres. |
| `gas.bombona_kg` | 12.5 | Supuesto del autor (hipótesis de modelado) | Contenido de la bombona de butano doméstica. |
| `gas.bombonas_ano_defecto` | 6 | Supuesto del autor (hipótesis de modelado) | Una bombona cada dos meses. |
| `gas.butano_pcs` | 13.6 | Conocimiento técnico | Rango 13,6-13,8. |
| `gas.butano_precio_bombona` | 16.35 | Resolución DGPEM; Endesa (marzo 2026) | Último dato hallado; revisiones posteriores no localizadas. Rango 15-18. |
| `gas.cuota_fija_evitable` | [0, 0, 0] | Supuesto del autor (hipótesis de modelado) | Cuota fija de gas que se evita al abandonar el gas (0 si quedan otros usos de gas). |
| `gas.factura_mes_eur` | {'20-40': [20, 30, 40], '40-80': [40, 60, 80], '<2 | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta para la factura media mensual de gas. |
| `gas.fijo_libre_ratio` | [0.8, 1.0, 1.3] | Supuesto del autor (hipótesis de modelado) | Término fijo de las ofertas libres respecto del de la TUR. |
| `gas.gas_natural_impuesto_hidrocarburos` | 0.00234 | Ley 38/1992 art. 50 | De memoria. |
| `gas.iva` | 21 | Ley 37/1992 | Tipo general. |
| `gas.oferta_libre_tipica` | [0.045, 0.06, 0.075] | Estimación comparador CNMC | Sin fuente. |
| `gas.sg_butano` | 1.3 | Supuesto del autor (hipótesis de modelado) | Incertidumbre del consumo de butano. |
| `gas.sg_precio` | 1.1 | Supuesto del autor (hipótesis de modelado) | Incertidumbre del precio del gas por las revisiones trimestrales de la TUR. |
| `gas.tur_termino_fijo_tur1` | 3.83 | Resolución DGPEM TUR 1-oct-2026 | Fuente secundaria. |
| `gas.tur_termino_fijo_tur2` | 8.17 | Resolución DGPEM TUR 1-oct-2026 | Fuente secundaria. |
| `gas.tur_termino_variable_tur1` | 0.0525 | Resolución DGPEM TUR 1-oct-2026 | Fuente secundaria. |
| `gas.tur_termino_variable_tur2` | 0.0504 | Resolución DGPEM TUR 1-oct-2026 | Fuente secundaria. |
| `gas.umbral_tur1_kwh` | 5000 | Supuesto del autor (hipótesis de modelado) | Límite de consumo anual de la TUR1 (por encima se aplica la TUR2). |
| `huella.arboles_absorcion_kgco2_ano` | [10, 20, 30] | Fundacion Aquae (10-30 kg/ano) via resultados; calculad | Depende de especie y edad; fuente no oficial. |
| `huella.factor_autobus` | [0.03, 0.05, 0.07] | Estimacion; SNCF 0.038, blog 0.065-0.070 | Depende de ocupacion. |
| `huella.factor_avion_kgco2_pkm` | [0.13, 0.18, 0.25] | Estimacion (DEFRA/MITECO); SNCF 0.125; blog 0.19-0.285 | No se hallo tabla MITECO. Corto <1500 km ~0.15-0.25, largo ~0.15 sin forzamiento radiativo. |
| `huella.factor_gasoleo_calefaccion_kgco2_kwh` | 0.27 | MITECO factor gasoleo ~2.868 kgCO2e/l (fragmento secund | 2.868 kg/l / 10.6 kWh/l = 0.27; rango 0.26-0.28; dato de 2019 de terceros, no del dominio MITECO. |
| `huella.factor_tren_cercanias` | [0.02, 0.03, 0.05] | Estimacion (MITECO/AEMA); SNCF TGV 0.0035 | Cercanias electrico ~0.025-0.04 segun mix; sin fragmento. |
| `huella.km_dia_coche` | {'20-50': [20, 35, 50], '50-100': [50, 70, 100], ' | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta. |
| `huella.media_hogar_espana_tco2` | [2.0, 2.5, 3.5] | Estimacion (INE cuentas de emisiones / Inventario MITEC | Sin cifra oficial hallada; per capita total citado 5.95-8 t (fuentes secundarias). |
| `huella.palanca_fv_inclinacion` | 30 | Supuesto del autor (hipótesis de modelado) | Inclinación de la FV de referencia de la palanca de reducción (orientación sur). |
| `huella.palanca_fv_kwp` | 3 | Supuesto del autor (hipótesis de modelado) | Instalación FV de referencia para la palanca de reducción. |
| `huella.tipo_vuelo_corto_fraccion` | [0.4, 0.6, 0.8] | Supuesto del autor (hipótesis de modelado) | Fracción de vuelos cortos/medios; el resto largos. |
| `huella.vuelos_ano` | {'1-2': [1, 1.5, 2], '3-6': [3, 4, 6], '>6': [7, 9 | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta. |
| `huella.vuelos_tipicos_km` | {'corto': 1000, 'largo': 8000, 'medio': 2500} | Supuesto (dato del encargo) | Supuesto de modelizacion. |
| `ice.consumo_l_100km` | {'diesel': {'compacto': [4.5, 5.3, 6.2], 'suv_berl | IDAE Guía de vehículos de turismo de venta en España | PHEV es el WLTP ponderado con utility factor; con batería agotada 5.5-7.5 L/100 km. Aplicar también factor real vs WLTP (~1.15-1.25) a ICE/H |
| `ice.coste_mantenimiento_eur_km` | [0.04, 0.055, 0.075] | Estudios de TCO (ADAC, ICCT, Leaseplan) | Incluye revisiones, frenos, neumáticos y averías. |
| `ice.seguro_anual_eur` | [300, 450, 650] | Comparadores de seguros (supuesto) | Estimación; ver ve.seguro_anual_eur. |
| `impuestos.ibi_cuota_media` | [150, 350, 700] | Supuesto del autor (hipótesis de modelado) | Cuota anual del IBI de una vivienda. |
| `impuestos.icio_tipo` | [0.02, 0.03, 0.04] | Supuesto del autor (hipótesis de modelado) | Tipo del ICIO municipal. |
| `impuestos.ivtm_medio_eur` | [72, 95, 140] | TRLRHL art. 95: cuota base 71,94 EUR (12-15,99 CVF) vis | La cuota base 71,94 está respaldada por fuentes municipales, no por fragmento de boe.es. El coeficiente municipal puede llegar hasta 2. Boni |
| `lcoe.capex_eur_kw` | {'ciclo_combinado': [800, 1000, 1400], 'eolica_mar | IRENA Renewable Power Generation Costs in 2024 (FV 691  | Solo se leyeron en fragmentos las medias globales IRENA 2024 (FV, eolica); el fragmento de Lazard no dio USD/kW. El resto de rangos son esti |
| `lcoe.costes_combustible_nuclear_eur_mwh` | [4, 6, 9] | Estimacion (ciclo de combustible nuclear tipico 5-8 EUR | Sin fragmento; estimacion. |
| `lcoe.escenario_gas` | {'alto': 2, 'bajo': 0, 'medio': 1} | Supuesto del autor (hipótesis de modelado) | Escenario de precio del gas y del CO₂ (mínimo, moda, máximo del rango de referencia). |
| `lcoe.factor_capacidad_espana` | {'ciclo_combinado': [0.1, 0.18, 0.4], 'eolica_mari | Estimacion a partir de REE Informe del sistema electric | La busqueda dio solo cuotas de mix 2025 (FV 21,3%, eolica 20,6%, nuclear 18,1%, CC ~17%; 142,5 GW instalados), no horas equivalentes. Valore |
| `lcoe.factor_emision_ccgt_t_mwh` | [0.34, 0.37, 0.4] | Estimacion (gas 0,202 tCO2/MWh PCI / rendimiento 0,55); | Calculo propio; valor de REE por tecnologia no hallado. |
| `lcoe.factor_wacc` | {'alto': 1.25, 'bajo': 0.8, 'medio': 1.0} | Supuesto del autor (hipótesis de modelado) | Escenario de coste de capital sobre el WACC de referencia. |
| `lcoe.mwh_por_kw_mwh` | 8.76 | Supuesto del autor (hipótesis de modelado) | Horas anuales / 1000. |
| `lcoe.opex_fijo_eur_kw_ano` | {'ciclo_combinado': [12, 18, 28], 'eolica_marina': | Estimacion (rangos tipicos IRENA/IEA-NEA/Lazard) | Sin fragmento que de la cifra; estimacion. Rango plausible segun fuentes tipicas IRENA/NEA. |
| `lcoe.opex_variable_eur_mwh` | {'ciclo_combinado': [2, 3, 5], 'eolica_marina': [0 | Estimacion (IEA/NEA Projected Costs 2020, Lazard) | Estimacion; no confirmado en busqueda. |
| `lcoe.perfil_captura` | {'eolica_marina': 'lica', 'eolica_terrestre': 'lic | Supuesto del autor (hipótesis de modelado) | Columna de REData para el precio capturado de cada tecnología. |
| `lcoe.precio_co2_eur_t` | [65, 73, 85] | Cotizaciones EUA Dec-25: ~69,64 (ene 2025) y ~76,69 (se | No se hallo media anual 2025; los EUA subieron ~11,6% en el anio segun Grupo ASE. Valor central estimado. |
| `lcoe.precio_gas_ttf_eur_mwh` | [28, 36, 50] | AleaSoft: futuros TTF front-month ICE promedio 2025 = 3 | Fuente secundaria (AleaSoft), no dominio primario. Ano 2025; rango min/max es supuesto. No se obtuvo media MIBGAS. |
| `lcoe.rendimiento_ciclo_combinado` | [0.5, 0.55, 0.58] | Estimacion tecnica (CCGT modernos 55-60%, parque espano | Sin fragmento; estimacion. |
| `lcoe.tecnologias` | {'ciclo_combinado': 'Ciclo combinado', 'eolica_mar | Supuesto del autor (hipótesis de modelado) | Nombres de las tecnologías del explorador de LCOE. |
| `lcoe.vida_util_anios` | {'ciclo_combinado': [25, 30, 35], 'eolica_marina': | Estimacion (IRENA/NEA/Lazard) | Estimacion estandar de la literatura; no verificada en esta busqueda. |
| `lcoe.wacc` | {'ciclo_combinado': [0.05, 0.07, 0.09], 'eolica_ma | Supuesto del proyecto (referencias IRENA/Lazard no conf | Supuesto; rango plausible 3-10% real. |
| `mercado.costes_variables_eur_mwh` | {'carbon': [90, 120, 160], 'ciclo_combinado': [75, | Calculo ilustrativo: gas TTF 36 EUR/MWh / 0,55 + CO2 73 | Solo para ilustrar el precio marginal. Hidraulica: valor de agua, no coste real. Rangos estimados. |
| `mercado.mecanismo_ajuste_gas_descripcion` | RDL 10/2022 (13 mayo, BOE 14 mayo): mecanismo ibér | BOE RDL 10/2022 (via resumen Comillas IIT, Clifford Cha | Datos de fuentes secundarias; discrepancia sobre duracion del tramo inicial (6 vs 7 meses). Identificador BOE-A-2022-7843 no confirmado en b |
| `mercado.omie_mtu_15min_inicio` | 2025-10-01 | Market Coupling Steering Committee / NEMO Committee: go | Confirmado en varios fragmentos (NEMO Committee, EXAA, SouthPool), ninguno de dominio de la lista primaria; 96 periodos/dia. |
| `mercado.omie_precio_min_max` | {'maximo': 4000, 'minimo': -500} | ACER Decision 01/2023 sobre HMMCP SDAC (referencia +400 | Texto de ACER 2023 lo dice explicitamente, pero ACER no esta en la lista de dominios primarios y no se vio el articulo de la decision 02/202 |
| `mercado.precio_pvpc_descripcion` | PVPC: tarifa regulada para consumidores <=10 kW. T | RD 446/2023, BOE (via eseficiencia.es / MITECO) | Calendario 25/40/55% de fuente secundaria (eseficiencia); no vi el texto BOE. Pesos de 2026 a confirmar. |
| `mercado.tecnologias_marginales_orden_merito` | ['fotovoltaica', 'eolica', 'nuclear', 'hidraulica_ | Orden de merito tipico segun costes variables (descript | Nota descriptiva: renovables y nuclear ofertan cerca de 0 o a coste bajo; gas, carbon y bombeo (coste de oportunidad del agua) suelen fijar  |
| `omie.az_mi_fv` | [-30, 0, 30] | Supuesto del autor (hipótesis de modelado) | Azimut de «mi FV» en el explorador si no se ha hecho T02. |
| `omie.dias_semana` | 7 | Supuesto del autor (hipótesis de modelado) | Longitud del bloque del bootstrap por ventana. |
| `omie.incl_mi_fv` | [15, 30, 45] | Supuesto del autor (hipótesis de modelado) | Inclinación de «mi FV» en el explorador. |
| `omie.n_spread_horas` | 4 | Supuesto del autor (hipótesis de modelado) | Ventana por defecto del spread diario. |
| `omie.tilt_mi_fv` | 30 | Supuesto del autor (hipótesis de modelado) | Inclinación de 'mi FV' en el explorador si no se ha hecho T02. |
| `omie.umbral_precio_bajo` | 0 | Supuesto del autor (hipótesis de modelado) | Umbral por defecto para contar horas con precio no positivo. |
| `omie.ventana_dias` | {'anio': 365, 'mes': 30, 'semana': 7} | Supuesto del autor (hipótesis de modelado) | Ventanas de la vista simple. |
| `perfil.acs_ducha_min` | [4, 7, 10] | Supuesto del autor (hipótesis de modelado) | Duración por defecto de ducha. |
| `perfil.acs_duchas_persona_dia` | [0.8, 1.0, 1.3] | Supuesto del autor (hipótesis de modelado) | Uso por defecto para el consumo eléctrico del termo. |
| `perfil.edad_vivienda_defecto` | 1980-2006 | Supuesto del autor (hipótesis de modelado) | Tramo de antigüedad por defecto para escalar la demanda térmica. |
| `perfil.estacionalidad_actividad` | [1.12, 1.08, 1.03, 1.0, 0.97, 0.95, 0.95, 0.95, 0. | Supuesto del autor (hipótesis de modelado) | Iluminación y uso interior algo mayores en invierno. |
| `perfil.exponente_personas` | 0.6 | Supuesto del autor (hipótesis de modelado) | El consumo de actividad escala con (personas/2,5)^exponente. |
| `perfil.factura_mes_eur` | {'40-70': [40, 55, 70], '70-120': [70, 95, 120], ' | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta de la pregunta de la factura media mensual. |
| `perfil.fraccion_superficie_climatizada_refrig` | [0.25, 0.4, 0.7] | Supuesto del autor (hipótesis de modelado) | Parte de la vivienda que se refrigera con aire acondicionado. |
| `perfil.meses_piscina` | [4, 5, 6, 7, 8] | Supuesto del autor (hipótesis de modelado) | Mayo a septiembre. |
| `perfil.personas` | {'1': [1, 1, 1], '2': [2, 2, 2], '3-4': [3, 3.5, 4 | Supuesto del autor (hipótesis de modelado) | Respuesta cualitativa traducida a rango numérico. |
| `perfil.personas_referencia` | 2.5 | Supuesto del autor (hipótesis de modelado) | Hogar medio de referencia (INE). |
| `perfil.piscina_dias` | [120, 180, 240] | Supuesto del autor (hipótesis de modelado) | Temporada de piscina. |
| `perfil.piscina_horas_dia` | [4, 6, 8] | Supuesto del autor (hipótesis de modelado) | Horas de depuración. |
| `perfil.sg_componente` | 1.25 | Supuesto del autor (hipótesis de modelado) | Dispersión de cada componente del consumo. |
| `perfil.sg_factura` | 1.12 | Supuesto del autor (hipótesis de modelado) | Incertidumbre del consumo anual inferido de un tramo de factura. |
| `perfil.sg_prior_consumo` | 1.35 | Supuesto del autor (hipótesis de modelado) | Incertidumbre del consumo anual sin dato de factura. |
| `perfil.superficie_m2` | {'piso_70_120': [70, 90, 120], 'piso_<70': [40, 60 | Supuesto del autor (hipótesis de modelado) | Superficie útil por tramo de respuesta; el valor central es el punto medio aproximado del tramo. |
| `perfil.t_base_calefaccion_c` | 15 | Supuesto del autor (hipótesis de modelado) | Temperatura base para repartir la calefacción eléctrica en el año. |
| `perfil.t_base_refrigeracion_c` | 24 | Supuesto del autor (hipótesis de modelado) | Temperatura base para repartir la refrigeración en el año. |
| `perfil.ve_km_dia` | [15, 35, 70] | Supuesto del autor (hipótesis de modelado) | Uso por defecto del VE en el perfil si no se ha hecho T04. |
| `refrigeracion.capex_reversible_factor` | [1.1, 1.25, 1.5] | Supuesto del autor (hipótesis de modelado) | Sobrecoste de un equipo reversible frente a un split solo frío. |
| `refrigeracion.capex_split_eur` | [700, 1000, 1600] | Estimación de mercado | Split 1x1 inverter de ~2,5 kW (9000 BTU). |
| `refrigeracion.demanda_kwh_m2_ano_por_zona` | {'A': [5, 10, 20], 'B': [10, 20, 30], 'C': [5, 12, | Estimación; CTE e IDAE | La zona CTE (A-E) es de invierno; la refrigeración depende más de la severidad de verano y varía mucho dentro de cada zona. Hasta 40 kWh/m²  |
| `refrigeracion.estancias_equipos` | {'1': 1, '2': 2, '3-4': 3, 'toda': 4} | Supuesto del autor (hipótesis de modelado) | Número de splits o unidades interiores. |
| `refrigeracion.factor_reversible` | [0.9, 0.95, 1.0] | Supuesto del autor (hipótesis de modelado) | SEER de un multisplit reversible respecto del split individual. |
| `refrigeracion.factor_seer_real` | [0.7, 0.8, 0.9] | Supuesto del autor (hipótesis de modelado) | SEER de campo respecto del de etiqueta. |
| `refrigeracion.factor_soleada` | {'no': [0.8, 1.0, 1.1], 'si': [1.1, 1.3, 1.6]} | Supuesto del autor (hipótesis de modelado) | Vivienda muy soleada (orientación y falta de protección solar). |
| `refrigeracion.fraccion_estancias` | {'1': [0.1, 0.15, 0.2], '2': [0.2, 0.3, 0.4], '3-4 | Supuesto del autor (hipótesis de modelado) | Parte de la vivienda climatizada según estancias. |
| `refrigeracion.potencia_electrica_eer` | [2.8, 3.3, 4.0] | Supuesto del autor (hipótesis de modelado) | Relación potencia frigorífica/eléctrica a plena carga para el pico. |
| `refrigeracion.potencia_frigorifica_w_m2` | [60, 90, 120] | Regla práctica de dimensionado | Rango plausible 50-150 W/m² según orientación y clima. |
| `refrigeracion.seer_antiguo` | [2.5, 3.2, 4.0] | Supuesto del autor (hipótesis de modelado) | Equipo antiguo sin inverter. |
| `refrigeracion.seer_split` | [5.6, 6.5, 8.5] | Reglamento UE 626/2011 (etiquetado); catálogos | Estimación. A++ SEER >= 6,1; A+++ >= 8,5. El 626/2011 fue sustituido por el Reglamento UE 2019/2016 (escala A-G); se mantiene como referenci |
| `refrigeracion.setpoint_c` | [23, 24, 25] | RITE IT 1.1.4.1.2 | Rango 23-25 ºC dado por el brief. No se vio el texto en un fragmento primario. |
| `refrigeracion.sg_superficie` | 1.2 | Supuesto del autor (hipótesis de modelado) | Incertidumbre de la superficie climatizada. |
| `refrigeracion.uso` | {'medio': [0.8, 1.0, 1.2], 'mucho': [1.2, 1.5, 2.0 | Supuesto del autor (hipótesis de modelado) | Uso del aire acondicionado. |
| `refrigeracion.vida_util` | 15 | Supuesto del autor (hipótesis de modelado) | Vida útil de un split. |
| `simultaneidad.base_kw` | [0.25, 0.5, 1.0] | Supuesto del autor (hipótesis de modelado) | Carga base simultánea (nevera, iluminación, TV, ordenador). |
| `simultaneidad.dias_activos` | {'aire_acondicionado': 120, 'calefaccion_electrica | Supuesto del autor (hipótesis de modelado) | Días de uso estacional; el resto de aparatos se supone todo el año. |
| `simultaneidad.dias_exceso_limitador` | {'a_menudo': [7, 20, 60], 'alguna': [1, 3, 6], 'nu | Supuesto del autor (hipótesis de modelado) | Respuesta '¿salta el limitador?' traducida a días con corte. |
| `simultaneidad.potencia_efectiva_kw` | {'aire_acondicionado': [0.5, 1.0, 2.0], 'calefacci | Supuesto del autor (hipótesis de modelado) | Potencia media efectiva en 15 min de cada aparato (inferior a la nominal por ciclado y uso parcial de zonas). |
| `simultaneidad.prob_pico_diario` | {'aire_acondicionado': 0.3, 'calefaccion_electrica | Supuesto del autor (hipótesis de modelado) | Probabilidad de que cada aparato esté en marcha en el cuarto de hora de máxima demanda de un día con uso. |
| `solar_termica.area_captador_m2` | [1.8, 2.0, 2.5] | Estimacion (catalogos) | Tipico 2 m2 de apertura. |
| `solar_termica.capex_eur_m2` | [600, 800, 1000] | Habitissimo (estimacion de mercado) | Fuente privada; no IDAE. |
| `solar_termica.capex_vivienda_2_captadores_eur` | [3500, 4800, 6500] | Habitissimo: ~6000 EUR ACS vivienda 150 m2; derivado de | Estimacion central; rango plausible 3500-7000. |
| `solar_termica.contribucion_minima_hs4_por_zona` | {'tabla_2_1_original_pct_zonas_I_a_V': {'10000-125 | CTE DB-HE 4 tabla 2.1 (version original; extraccion de  | Texto PDF desordenado, fuente no primaria. Aviso: segun Ferroli, la version vigente (HE 2019) elimina la distincion por zona y exige 60% (<5 |
| `solar_termica.eta_sistema` | [0.7, 0.8, 0.9] | Supuesto del autor (hipótesis de modelado) | Rendimiento de tuberías, intercambio y acumulación del sistema solar. |
| `solar_termica.fraccion_solar_tipica` | {'I': 0.45, 'II': 0.55, 'III': 0.6, 'IV': 0.65, 'V | Estimacion (IDAE; consistente con minimos HE4 30-70%) | Rango tipico 40-75%; sin fragmento. |
| `solar_termica.mantenimiento_anual_fraccion` | [0.01, 0.015, 0.02] | Estimacion | Supuesto 1-2%. |
| `solar_termica.n_captadores` | {'1': 1, '2': 2, '3+': 3} | Supuesto del autor (hipótesis de modelado) | Número de captadores. |
| `solar_termica.pr_fv_proxy` | 0.8 | Supuesto del autor (hipótesis de modelado) | Rendimiento global del sistema FV de PVGIS usado para recuperar la irradiancia sobre el plano inclinado a partir de la producción por kWp. |
| `solar_termica.rendimiento_captador` | {'a1': [3.0, 3.8, 4.5], 'a2': [0.005, 0.012, 0.02] | Estimacion captador plano selectivo (EN 12975 / ISO 980 | Busqueda no confirmo valores. Comillas: rendimiento plano ~50% a (tm-ta)/G~1 (unidades del estudio). |
| `solar_termica.sg_demanda` | 1.25 | Supuesto del autor (hipótesis de modelado) | Incertidumbre de la demanda de ACS. |
| `solar_termica.t_colector_c` | [40, 50, 65] | Supuesto del autor (hipótesis de modelado) | Temperatura media del fluido en el captador. |
| `solar_termica.umbral_g_kw_m2` | 0.05 | Supuesto del autor (hipótesis de modelado) | Irradiancia mínima para que el captador aporte energía. |
| `solar_termica.vida_util` | [20, 25, 30] | Estimacion (IDAE) | Sin fragmento. |
| `solar_termica.volumen_acumulador_l_m2` | [50, 75, 180] | CTE DB-HE 4: 50 < V/A < 180 (dato del encargo) | Relacion no confirmada en fragmentos; tipico 60-100 en vivienda. |
| `solar_termica.zonas_climaticas_solares_he4` | {'zona_I': {'ejemplo': 'Galicia norte, Cantabria,  | CTE DB-HE 4 tabla 2.2 (limites de zonas); aproximacion | Solo relacion aproximada; limites 3.8/4.2/4.6/5.0 de memoria (mapa de zonas por provincia no obtenido). |
| `tarifa.ajuste_gas_fin` | 2023-12-31 | RDL 10/2022, prórrogas RDL 5/2023 y 8/2023 | De memoria. |
| `tarifa.ajuste_gas_inicio` | 2022-06-15 | RDL 10/2022 | De memoria. |
| `tarifa.ajuste_gas_tope_gas_inicial` | 40 | RDL 10/2022 | 40 €/MWh, +5 €/mes desde el 7º mes (media primer semestre ~48,8). |
| `tarifa.alpha_corte` | 0.1 | Supuesto del autor (hipótesis de modelado) | Probabilidad anual admisible de que la demanda máxima supere la potencia contratada. |
| `tarifa.alquiler_contador` | 0.81 | Orden ITC/3860/2007 | Conocimiento previo; analógico 0,54. Sin IVA. |
| `tarifa.bono_social_descuento` | 42.5 | RD 897/2017 y prórrogas | No confirmado; verificar. |
| `tarifa.cargo_energia_p1` | 0.064292 | Orden TED/1524/2025 (derivado: total Eleia 0,097553 - p | Derivado de web comercial (peaje+cargo) menos peaje oficial; no leído en la orden. |
| `tarifa.cargo_energia_p2` | 0.012858 | Orden TED/1524/2025 (derivado: 0,029267 - peaje) | Derivado, ver P1. |
| `tarifa.cargo_energia_p3` | 0.003215 | Orden TED/1524/2025 (derivado: 0,003292 - peaje) | Derivado, ver P1. |
| `tarifa.dias_anio` | 365 | Supuesto del autor (hipótesis de modelado) | Año de facturación. |
| `tarifa.festivos_nacionales_fijos` | ['01-01', '01-06', '05-01', '08-15', '10-12', '11- | Estatuto de los Trabajadores art. 37.2 | Viernes Santo móvil (2026-04-03), no incluido. |
| `tarifa.horas_periodos` | {'P1_punta_laborables': [10, 11, 12, 13, 18, 19, 2 | CNMC Circular 3/2020 | De conocimiento de la norma. |
| `tarifa.iee_minimo_domestico` | 0.001 | Ley 38/1992 art. 99 | De memoria de la norma. |
| `tarifa.iee_tipo` | 5.11269632 | Ley 38/1992 art. 99; Selectra/Repsol oct-2026 | Octubre 2026 sin rebaja. Rebaja a 0,5% (IVA 10%) condicionada a IPC electricidad >15% interanual; evaluación sept-2026 podría afectar a novi |
| `tarifa.indexada_margen` | [5, 15, 35] | Estimación ofertas indexadas | Sin fuente primaria. |
| `tarifa.indexada_perdidas` | [0.12, 0.13, 0.14] | RD 1164/2001 / CNMC | De memoria. |
| `tarifa.indexada_servicios_ajuste` | [10, 18, 30] | Estimación REE/OMIE | Sin fuente hallada. |
| `tarifa.iva_electricidad` | 21 | Ley 37/1992; Selectra/Repsol | 21% en octubre 2026. IVA reducido 10% para potencia <=10 kW solo en periodos con rebaja (22-mar a 31-may-2026) o si se activa la salvaguarda |
| `tarifa.oferta_fija_energia_tipica` | [0.1, 0.13, 0.18] | Estimación comparador CNMC | Rango plausible 0,09-0,20. |
| `tarifa.oferta_fija_potencia_tipica` | [0.07, 0.09, 0.12] | Estimación ofertas 2.0TD | Regulado peaje+cargo P1 = 0,076 €/kW·día. |
| `tarifa.pmax_muestras` | 500 | Supuesto del autor (hipótesis de modelado) | Muestras de simultaneidad para la demanda máxima. |
| `tarifa.potencia_sin_dato` | [3, 4, 5] | Supuesto del autor (hipótesis de modelado) | Rango de potencia contratada probable si el usuario responde 'no sé' (mínimo, moda, máximo). |
| `tarifa.potencias_normalizadas` | [1.15, 1.73, 2.3, 3.46, 4.6, 5.75, 6.9, 8.05, 9.2, | RD 1164/2001 / REBT | En 2.0TD se puede contratar cualquier potencia hasta 15 kW. |
| `tarifa.pvpc_margen_comercializacion` | 3.113 | RD 446/2023 | De memoria; rango 3,0-3,3. |
| `tarifa.ratio_periodos_fija` | {'P1': 1.25, 'P2': 1.0, 'P3': 0.75} | Supuesto del autor (hipótesis de modelado) | Ofertas con precio por periodo: relación respecto al precio único típico. |
| `tarifa.sg_f_consumo` | 1.05 | Supuesto del autor (hipótesis de modelado) | Incertidumbre residual del consumo anual (factor global). |
| `tarifa.sg_f_omie` | 1.15 | Supuesto del autor (hipótesis de modelado) | Incertidumbre del nivel medio del precio OMIE respecto del histórico. |
| `tarifa.sg_precio_nivel` | 1.0 | Supuesto del autor (hipótesis de modelado) | Reservado. |
| `ve.anios_tenencia` | {'10+': 11, '3-5': 4, '6-9': 8} | Supuesto del autor (hipótesis de modelado) | Años de tenencia por tramo (valor central). |
| `ve.ayudas_compra` | {'base_maxima_eur': 20000, 'deduccion_irpf_fraccio | Medios (Carwow, RACE, Mapfre) sobre RDL que recupera pa | Segunda pasada con WebSearch: solo fuentes secundarias, sin dominio primario. Las cifras del tope de recarga difieren entre medios (600 vs 4 |
| `ve.consumo_wltp_kwh_100km` | {'compacto': [14.5, 16.5, 18.5], 'suv_berlina': [1 | IDAE Guía de vehículos de turismo de venta en España | Rangos típicos de homologación WLTP. Contraste secundario: VW ID.4 16,9 kWh/100 km WLTP; fuente española orientativa: 12-13 bueno, 16-18 nor |
| `ve.coste_carga_publica_eur_kwh` | {'ac': [0.35, 0.45, 0.55], 'dc': [0.45, 0.58, 0.75 | Observatorio de la Movilidad Eléctrica / ANFAC / Electr | Estimación. Ultrarrápida >150 kW puede llegar a 0.80-0.90. |
| `ve.coste_mantenimiento_ve_eur_km` | [0.015, 0.025, 0.035] | Estudios de TCO (ADAC, ICCT, Leaseplan) | Incluye revisiones, frenos y neumáticos. Aprox. 30-50% menos que ICE. |
| `ve.eficiencia_carga_domestica` | [0.85, 0.9, 0.93] | ICCT y estudios de pérdidas de carga AC (Idaho National | Pérdidas de 7-15% según potencia, temperatura y estado de batería. |
| `ve.f_ayuda` | [0, 0.5, 1] | Supuesto del autor (hipótesis de modelado) | Fracción de la deducción IRPF por compra de VE efectivamente aprovechada. |
| `ve.factor_consumo_real_vs_wltp` | [1.1, 1.2, 1.3] | Estudios ADAC / Geotab / EEA (consumo real vs homologad | Desviación real habitual 10-30% según velocidad y uso. Aplicar sobre consumo WLTP a temperatura templada. |
| `ve.factor_temperatura_consumo` | {0: [1.25, 1.35, 1.5], 5: [1.15, 1.25, 1.35], 10:  | Geotab (curva consumo/temperatura), ADAC, EEA | Óptimo ~20-22 °C. Aproximación de la literatura; interpolar linealmente. |
| `ve.fraccion_carga_publica_por_aparcamiento` | {'calle': [0.5, 0.75, 0.95], 'garaje_comunitario': | Supuesto del modelo | Supuesto. |
| `ve.horarios` | {'a': [17, 8], 'b': [19, 8], 'c': [21, 7], 'd': [1 | Supuesto del autor (hipótesis de modelado) | Franjas de respuesta: a) llego ~17 h y salgo ~8 h; b) ~19 h/~8 h; c) ~21 h/~7 h; d) ~19 h/~10 h. |
| `ve.km_fin_de_semana_ano` | [2500, 4000, 6000] | MITMA EMOVE / INE; supuesto | Supuesto de ocio y fin de semana; no es dato directo de la encuesta. |
| `ve.km_laborable` | {'20-50': [20, 35, 50], '50-100': [50, 70, 100], ' | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta de km en un día laborable. |
| `ve.km_viaje_largo` | [250, 400, 700] | Supuesto del modelo | Supuesto. |
| `ve.laborables_semana` | 5 | Supuesto del autor (hipótesis de modelado) | Días laborables por semana para anualizar los km. |
| `ve.penalizacion_carga_comunitaria` | Sin penalización legal: el derecho a instalar el p | Ley 49/1960 de Propiedad Horizontal art. 17.5; RD 1053/ | Recordado de la norma, sin fragmento. Penalización real de coste y plazo. |
| `ve.potencia_cargador_kw` | {'calle': 3.7, 'garaje_comunitario': 3.7, 'garaje_ | Supuesto del autor (hipótesis de modelado) | Potencia de cargador doméstico supuesta por tipo de aparcamiento. |
| `ve.precio_compra_diesel_eur` | {'compacto': [24000, 28000, 33000], 'suv_berlina': | ANFAC / Autoscout24 | Oferta diésel muy reducida en urbano; estimación. |
| `ve.precio_compra_gasolina_eur` | {'compacto': [20000, 25000, 30000], 'suv_berlina': | ANFAC / Autoscout24 | Estimación de PVP nuevo 2025-26. |
| `ve.precio_compra_hibrido_eur` | {'compacto': [26000, 30000, 36000], 'suv_berlina': | ANFAC / Autoscout24 | Estimación de PVP nuevo 2025-26. |
| `ve.precio_compra_phev_eur` | {'compacto': [33000, 38000, 45000], 'suv_berlina': | ANFAC / Autoscout24 | Estimación. Pocos modelos PHEV urbanos. |
| `ve.precio_compra_ve_eur` | {'compacto': [28000, 34000, 42000], 'suv_berlina': | ANFAC / Autoscout24 / IDAE guía de vehículos | Estimación de PVP de mercado español 2025-26 sin ayudas. Marcas chinas bajan el mínimo de urbano a ~17000. |
| `ve.seguro_anual_eur` | [350, 500, 750] | Comparadores de seguros (supuesto) | VE suele costar 10-20% más por reparación y batería. Depende de edad, provincia y cobertura. |
| `ve.sg_precio_energia` | 1.0 | Supuesto del autor (hipótesis de modelado) | Reservado. |
| `ve.valor_residual_fraccion` | {'ice': {3: [0.6, 0.66, 0.72], 5: [0.48, 0.55, 0.6 | OCU/BEUC (3 años, 45000 km: VE pierde 50%, PHEV 39%, di | Ajustado con WebSearch a 3 y 5 años (fuentes secundarias). Años 8-12 siguen siendo extrapolación. La brecha VE-gasolina se reduce en 2025 (d |
| `ve.viajes_largos` | {'1-5': [1, 3, 5], '6-15': [6, 10, 15], '>15': [15 | Supuesto del autor (hipótesis de modelado) | Tramos de respuesta de viajes largos. |
| `ve.vida_bateria_garantia` | {'anos': [8, 8, 10], 'estado_salud_minimo': 0.7, ' | Garantías estándar de fabricantes; Reglamento (UE) 2023 | Estándar 8 años o 160000 km con SoH >=70%. |
