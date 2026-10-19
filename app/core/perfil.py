"""Perfil único "Mi hogar", versionado y compartido por todas las herramientas."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields

VERSION = 1

VIVIENDAS = [
    ("piso_<70", "Piso de menos de 70 m²"),
    ("piso_70_120", "Piso de 70 a 120 m²"),
    ("piso_>120", "Piso de más de 120 m²"),
    ("unif_<120", "Unifamiliar de menos de 120 m²"),
    ("unif_>120", "Unifamiliar de más de 120 m²"),
]
PERSONAS = [("1", "1"), ("2", "2"), ("3-4", "3 o 4"), ("5+", "5 o más")]
OCUPACION = [("fuera", "Fuera en horario laboral"), ("parcial", "Teletrabajo parcial"),
             ("casa", "Casi siempre en casa")]
EQUIPOS = [("induccion", "Cocina de inducción"), ("horno", "Horno eléctrico"),
           ("termo_electrico", "Termo eléctrico"), ("aire_acondicionado", "Aire acondicionado"),
           ("calefaccion_electrica", "Calefacción eléctrica"), ("ve", "Vehículo eléctrico"),
           ("piscina", "Piscina")]
FACTURA = [("<40", "Menos de 40 €"), ("40-70", "40–70 €"), ("70-120", "70–120 €"),
           (">120", "Más de 120 €"), ("nose", "No lo sé")]
LIMITADOR = [("nunca", "Nunca"), ("alguna", "Alguna vez al año"), ("a_menudo", "A menudo")]


@dataclass
class Perfil:
    version: int = VERSION
    cp: str = "28001"
    vivienda: str = "piso_70_120"
    personas: str = "2"
    ocupacion: str = "parcial"
    equipos: list = field(default_factory=list)
    factura: str = "nose"
    potencia: float | None = None  # kW contratados; None = "no sé"
    limitador: str = "nunca"

    @property
    def unifamiliar(self) -> bool:
        return self.vivienda.startswith("unif")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Perfil":
        nombres = {f.name for f in fields(cls)}
        p = cls(**{k: v for k, v in d.items() if k in nombres})
        p.version = VERSION
        return p


def aplicar(perfil: Perfil, campo: str, valor) -> None:
    """Asigna una respuesta de formulario al campo del perfil (la potencia 'nose' -> None)."""
    if campo == "potencia":
        perfil.potencia = None if valor in (None, "", "nose") else float(valor)
    elif campo == "equipos":
        perfil.equipos = list(valor)
    else:
        setattr(perfil, campo, valor)
