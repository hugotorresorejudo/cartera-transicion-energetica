import numpy as np
import pytest

from core import datadis, perfiles_carga as pc
from core.perfil import Perfil
from tools import t16_datadis as t


def _csv(dias=40, sep=";", dec=","):
    filas = ["CUPS;Fecha;Hora;Consumo_kWh;Metodo_obtencion".replace(";", sep)]
    import datetime as dt
    d0 = dt.date(2023, 1, 1)
    for i in range(dias):
        d = d0 + dt.timedelta(days=i)
        for h in range(1, 25):
            v = 0.2 + (0.8 if 19 <= h <= 22 else 0.0)
            filas.append(sep.join(["ES0021", d.strftime("%d/%m/%Y"), str(h), f"{v:.3f}".replace(".", dec), "R"]))
    return "\n".join(filas)


def test_parseo_horas_y_decimales():
    d = datadis.parsear(_csv(3))
    assert len(d) == 72 and d["h"].min() == 0 and d["h"].max() == 23
    assert d["kwh"].sum() == pytest.approx(3 * (24 * 0.2 + 4 * 0.8), rel=1e-6)


def test_cuartohorario_se_suma():
    txt = "Fecha;Hora;Consumo_kWh\n" + "\n".join(f"01/02/2023;{h:02d}:{m:02d};0,25" for h in range(24) for m in (0, 15, 30, 45))
    d = datadis.parsear(txt)
    assert len(d) == 24 and d["kwh"].iloc[0] == pytest.approx(1.0)


def test_curva_anual_8760_y_estadisticos():
    curva, st = datadis.curva_anual(datadis.parsear(_csv(40)))
    assert curva.shape == (8760,) and curva.min() >= 0
    assert st["dias"] == 40 and not st["completo"]
    assert st["P1"] + st["P2"] + st["P3"] == pytest.approx(1.0, abs=1e-6)


def test_t16_con_y_sin_archivo():
    p = Perfil(factura="70-120", potencia=4.6)
    sin = t.calcular(t.inferir(p, {}), 40)
    assert np.isnan(sin.kpi("error").p50) and sin.kpi("coste_mejor").p50 > 0
    con = t.calcular(t.inferir(p, {"csv": _csv(60)}), 40)
    assert np.isfinite(con.kpi("error").p50) and con.kpi("E_real").p50 > 1000
    assert any("Curva leída" in n for n in con.notas)
