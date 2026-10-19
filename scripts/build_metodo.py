#!/usr/bin/env python3
"""Genera app/data/metodo.json con las secciones 4, 5, 6 y 8 de cada ficha, ya convertidas a HTML (pestaña «Método»)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md2html import md2html  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SECCIONES = (4, 5, 6, 7, 8)
salida = {}
for f in sorted((RAIZ / "docs" / "fichas").glob("T*.md")):
    txt = f.read_text(encoding="utf-8")
    titulo = txt.splitlines()[0].lstrip("# ").strip()
    partes = re.split(r"\n(?=## \d\. )", txt)
    cuerpo = []
    for p in partes[1:]:
        n = int(p[3])
        if n in SECCIONES:
            cuerpo.append(p)
    salida[f.stem.lower()] = {"titulo": titulo, "html": md2html("\n\n".join(cuerpo))}
(RAIZ / "app" / "data" / "metodo.json").write_text(json.dumps(salida, ensure_ascii=False), encoding="utf-8")
print(len(salida), "fichas")
