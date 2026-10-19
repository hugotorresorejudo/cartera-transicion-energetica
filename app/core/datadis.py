"""Lectura de la curva de carga descargada de Datadis (CSV) y conversión a un año tipo de 8760 horas."""
from __future__ import annotations

import io

import numpy as np
import pandas as pd

from .calendario import calendario_tipico


class DatadisError(ValueError):
    pass


def _col(df: pd.DataFrame, *claves: str):
    for c in df.columns:
        n = c.strip().lower().replace("_", " ")
        if any(k in n for k in claves):
            return c
    return None


def parsear(texto: str) -> pd.DataFrame:
    """CSV de Datadis (separador ';' o ',', decimal ','; fecha DD/MM/YYYY; hora 1-24/25 o HH:MM).

    Devuelve un DataFrame horario con columnas fecha (date), h (0-23) y kwh; los datos cuartohorarios se suman por hora."""
    primera = texto.lstrip("﻿").splitlines()[0] if texto.strip() else ""
    sep = ";" if primera.count(";") >= primera.count(",") else ","
    df = pd.read_csv(io.StringIO(texto.lstrip("﻿")), sep=sep, dtype=str)
    cf, ch, cc = _col(df, "fecha", "date"), _col(df, "hora", "hour"), _col(df, "consumo", "kwh", "energ")
    if not (cf and ch and cc):
        raise DatadisError("No se encuentran las columnas Fecha, Hora y Consumo del CSV de Datadis")
    fecha = pd.to_datetime(df[cf], dayfirst=True, errors="coerce")
    horas = df[ch].str.strip()
    if horas.str.contains(":").any():
        hh = horas.str.split(":").str[0].astype(float)
        h = np.where(horas.str.split(":").str[1].astype(float) == 0, hh - 0, hh)  # 'HH:MM' de inicio de intervalo
        h = np.clip(h, 0, 23)
    else:
        h = np.clip(horas.astype(float) - 1, 0, 23)
    kwh = pd.to_numeric(df[cc].str.replace(",", ".", regex=False), errors="coerce")
    d = pd.DataFrame({"fecha": fecha.dt.date, "h": h.astype(int), "kwh": kwh}).dropna()
    if d.empty:
        raise DatadisError("El CSV no contiene datos válidos")
    return d.groupby(["fecha", "h"], as_index=False)["kwh"].sum()


def curva_anual(d: pd.DataFrame) -> tuple[np.ndarray, dict]:
    """(curva de 8760 kWh, estadísticas): los días medidos se colocan en su fecha y los que faltan se completan con el perfil
    medio por mes, tipo de día y hora (o el global si falta el mes)."""
    cal = calendario_tipico()
    mes, dow, hora = cal["mes"], cal["dia_semana"], cal["hora"]
    f = pd.to_datetime(d["fecha"])
    d = d.assign(mes=f.dt.month - 1, finde=(f.dt.weekday >= 5).astype(int), doy=f.dt.dayofyear)
    # sin 29-feb
    d = d[~((f.dt.month == 2) & (f.dt.day == 29))]
    n_dias = d["fecha"].nunique()
    energia_obs = d["kwh"].sum()
    perfil_mes = d.groupby(["mes", "finde", "h"])["kwh"].mean()
    perfil_glob = d.groupby(["finde", "h"])["kwh"].mean()
    curva = np.zeros(8760, dtype=np.float32)
    finde_ref = (dow >= 5).astype(int)
    for i in range(8760):
        v = perfil_mes.get((mes[i], finde_ref[i], hora[i]))
        curva[i] = perfil_glob.get((finde_ref[i], hora[i]), 0.0) if v is None or np.isnan(v) else v
    # valores medidos sobre los calculados
    base = pd.Timestamp("2023-01-01")
    idx = ((pd.to_datetime(d["fecha"]).dt.dayofyear - 1) * 24 + d["h"]).to_numpy()
    ok = (idx >= 0) & (idx < 8760)
    bis = (pd.to_datetime(d["fecha"]).dt.year % 4 == 0) & (pd.to_datetime(d["fecha"]).dt.month > 2)
    idx = np.where(bis.to_numpy(), idx - 24, idx)
    ok &= (idx >= 0) & (idx < 8760)
    curva[idx[ok]] = d["kwh"].to_numpy()[ok]
    per = cal["periodo"]
    tot = float(curva.sum())
    stats = {"dias": int(n_dias), "E_anual": tot, "E_medido": float(energia_obs), "completo": bool(n_dias >= 360),
             "pmax_kw": float(d["kwh"].max()), "P1": float(curva[per == 0].sum() / tot), "P2": float(curva[per == 1].sum() / tot),
             "P3": float(curva[per == 2].sum() / tot)}
    return curva, stats
