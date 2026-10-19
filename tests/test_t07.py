import numpy as np

from core.perfil import Perfil
from tools import t07_cargador as t


def test_t07_resultados():
    res = t.calcular(t.inferir(Perfil(equipos=["induccion"], potencia=4.6), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert len(res.tabla) >= 4
    assert res.kpi("p_rec").p50 >= 3


def test_t07_monofasico_limita_a_7_4():
    res = t.calcular(t.inferir(Perfil(), {"fases": "mono"}), 30)
    assert max(f["Cargador (kW)"] for f in res.tabla) <= 7.4
    res3 = t.calcular(t.inferir(Perfil(), {"fases": "tri"}), 30)
    assert max(f["Cargador (kW)"] for f in res3.tabla) == 11


def test_t07_mas_potencia_menos_horas():
    res = t.calcular(t.inferir(Perfil(), {"fases": "tri"}), 30)
    h = {f["Cargador (kW)"]: f["Horas de carga (P50)"] for f in res.tabla}
    assert h[3.7] > h[7.4] > h[11]
