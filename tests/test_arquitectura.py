"""Reglas de arquitectura del encargo: sin cifras de referencia literales, sin red, entradas y salidas del núcleo."""
import ast
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import literales  # noqa: E402


def test_cero_literales_numericos_sospechosos_en_tools_y_precios():
    assert literales.sospechosos() == [], "las cifras de referencia deben vivir en referencias.yaml"


def test_la_app_no_hace_peticiones_de_red_en_tiempo_de_ejecucion():
    patrones = re.compile(r"\b(requests|urllib|httpx|aiohttp|http\.client|open_url|pyfetch|XMLHttpRequest|fetch\()")
    culpables = []
    for f in (RAIZ / "app").rglob("*.py"):
        for i, ln in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if patrones.search(ln) and not ln.strip().startswith("#"):
                culpables.append(f"{f.relative_to(RAIZ)}:{i}: {ln.strip()[:80]}")
    assert culpables == []
    for f in list((RAIZ / "app" / "www").glob("*.js")) + list((RAIZ / "app" / "www").glob("*.css")):
        assert "http://" not in f.read_text(encoding="utf-8") and "https://" not in f.read_text(encoding="utf-8"), f.name


def test_las_herramientas_no_importan_shiny():
    for f in (RAIZ / "app" / "tools").glob("t*.py"):
        arbol = ast.parse(f.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.module.split(".")[0] in ("shiny", "htmltools"):
                pytest.fail(f"{f.name} importa Shiny")
            if isinstance(nodo, ast.Import):
                assert not any(a.name.split(".")[0] in ("shiny", "htmltools") for a in nodo.names)


def test_el_nucleo_no_depende_de_shiny_ni_de_las_herramientas():
    for f in (RAIZ / "app" / "core").glob("*.py"):
        t = f.read_text(encoding="utf-8")
        assert "import shiny" not in t and "from shiny" not in t, f.name
        assert "from tools" not in t and "import tools" not in t, f.name


def test_solo_dependencias_disponibles_en_pyodide():
    permitidas = {"numpy", "pandas", "scipy", "matplotlib", "yaml", "shiny", "htmltools"}
    stdlib = set(sys.stdlib_module_names)
    locales = {"config", "graficos", "ui_comun", "core", "tools"}
    for f in (RAIZ / "app").rglob("*.py"):
        for nodo in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            mods = []
            if isinstance(nodo, ast.Import):
                mods = [a.name.split(".")[0] for a in nodo.names]
            elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
                mods = [nodo.module.split(".")[0]]
            for m in mods:
                assert m in permitidas | stdlib | locales, f"{f.name}: dependencia no permitida {m}"
    for prohibido in ("pulp", "pyomo", "highspy"):
        assert prohibido not in "".join(f.read_text(encoding="utf-8") for f in (RAIZ / "app").rglob("*.py")).lower()
