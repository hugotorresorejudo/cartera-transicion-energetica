"""Busca literales numéricos sospechosos (cifras de referencia) en app/tools/ y app/core/precios.py."""
import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "app"
# Estructurales o físicos admitidos: índices, contadores, conversiones de unidad, percentiles, tamaños de matriz y constantes físicas.
PERMITIDOS = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 24, 50, 52, 60, 90, 100, 168, 365, 500, 1000, 8760, 0.5, 1.0, 0.0, 2.0, 10.0, 100.0, 1e-9, 1e-6, 1e-12, 1.5}
# 500: N por defecto del Monte Carlo (configurable); 52: semanas/año; 16: tamaño de caché; 13: límite de range() de 12 meses.
# Constantes físicas con nombre propio
FISICAS = {1.163, 273.15}


def sospechosos():
    res = []
    objetivos = sorted((RAIZ / "tools").glob("t*.py")) + [RAIZ / "core" / "precios.py"]
    for f in objetivos:
        arbol = ast.parse(f.read_text(encoding="utf-8"))
        # Ignora docstrings y los f-strings: solo Constant numéricas
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)) and not isinstance(nodo.value, bool):
                v = nodo.value
                if v in PERMITIDOS or v in FISICAS:
                    continue
                res.append((f.name, nodo.lineno, v))
    return res


if __name__ == "__main__":
    for r in sospechosos():
        print(r)
