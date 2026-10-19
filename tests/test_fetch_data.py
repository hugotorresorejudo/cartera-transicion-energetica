"""Pruebas de scripts/fetch_data.py con respuestas simuladas (en el entorno de desarrollo no hay acceso a OMIE, REData ni PVGIS)."""
import datetime as dt
import json

import numpy as np
import pandas as pd
import pytest

import fetch_data as fd


class Resp:
    def __init__(self, texto="", js=None, status=200):
        self.text, self._js, self.status_code = texto, js, status

    def json(self):
        return self._js


def test_omie_cuartohorario_se_promedia_a_hora(monkeypatch):
    lineas = [f"2025;10;02;{p};{40.0 + p / 100:.2f};{50.0 + (p - 1) // 4:.2f};" for p in range(1, 97)] + ["*"]
    monkeypatch.setattr(fd, "get", lambda *a, **k: Resp("\n".join(lineas)))
    df = fd.omie_dia(dt.date(2025, 10, 2))
    assert len(df) == 24 and list(df["h"][:3]) == [1, 2, 3]
    assert df["es"].iloc[0] == pytest.approx(50.0) and df["es"].iloc[23] == pytest.approx(73.0)


def test_omie_horario_24_filas_y_dia_sin_fichero(monkeypatch):
    lineas = [f"2024;05;01;{h};60,5;61,5;" for h in range(1, 25)]
    monkeypatch.setattr(fd, "get", lambda *a, **k: Resp("\n".join(lineas)))
    df = fd.omie_dia(dt.date(2024, 5, 1))
    assert len(df) == 24 and df["es"].iloc[0] == pytest.approx(61.5)
    monkeypatch.setattr(fd, "get", lambda *a, **k: None)
    assert fd.omie_dia(dt.date(2024, 5, 2)) is None


def test_percentiles_omie_estructura(tmp_path, monkeypatch):
    monkeypatch.setattr(fd, "DATA", tmp_path)
    fechas = pd.date_range("2024-01-01", periods=60).strftime("%Y-%m-%d")
    df = pd.DataFrame([(f, h, 50.0 + h, 50.0) for f in fechas for h in range(1, 25)], columns=["fecha", "h", "es", "pt"])
    fd.percentiles_omie(df)
    d = json.loads((tmp_path / "omie_percentiles.json").read_text())
    assert "1|L|0" in d and len(d["1|L|0"]) == 3 and d["1|L|0"][0] <= d["1|L|0"][1] <= d["1|L|0"][2]


def test_redata_parsea_series(monkeypatch):
    js = {"included": [{"attributes": {"title": "PVPC", "values": [{"value": 100.0 + i, "datetime": f"2025-01-01T{i:02d}:00:00.000+01:00"} for i in range(24)]}}]}
    monkeypatch.setattr(fd, "get", lambda *a, **k: Resp(js=js))
    df = fd._redata("mercados/precios-mercados-tiempo-real", dt.date(2025, 1, 1), dt.date(2025, 1, 1))
    assert list(df.columns) == ["PVPC"] and len(df) == 24


def test_pvgis_provincia_genera_npz_compatible(tmp_path, monkeypatch):
    monkeypatch.setattr(fd, "DATA", tmp_path)
    (tmp_path / "pvgis").mkdir()

    def fake(url, params=None, **k):
        if url.endswith("seriescalc"):
            horas = []
            for a in (2016, 2017):
                for d in pd.date_range(f"{a}-01-01", f"{a}-12-31"):
                    for h in range(24):
                        horas.append({"time": f"{d:%Y%m%d}:{h:02d}10", "P": 800.0 if 9 <= h <= 15 else 0.0, "T2m": 15.0})
            return Resp(js={"outputs": {"hourly": horas}})
        t = [{"time(UTC)": f"2015{m:02d}01:0000", "T2m": 10.0 + m} for m in range(1, 13) for _ in range(730)]
        return Resp(js={"outputs": {"tmy_hourly": t[:8760]}})

    monkeypatch.setattr(fd, "get", fake)
    monkeypatch.setattr(fd.time, "sleep", lambda *_: None)
    monkeypatch.setattr(fd, "ANIOS_PVGIS", (2016, 2017))
    fila = {"codigo": "28", "lat": 40.4, "lon": -3.7}
    assert fd.fetch_pvgis_provincia(fila, forzar=True)
    z = np.load(tmp_path / "pvgis" / "pv_28.npz")
    assert z["y"].shape == (4, 5, 8760) and z["y"].dtype == np.uint16
    assert z["fy"].shape == (2, 12) and z["t2m"].shape == (8760,)
    assert z["y"][2, 2].max() > 0
