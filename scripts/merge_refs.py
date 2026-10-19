#!/usr/bin/env python3
"""Fusiona docs/refs/*.yaml (+ supuestos) en app/data/referencias.yaml y valida el esquema."""
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))
from core.referencias import validar  # noqa: E402

salida = {}
for f in sorted((RAIZ / "docs" / "refs").glob("*.yaml")):
    d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    for k, v in d.items():
        if k in salida:
            print("duplicada:", k, "en", f.name)
        salida[k] = v
errs = validar(salida)
for e in errs:
    print("ERROR", e)
cab = "# Generado por scripts/merge_refs.py a partir de docs/refs/*.yaml. No editar a mano: editar la fuente y volver a fusionar.\n"
(RAIZ / "app" / "data" / "referencias.yaml").write_text(
    cab + yaml.safe_dump(salida, allow_unicode=True, sort_keys=True, width=100), encoding="utf-8")
print(len(salida), "entradas;", sum(1 for v in salida.values() if v.get("verificado")), "verificadas;", len(errs), "errores")
