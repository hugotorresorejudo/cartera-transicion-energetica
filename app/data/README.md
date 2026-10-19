# Datos de la aplicación (`app/data/`)

La app solo **lee** estos ficheros por la misma ruta de origen; no hace ninguna petición a terceros. Los genera `scripts/fetch_data.py`
(workflow `data.yml`) o, solo para demostración sin conexión, `scripts/generar_sintetico.py`. Tamaño objetivo: ≤ 20 MB en total.

| Fichero | Contenido | Generado por |
| --- | --- | --- |
| `referencias.yaml` | **Única fuente de cifras de referencia.** Cada entrada: `valor`, `unidad`, `fuente`, `url`, `fecha_consulta`, `verificado` (+ `nota` si `verificado: false`). | `scripts/merge_refs.py` desde `docs/refs/*.yaml` |
| `referencias.json` | Copia de la anterior para arrancar rápido en Pyodide (`referencias.py` la usa si está al día). | `scripts/merge_refs.py` |
| `metodo.json` | HTML de las secciones 4–8 de cada ficha (pestaña *Método*). | `scripts/build_metodo.py` |
| `meta.json` | `{actualizado, sintetico, fuentes}`: fecha de los datos y si son sintéticos (la UI avisa). | `fetch_data.py` / `generar_sintetico.py` |
| `provincias.csv` | `codigo` (INE, 2 primeros dígitos del CP), `nombre`, `lat`, `lon`, `altitud_m`, `zona_cte`, `territorio` de las 52 capitales. Zona CTE DB-HE (Anejo B) **sin verificar en fuente primaria**. | manual |
| `omie_es_horario.csv.gz` | Precio marginal del mercado diario: `fecha`, `h` (1–25), `es`, `pt` en €/MWh. 3 años completos + el actual; los datos cuartohorarios se promedian por hora. | `fetch_data.py` |
| `omie_percentiles.json` | P10/P50/P90 del precio ES por `mes\|tipo_dia\|hora` (`L` laborable, `F` fin de semana/festivo). | `fetch_data.py` |
| `redata_horario.csv.gz` | Últimos 12 meses horarios de REData: `ts`, `p_*` (PVPC, spot, €/MWh→€/kWh según serie), `g_*` generación por tecnología (MW), `d_*` demanda (MW), `e_*` emisiones (t CO₂). | `fetch_data.py` |
| `pvgis/pv_XX.npz` | Por capital (XX = código INE): `y` (uint16, 4 inclinaciones {0,15,30,45} × 5 azimuts {−90,−45,0,45,90} × 8760 h, kW por kWp × 1e−4, año típico), `fy` (años × 12, factor mensual de cada año PVGIS respecto del típico), `t2m` (int16, 8760 h, °C × 10, TMY), `anios`. Convención PVGIS: azimut 0 = sur. | `fetch_data.py --pvgis` |
| `curvas_omie.json` | Curvas de oferta por tecnología y demanda de días representativos (hora 4, 14, 21): `[{fecha, hora, oferta:[{tecnologia, mw, precio}], demanda_mw}]`. Hoy sintéticas. | `generar_sintetico.py` |
| `esios_horario.csv.gz` | (opcional) `ts`, `pvpc`, `spot` en €/kWh, solo con el secreto `ESIOS_TOKEN`. | `fetch_data.py` |

Notas:

- Todas las series se alinean a un año tipo de **8760 horas** (sin 29 de febrero); las horas del cambio de hora se promedian (25 h) o se duplican (23 h).
- La temperatura del agua de red por capital y las demás tablas por zona viven en `referencias.yaml`, no aquí.
