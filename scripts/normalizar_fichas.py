#!/usr/bin/env python3
"""Fuerza los 8 títulos exactos de sección en docs/fichas/Txx.md."""
import re
from pathlib import Path

TIT = ["Objetivo y decisión", "Entradas SIMPLE (≤ 8)", "Entradas AVANZADO", 'Tabla de inferencia "respuesta → parámetro técnico"',
       "Datos reales a contrastar (fuente y qué se extrae)", "Método de cálculo con ecuaciones LaTeX",
       "Salidas con rango P10–P90", "Validación y limitaciones"]
for f in sorted((Path(__file__).resolve().parent.parent / "docs" / "fichas").glob("T*.md")):
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"^## (\d)\. .*$", lambda m: f"## {m.group(1)}. {TIT[int(m.group(1)) - 1]}", t, flags=re.M)
    f.write_text(t, encoding="utf-8")
