# Brief de investigación de referencias (para subagentes)

Contexto: app web de herramientas de decisión energética para hogares en España. Toda cifra de referencia vive en `referencias.yaml`.
Fecha de hoy: 2026-10-19. Busca valores vigentes en 2026 (o el último año disponible; indícalo en `nota`).

## Herramientas
- Usa WebSearch (modo standard; "extended" solo si el resultado es pobre). WebFetch NO alcanza los dominios oficiales desde este sandbox (ENOTFOUND): acepta la evidencia de los fragmentos de búsqueda.
- `verificado: true` SOLO si un fragmento procedente de un dominio primario (boe.es, cnmc.es, miteco.gob.es, idae.es, ree.es, omie.es, sede.agenciatributaria.gob.es, ine.es, dgt.es, ec.europa.eu, codigotecnico.org, mitma.gob.es) o una norma citada dice explícitamente el valor.
- Si no hay fuente primaria: `verificado: false`, `valor` = estimación central plausible y `nota` con el rango plausible y la justificación. NUNCA inventes una URL: si no tienes URL, usa la del organismo oficial más específica que hayas visto en los resultados.
- Si el valor depende de un parámetro (año, zona, tamaño), documenta en `nota`.

## Formato de salida (SOLO YAML, sin prosa, sin bloque markdown extra)
```
clave.con.puntos:
  valor: <número | lista | mapa>     # los rangos como [min, moda, max] cuando se indique "rango"
  unidad: "<unidad>"
  fuente: "<organismo + norma/documento>"
  url: "<url>"
  fecha_consulta: "2026-10-19"
  verificado: true|false
  nota: "<obligatoria si verificado=false>"
```
Devuelve únicamente el YAML con las claves pedidas (puedes añadir claves extra útiles con el mismo prefijo). Respuesta máxima ~250 líneas.
