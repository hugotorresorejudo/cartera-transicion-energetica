#!/usr/bin/env python3
"""Genera datos SINTÉTICOS de demostración en app/data/ (marcados con sintetico=true en meta.json).

Solo sirve para ejecutar y probar la app sin conexión a OMIE/REData/PVGIS. NO son datos reales: el workflow
`data.yml` (scripts/fetch_data.py) los sustituye por los reales. La UI muestra un aviso mientras `sintetico` sea true."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "app" / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
TILTS = [0, 15, 30, 45]
AZIMS = [-90, -45, 0, 45, 90]
DIAS_MES = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def geometria(lat, lon, n_dias=365):
    doy = np.repeat(np.arange(n_dias) + 1, 24)
    hora = np.tile(np.arange(24), n_dias) + 0.5
    decl = np.radians(23.45) * np.sin(2 * np.pi * (284 + doy) / 365)
    ts = hora - 1.0 + lon / 15.0  # hora solar aproximada (CET - 1 h + corrección de longitud)
    w = np.radians(15 * (ts - 12))
    phi = np.radians(lat)
    cosz = np.sin(phi) * np.sin(decl) + np.cos(phi) * np.cos(decl) * np.cos(w)
    return doy, decl, w, phi, np.clip(cosz, 0, 1)


def pv_combo(lat, lon, tilt, az, kt_mes, nube):
    """kW por kWp de una superficie (tilt, az) con cielo claro de Meinel modulado por nubosidad."""
    doy, decl, w, phi, cosz = geometria(lat, lon)
    beta, gam = np.radians(tilt), np.radians(az)
    cos_inc = (np.sin(decl) * np.sin(phi) * np.cos(beta) - np.sin(decl) * np.cos(phi) * np.sin(beta) * np.cos(gam)
               + np.cos(decl) * np.cos(phi) * np.cos(beta) * np.cos(w)
               + np.cos(decl) * np.sin(phi) * np.sin(beta) * np.cos(gam) * np.cos(w)
               + np.cos(decl) * np.sin(beta) * np.sin(gam) * np.sin(w))
    cos_inc = np.clip(cos_inc, 0, 1)
    am = 1.0 / np.maximum(cosz, 0.05)
    dni = np.where(cosz > 0.02, 1353 * 0.7 ** (am ** 0.678), 0.0)
    dhi = 0.12 * dni * cosz + 20 * (cosz > 0.02)
    mes = np.repeat(np.repeat(np.arange(12), DIAS_MES), 24)
    k = kt_mes[mes] * nube
    g = k * (dni * cos_inc + dhi * (1 + np.cos(beta)) / 2 + 0.2 * (dni * cosz + dhi) * (1 - np.cos(beta)) / 2)
    return np.clip(g / 1000.0 * 1.2, 0, 1.0)


def t2m_tipica(lat, alt, rng):
    mes = np.repeat(np.repeat(np.arange(12), DIAS_MES), 24)
    hora = np.tile(np.arange(24), 365)
    doy = np.repeat(np.arange(365), 24)
    anual = 19.5 - 0.42 * (lat - 36) - 0.0065 * alt
    est = -(8.5 + 0.1 * (lat - 36)) * np.cos(2 * np.pi * (doy - 20) / 365)
    diurno = 4.5 * np.sin(2 * np.pi * (hora - 9) / 24)
    return anual + est + diurno + rng.normal(0, 0.5, 8760)


def sintetico_pv(prov):
    rng = np.random.default_rng(int(prov["codigo"]) * 7 + 1)
    lat, lon, alt = prov["lat"], prov["lon"], prov["altitud_m"]
    claridad = np.clip(0.80 - 0.0105 * (lat - 36) - 0.07, 0.62, 0.9)
    kt = claridad * (1 + 0.10 * np.cos(2 * np.pi * (np.arange(12) - 6.5) / 12))
    doy = np.repeat(np.arange(365), 24)
    nube_dia = np.clip(1 - 0.35 * np.abs(rng.standard_normal(365)) * (1.15 - 0.6 * np.sin(np.pi * np.arange(365) / 365)), 0.25, 1.0)
    nube = nube_dia[doy]
    y = np.zeros((4, 5, 8760), dtype=np.uint16)
    for i, tl in enumerate(TILTS):
        for j, az in enumerate(AZIMS):
            if tl == 0 and j > 0:
                y[i, j] = y[i, 0]
                continue
            y[i, j] = np.round(pv_combo(lat, lon, tl, az, kt, nube) * 1e4)
    fy = np.exp(rng.normal(0, 0.05, (8, 12))).astype(np.float32)
    t2 = t2m_tipica(lat, alt, rng)
    ruta = DATA / "pvgis"
    ruta.mkdir(exist_ok=True)
    np.savez_compressed(ruta / f"pv_{prov['codigo']}.npz", y=y, fy=fy, t2m=np.round(t2 * 10).astype(np.int16),
                        anios=np.arange(2016, 2024))


def fundamentos(anio, rng, gas_factor):
    """Series horarias sintéticas coherentes: solar, eólica, demanda y precio por orden de mérito simplificado."""
    n = 366 if (anio % 4 == 0) else 365
    doy = np.repeat(np.arange(n), 24)
    hora = np.tile(np.arange(24), n)
    sol_clear = pv_combo(40.0, -3.7, 30, 0, np.full(12, 1.0), np.ones(8760))
    sol_clear = np.resize(sol_clear, n * 24) if n == 365 else np.concatenate([sol_clear, sol_clear[:24]])
    nube = np.clip(1 - 0.4 * np.abs(rng.standard_normal(n)), 0.2, 1)[doy]
    solar = 30000 * sol_clear * nube
    ar = np.zeros(n)
    for i in range(1, n):
        ar[i] = 0.85 * ar[i - 1] + rng.normal(0, 0.5)
    viento = 6500 + 4800 * np.repeat(ar, 24) / 1.5 * 1.0 + 1500 * rng.standard_normal(n * 24) * 0.3 + 2000 * np.cos(2 * np.pi * (doy - 30) / 365)
    viento = np.clip(viento, 500, 20000)
    forma = np.array([.74, .70, .67, .66, .66, .69, .75, .83, .92, .97, 1, 1, 1, .99, .96, .93, .92, .94, .98, 1.03, 1.05, 1.02, .93, .82])
    demanda = 29000 * forma[hora] * (1 + 0.12 * np.abs(np.cos(2 * np.pi * (doy - 10) / 365)) ** 2)
    nuclear, hidro = 6000.0, 2500 + 1500 * np.cos(2 * np.pi * (doy - 90) / 365) ** 2
    residual = demanda - solar - viento - nuclear - hidro
    cc = np.clip(residual, 0, None)
    precio = gas_factor * (22 + 62 * (cc / 14000) ** 1.3) + rng.normal(0, 4, n * 24)
    precio = np.where(residual < 0, np.clip(precio * 0.1 - 2 * np.abs(residual) / 4000, -3, 6), precio)
    precio = np.clip(precio, -5, 250)
    return n, dict(solar=solar, viento=viento, demanda=demanda, nuclear=np.full(n * 24, nuclear), hidro=hidro, cc=cc, precio=precio)


def generar():
    DATA.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today()
    anios = list(range(hoy.year - 3, hoy.year + 1))
    filas, fund_ult = [], None
    for k, a in enumerate(anios):
        rng = np.random.default_rng(100 + a)
        n, f = fundamentos(a, rng, gas_factor=[1.05, 0.95, 1.0, 1.0][k % 4])
        dias = pd.date_range(f"{a}-01-01", periods=n)
        if a == hoy.year:
            dias = dias[dias.date <= hoy]
        for i, d in enumerate(dias):
            for h in range(24):
                filas.append((d.date().isoformat(), h + 1, round(float(f["precio"][i * 24 + h]), 2),
                              round(float(f["precio"][i * 24 + h]) * 1.0, 2)))
        fund_ult = (a, n, f, dias)
    omie = pd.DataFrame(filas, columns=["fecha", "h", "es", "pt"])
    omie.to_csv(DATA / "omie_es_horario.csv.gz", index=False, compression="gzip")
    # REData sintético: últimos 12 meses
    a, n, f, dias = fund_ult
    idx = pd.date_range(pd.Timestamp(dias[0]), periods=len(dias) * 24, freq="h")
    d = pd.DataFrame({"ts": idx, "p_Precio mercado spot": f["precio"][:len(idx)] / 1000.0,
                      "g_Solar fotovoltaica": f["solar"][:len(idx)], "g_Eólica": f["viento"][:len(idx)],
                      "g_Nuclear": f["nuclear"][:len(idx)], "g_Hidráulica": f["hidro"][:len(idx)],
                      "g_Ciclo combinado": f["cc"][:len(idx)], "d_Demanda real": f["demanda"][:len(idx)]})
    d["p_PVPC"] = (d["p_Precio mercado spot"] * 0.45 + d["p_Precio mercado spot"].mean() * 0.55 + 0.02) * 1.13 + 0.05
    d["e_tCO2 eq."] = d["g_Ciclo combinado"] * 0.37
    d.round(4).to_csv(DATA / "redata_horario.csv.gz", index=False, compression="gzip")
    import fetch_data  # reutiliza el agregado de percentiles
    fetch_data.DATA = DATA
    fetch_data.percentiles_omie(omie)
    # PVGIS
    provs = pd.read_csv(DATA / "provincias.csv", dtype={"codigo": str})
    for _, p in provs.iterrows():
        sintetico_pv(p)
    # curvas OMIE sintéticas (escalera de oferta por tecnologías)
    curvas = []
    rng = np.random.default_rng(7)
    for mes in range(1, 13):
        for hora in (4, 14, 21):
            solar = 22000 * (hora == 14) * rng.uniform(0.5, 1.0)
            tec = [("Solar FV", 0.0, solar), ("Eólica", 0.5, rng.uniform(2000, 12000)), ("Nuclear", 8.0, 6000.0),
                   ("Hidráulica", 35.0, rng.uniform(1500, 5000)), ("Cogeneración", 70.0, 2500.0),
                   ("Ciclo combinado", 95.0, 14000.0), ("Carbón y otras", 140.0, 1500.0), ("Reserva", 400.0, 3000.0)]
            acum, oferta = 0.0, []
            for nombre, c, mw in tec:
                oferta.append({"tecnologia": nombre, "mw": round(float(mw), 1), "precio": c})
            demanda = [{"mw": round(float(29000 * (0.7 if hora == 4 else 1.0) * rng.uniform(0.9, 1.1)), 1), "precio": 4000}]
            curvas.append({"fecha": f"2025-{mes:02d}-15", "hora": hora, "oferta": oferta, "demanda_mw": demanda[0]["mw"]})
    (DATA / "curvas_omie.json").write_text(json.dumps(curvas))
    (DATA / "meta.json").write_text(json.dumps({
        "actualizado": hoy.isoformat(), "sintetico": True,
        "aviso": "Datos sintéticos de demostración generados por scripts/generar_sintetico.py; ejecuta scripts/fetch_data.py para los reales.",
        "fuentes": {}}, indent=1, ensure_ascii=False))
    print("sintético generado en", DATA)


if __name__ == "__main__":
    generar()
