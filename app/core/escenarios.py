"""Guardar/cargar escenarios JSON reproducibles y compararlos."""
from __future__ import annotations

import json

from .perfil import Perfil

VERSION = 1


def crear(herramienta: str, perfil: Perfil, respuestas: dict, editados: dict | None = None, n_mc: int = 500,
          semilla: int = 42, nombre: str = "", resultados=None) -> dict:
    esc = {"version": VERSION, "nombre": nombre or herramienta, "herramienta": herramienta, "perfil": perfil.to_dict(),
           "respuestas": respuestas, "editados": editados or {}, "n_mc": int(n_mc), "semilla": int(semilla)}
    if resultados is not None:
        esc["resumen"] = [{"id": k.id, "nombre": k.nombre, "unidad": k.unidad, "p10": k.p10, "p50": k.p50, "p90": k.p90,
                           "fmt": k.fmt} for k in resultados.kpis]
    return esc


def a_json(esc: dict) -> str:
    return json.dumps(esc, indent=1, ensure_ascii=False, sort_keys=True)


def de_json(txt: str) -> dict:
    esc = json.loads(txt)
    if esc.get("version") != VERSION:
        raise ValueError(f"Versión de escenario no soportada: {esc.get('version')}")
    return esc


def reproducir(esc: dict, modulo):
    """Recalcula un escenario con su semilla; mismos datos -> mismos resultados."""
    perfil = Perfil.from_dict(esc["perfil"])
    par = modulo.inferir(perfil, esc["respuestas"])
    for k, v in esc.get("editados", {}).items():
        if k in par.params:
            par.editar(k, v)
    return modulo.calcular(par, esc["n_mc"], esc["semilla"])


def comparar(escenarios: list[dict]) -> list[dict]:
    """Filas (una por KPI) con las columnas de hasta 3 escenarios para la vista lado a lado."""
    esc = escenarios[:3]
    ids = []
    for e in esc:
        for k in e.get("resumen", []):
            if k["id"] not in ids:
                ids.append(k["id"])
    filas = []
    for i in ids:
        fila = {"indicador": i}
        for j, e in enumerate(esc):
            k = next((k for k in e.get("resumen", []) if k["id"] == i), None)
            if k and "nombre_ind" not in fila:
                fila["indicador"] = k["nombre"]
            fila[e["nombre"] or f"Esc. {j + 1}"] = None if k is None else (k["p10"], k["p50"], k["p90"])
        filas.append(fila)
    return filas
