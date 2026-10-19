"""Calendario horario: festivos nacionales, tipo de día y periodo 2.0TD para un año de 8760 h."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np

from .referencias import ref


ANIO_TIPO = 2023  # año no bisiesto (8760 h) para perfiles y periodos


def pascua(anio: int) -> date:
    """Domingo de Pascua (algoritmo anónimo gregoriano)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(anio, mes, dia)


def festivos(anio: int) -> set[date]:
    fijos = ref().get("tarifa.festivos_nacionales_fijos")
    out = {date(anio, int(s[:2]), int(s[3:5])) for s in fijos}
    out.add(pascua(anio) - timedelta(days=2))  # Viernes Santo
    return out


def calendario(anio: int, sin_bisiesto: bool = True) -> dict[str, np.ndarray]:
    """Arrays por hora: mes (0-11), dia_semana (0=lunes), hora (0-23), dia_anio, festivo(bool), periodo (0,1,2 = P1,P2,P3)."""
    d0, d1 = date(anio, 1, 1), date(anio + 1, 1, 1)
    dias = [d0 + timedelta(days=i) for i in range((d1 - d0).days)]
    if sin_bisiesto:
        dias = [d for d in dias if not (d.month == 2 and d.day == 29)]
    fest = festivos(anio)
    mes = np.repeat([d.month - 1 for d in dias], 24)
    dow = np.repeat([d.weekday() for d in dias], 24)
    esf = np.repeat([d in fest for d in dias], 24)
    hora = np.tile(np.arange(24), len(dias))
    doy = np.repeat(np.arange(len(dias)), 24)
    laborable = (dow < 5) & ~esf
    hp = ref().get("tarifa.horas_periodos")
    tabla = np.full(24, 2)
    for h in hp["P2_llano_laborables"]:
        tabla[h] = 1
    for h in hp["P1_punta_laborables"]:
        tabla[h] = 0
    periodo = np.where(laborable, tabla[hora], 2)
    return {"mes": mes, "dia_semana": dow, "hora": hora, "dia_anio": doy, "festivo": esf,
            "laborable": laborable, "periodo": periodo}


def anio_de(fechas) -> np.ndarray:
    """Año de cada fecha (datetime64[D])."""
    return np.asarray(fechas, dtype="datetime64[D]").astype("datetime64[Y]").astype(int) + 1970


def indices_hora_tipo(fechas) -> np.ndarray:
    """(nd, 24) índice de hora del año tipo (0..8759) de cada hora de las fechas dadas; el 29-feb se asimila al 28-feb."""
    d = np.asarray(fechas, dtype="datetime64[D]")
    doy = (d - d.astype("datetime64[Y]")).astype(int)
    bis = (anio_de(d) % 4 == 0)
    doy = np.where(bis & (doy >= 59), doy - 1, doy)
    doy = np.clip(doy, 0, 364)
    return doy[:, None] * 24 + np.arange(24)[None, :]


def calendario_tipico() -> dict[str, np.ndarray]:
    """Año no bisiesto de referencia para perfiles sintéticos (2023 no tiene 29-feb)."""
    return calendario(ANIO_TIPO)
