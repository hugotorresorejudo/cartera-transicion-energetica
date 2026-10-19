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


CATALOGO = {
    "t01": ("Tarifas y potencia contratada", "¿PVPC, fija o indexada? ¿Qué potencia contratar?"),
    "t02": ("Autoconsumo fotovoltaico", "¿Compensa instalar placas, de qué potencia y cuánto ahorras?"),
    "t03": ("Explorador de precios OMIE", "Cuándo es barata la luz y cuánto vale un kWh solar."),
    "t04": ("Vehículo eléctrico: TCO y carga", "Coste total frente a gasolina, diésel o híbrido y cuándo cargar."),
    "t05": ("ACS: bomba de calor vs termo o gas", "Agua caliente: coste, VAN del cambio y emisiones."),
    "t06": ("Batería doméstica", "¿Compensa añadir almacenamiento a tus placas?"),
    "t07": ("Cargador doméstico y potencia", "Potencia del cargador y de tu contrato para el coche eléctrico."),
    "t08": ("Aerotermia vs caldera", "Calefacción y ACS: aerotermia frente a caldera de gas."),
    "t09": ("Inducción vs gas", "Cocina: placa de inducción frente a gas."),
    "t10": ("Huella de carbono doméstica", "Emisiones anuales de tu hogar y qué las reduce."),
    "t11": ("Ayudas y deducciones", "IRPF, IBI, ICIO y ayudas Next Generation."),
    "t12": ("Rehabilitación de envolvente", "Aislamiento y ventanas: ahorro y retorno."),
    "t13": ("Solar térmica", "Captadores para agua caliente: ahorro y retorno."),
    "t14": ("Autoconsumo colectivo", "Comunidad energética o autoconsumo compartido en un bloque."),
    "t15": ("Desplazamiento de cargas", "Cuándo poner lavadora, lavavajillas o termo."),
    "t16": ("Calibración con Datadis", "Sube tu curva de carga real y afina las cifras."),
    "t17": ("Señal horaria de mix y emisiones", "Cuándo consumir para emitir menos CO₂."),
    "t18": ("Climatización de verano", "Split o bomba de calor reversible: consumo y coste."),
    "t19": ("Inventario y consumo fantasma", "A dónde va tu consumo y cuánto es stand-by."),
    "t20": ("Curvas agregadas OMIE", "Cómo se forma el precio marginal del mercado diario."),
    "t21": ("Explorador de LCOE", "Coste nivelado de cada tecnología frente al precio capturado."),
    "t22": ("Tarifa de gas y butano", "TUR frente a mercado libre y butano."),
}
