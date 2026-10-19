# Pendientes y decisiones documentadas

Registro de problemas, límites y decisiones (formato: fecha · asunto · estado).

## Entorno de construcción

- **2026-10-19 · Descarga de datos reales bloqueada en el entorno de desarrollo.** Desde el contenedor de construcción solo eran alcanzables PyPI y npm;
  `omie.es`, `apidatos.ree.es`, `re.jrc.ec.europa.eu` y `boe.es` devolvían 403 del proxy. `scripts/fetch_data.py` está completo y revisado pero **no se
  pudo ejecutar contra las fuentes reales**. Para poder construir y probar la app se generó `app/data/` con `scripts/generar_sintetico.py`
  (series sintéticas marcadas con `sintetico: true` en `meta.json`; la interfaz muestra un aviso permanente). **Acción:** lanzar el workflow «Actualizar datos»
  (con la opción PVGIS) para sustituirlos por los reales. Hasta entonces los resultados dependientes de precios, producción solar y emisiones no son representativos.
- **2026-10-19 · Formatos de las fuentes sin contrastar.** Los formatos de `marginalpdbc` (OMIE), de REData (títulos de las series), de PVGIS v5.3
  (`seriescalc`, `tmy`) y de ESIOS están escritos de memoria. Si un campo cambia, `fetch_data.py` conserva la última caché válida y anota el fallo aquí.
- **2026-10-19 · Curvas agregadas de OMIE (T20).** No hay conversor de las curvas reales de OMIE (`curva_pbc`) a la escalera por tecnologías; `curvas_omie.json`
  contiene curvas sintéticas. Pendiente de implementar con datos reales (clasificación de unidades de oferta por tecnología).
- **2026-10-19 · Investigación de referencias con fuentes secundarias.** WebFetch no alcanzaba dominios oficiales (BOE, CNMC, MITECO, IDAE…): la
  investigación usó solo fragmentos de WebSearch. Quedan verificadas con fuente primaria solo las entradas marcadas `verificado: true`
  (peajes de 2026, cargos de potencia, ponderación de futuros del PVPC y una de comunidades energéticas). El resto está `verificado: false` con rango y nota.
  Ver `docs/referencias_pendientes.md`.
- **2026-10-19 · Vigencias normativas dudosas.** IVA y IEE reducidos en 2026, deducciones IRPF de eficiencia energética y vehículo eléctrico, sucesor del MOVES III
  (Plan Auto+), cargos de energía 2.0TD de 2026: confirmar en BOE antes de usar los resultados para decidir.

## Pruebas y calidad

- Sin `xfail` pendientes. Ningún test ha fallado tres veces seguidas.
- `actionlint` se ejecutó con éxito sobre ambos workflows.
- La prueba en navegador (`scripts/e2e.py`) ignora el aviso informativo de Matplotlib («building the font cache»), que Pyodide envía a la consola como error.

## Mejoras no incluidas por alcance

- Resolución cuartohoraria en los balances (los datos de OMIE cuartohorarios se promedian por hora).
- Autenticación, base de datos, backend y analítica quedan fuera del encargo.
