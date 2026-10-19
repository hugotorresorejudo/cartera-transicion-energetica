import numpy as np

from core.perfil import Perfil
from tools import t22_gas as t


def test_t22_resultados():
    res = t.calcular(t.inferir(Perfil(personas="3-4"), {"usos": ["cocina", "acs", "calefaccion"]}), 80)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert 300 < res.kpi("E").p50 < 20000
    assert res.kpi("c_tur").p50 > res.kpi("E").p50 * 0.03


def test_t22_factura_calibra_consumo():
    bajo = t.calcular(t.inferir(Perfil(), {"factura": "<20"}), 60, 1).kpi("E").p50
    alto = t.calcular(t.inferir(Perfil(), {"factura": ">80"}), 60, 1).kpi("E").p50
    assert alto > bajo


def test_t22_tabla_y_grafico():
    res = t.calcular(t.inferir(Perfil(), {}), 30)
    assert len(res.tabla) == 3 and res.graficos
