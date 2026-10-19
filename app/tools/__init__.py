"""Registro de herramientas T01…T22 (carga perezosa para arrancar rápido en Pyodide)."""
from __future__ import annotations

import importlib

CATEGORIAS = [
    ("Electricidad y mercado", ["t01", "t03", "t15", "t16", "t17", "t19", "t20"]),
    ("Autoconsumo y almacenamiento", ["t02", "t06", "t14", "t21"]),
    ("Movilidad", ["t04", "t07"]),
    ("Climatización y agua caliente", ["t05", "t08", "t09", "t12", "t13", "t18", "t22"]),
    ("Balance y ayudas", ["t10", "t11"]),
]

MODULOS = {
    "t01": "t01_tarifas", "t02": "t02_fv", "t03": "t03_omie", "t04": "t04_ve", "t05": "t05_acs",
    "t06": "t06_bateria", "t07": "t07_cargador", "t08": "t08_aerotermia", "t09": "t09_induccion",
    "t10": "t10_huella", "t11": "t11_ayudas", "t12": "t12_envolvente", "t13": "t13_solar_termica",
    "t14": "t14_comunidad", "t15": "t15_desplazamiento", "t16": "t16_datadis", "t17": "t17_emisiones",
    "t18": "t18_climatizacion", "t19": "t19_inventario", "t20": "t20_curvas", "t21": "t21_lcoe", "t22": "t22_gas",
}

PRIORIDAD = {t: 1 for t in ("t01", "t02", "t03", "t04", "t05")}
PRIORIDAD.update({t: 2 for t in ("t06", "t07", "t08", "t09", "t10", "t11", "t15", "t16", "t17", "t18", "t19", "t22")})
PRIORIDAD.update({t: 3 for t in ("t12", "t13", "t14", "t20", "t21")})


def cargar(id_: str):
    return importlib.import_module(f"tools.{MODULOS[id_.lower()]}")


def todos() -> list[str]:
    return sorted(MODULOS)
