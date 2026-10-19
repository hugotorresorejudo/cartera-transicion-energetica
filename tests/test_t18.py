import numpy as np

from core.perfil import Perfil
from tools import t18_climatizacion as t


def test_t18_resultados():
    res = t.calcular(t.inferir(Perfil(cp="41001"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    e = {f["Equipo"]: f["Consumo P50 (kWh/año)"] for f in res.tabla}
    assert e["Split antiguo"] > e["Split inverter eficiente"] > e["Multisplit reversible"] * 0.9
    assert res.kpi("ahorro").p50 > 0


def test_t18_mas_uso_mas_consumo():
    a = t.calcular(t.inferir(Perfil(cp="41001"), {"uso": "poco"}), 40, 1).kpi("e_ef").p50
    b = t.calcular(t.inferir(Perfil(cp="41001"), {"uso": "mucho"}), 40, 1).kpi("e_ef").p50
    assert b > a


def test_t18_sur_mas_demanda_que_norte():
    sur = t.calcular(t.inferir(Perfil(cp="41001"), {}), 40, 2).kpi("util").p50
    norte = t.calcular(t.inferir(Perfil(cp="33001"), {}), 40, 2).kpi("util").p50
    assert sur > norte
