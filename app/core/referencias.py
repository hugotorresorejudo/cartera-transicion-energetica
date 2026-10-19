"""Carga, validación y rastreo de referencias.yaml (única fuente de cifras de referencia)."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import yaml

RUTA = Path(__file__).resolve().parent.parent / "data" / "referencias.yaml"
CAMPOS = ("valor", "unidad", "fuente", "url", "fecha_consulta", "verificado")


class ReferenciaError(KeyError):
    pass


def validar(datos: dict) -> list[str]:
    """Devuelve la lista de errores de esquema (vacía si es válido)."""
    errores = []
    for clave, e in datos.items():
        if not isinstance(e, dict):
            errores.append(f"{clave}: la entrada no es un mapa")
            continue
        for c in CAMPOS:
            if c not in e:
                errores.append(f"{clave}: falta '{c}'")
        if not isinstance(e.get("verificado"), bool):
            errores.append(f"{clave}: 'verificado' debe ser booleano")
        if e.get("verificado") is False and not e.get("nota"):
            errores.append(f"{clave}: verificado=false exige 'nota'")
        if e.get("verificado") is True and not (e.get("fuente") and e.get("url")):
            errores.append(f"{clave}: verificado=true exige fuente y url")
        if not e.get("fuente") or not e.get("url"):
            if e.get("verificado") is not False:
                errores.append(f"{clave}: sin fuente/url")
    return errores


class Referencias:
    def __init__(self, datos: dict):
        self._d = datos
        self._usadas: set[str] = set()

    def entrada(self, clave: str) -> dict:
        try:
            return self._d[clave]
        except KeyError as exc:
            raise ReferenciaError(f"Referencia inexistente: {clave}") from exc

    def get(self, clave: str):
        e = self.entrada(clave)
        self._usadas.add(clave)
        return e["valor"]

    def rango(self, clave: str) -> tuple[float, float, float]:
        """Rango [min, moda, max]; un escalar se devuelve como (v, v, v)."""
        v = self.get(clave)
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return float(v[0]), float(v[1]), float(v[2])
        if isinstance(v, (int, float)):
            return float(v), float(v), float(v)
        raise ReferenciaError(f"{clave} no es un rango [min, moda, max]")

    def sub(self, clave: str, k):
        """Elemento k de una referencia de tipo mapa."""
        v = self.get(clave)
        return v[k] if k in v else v[str(k)]

    def tiene(self, clave: str) -> bool:
        return clave in self._d

    def claves(self):
        return list(self._d)

    @contextmanager
    def rastrear(self):
        """Registra las claves consultadas dentro del bloque."""
        previo = self._usadas
        self._usadas = set()
        try:
            yield self._usadas
        finally:
            self._usadas = previo | self._usadas

    def pendientes(self, usadas) -> list[str]:
        return sorted(k for k in usadas if self._d.get(k, {}).get("verificado") is False)


def cargar(ruta: Path | str = RUTA) -> Referencias:
    with open(ruta, encoding="utf-8") as f:
        datos = yaml.safe_load(f) or {}
    return Referencias(datos)


_REF: Referencias | None = None


def ref() -> Referencias:
    global _REF
    if _REF is None:
        _REF = cargar()
    return _REF
