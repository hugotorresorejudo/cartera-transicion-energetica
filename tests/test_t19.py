import numpy as np

from core.perfil import Perfil
from tools import t19_inventario as t


def test_t19_resultados():
    res = t.calcular(t.inferir(Perfil(personas="3-4"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert res.kpi("standby").p50 > 0 and len(res.tabla) >= 8


def test_t19_apagar_reduce_standby():
    a = t.calcular(t.inferir(Perfil(), {"apagas": "si"}), 40, 1).kpi("standby").p50
    b = t.calcular(t.inferir(Perfil(), {"apagas": "no"}), 40, 1).kpi("standby").p50
    assert a < b


def test_t19_antiguos_consumen_mas():
    a = t.calcular(t.inferir(Perfil(), {"edad": "nuevos"}), 40, 1).kpi("total").p50
    b = t.calcular(t.inferir(Perfil(), {"edad": "antiguos"}), 40, 1).kpi("total").p50
    assert b > a
