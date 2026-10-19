#!/usr/bin/env python3
"""Genera docs/referencias_pendientes.md y actualiza el bloque de referencias `verificado: false` del README."""
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
refs = yaml.safe_load((RAIZ / "app" / "data" / "referencias.yaml").read_text(encoding="utf-8"))
pend = {k: v for k, v in refs.items() if not v["verificado"]}
ver = {k: v for k, v in refs.items() if v["verificado"]}

lineas = [f"# Referencias pendientes de verificar ({len(pend)} de {len(refs)})", "",
          "Generado por `scripts/listar_pendientes.py`. Una referencia `verificado: false` no tiene todavía una fuente primaria confirmada: "
          "la interfaz muestra la etiqueta «pendiente de verificar» junto a cualquier resultado que dependa de ella.", "",
          "| Clave | Valor | Fuente indicada | Nota |", "| --- | --- | --- | --- |"]
for k in sorted(pend):
    v = pend[k]
    val = str(v["valor"]).replace("|", "/").replace("\n", " ")[:50]
    lineas.append(f"| `{k}` | {val} | {str(v['fuente'])[:55].replace('|', '/')} | {str(v.get('nota', ''))[:140].replace('|', '/').replace(chr(10), ' ')} |")
(RAIZ / "docs" / "referencias_pendientes.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")

por_prefijo = {}
for k in pend:
    por_prefijo.setdefault(k.split(".")[0], []).append(k)
bloque = [f"Hay **{len(pend)} referencias con `verificado: false`** de {len(refs)} ({len(ver)} verificadas con fuente primaria). Detalle completo con notas en "
          "[`docs/referencias_pendientes.md`](docs/referencias_pendientes.md).", "", "<details><summary>Claves pendientes por bloque</summary>", ""]
for pre in sorted(por_prefijo):
    bloque.append(f"- **{pre}** ({len(por_prefijo[pre])}): " + ", ".join(f"`{k.split('.', 1)[1]}`" for k in sorted(por_prefijo[pre])))
bloque += ["", "</details>"]
r = RAIZ / "README.md"
if r.exists():
    t = r.read_text(encoding="utf-8")
    t = re.sub(r"<!-- PENDIENTES:INICIO -->.*<!-- PENDIENTES:FIN -->", "<!-- PENDIENTES:INICIO -->\n" + "\n".join(bloque) + "\n<!-- PENDIENTES:FIN -->", t, flags=re.S)
    r.write_text(t, encoding="utf-8")
print(len(pend), "pendientes;", len(ver), "verificadas")
