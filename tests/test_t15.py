import numpy as np

from core.perfil import Perfil
from tools import t15_desplazamiento as t


def test_t15_resultados():
    res = t.calcular(t.inferir(Perfil(), {"aparatos": ["lavadora", "lavavajillas", "secadora", "termo"], "habitual": "tarde"}), 50)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert res.kpi("ahorro").p50 > 0
    assert len(res.tabla) == 4


def test_t15_precio_fijo_no_ahorra():
    res = t.calcular(t.inferir(Perfil(), {"tarifa": "fija"}), 30)
    assert abs(res.kpi("ahorro").p50) < 1e-3


def test_t15_ventana_amplia_ahorra_mas():
    a = t.calcular(t.inferir(Perfil(), {"ventana": "noche", "habitual": "tarde"}), 40, 1).kpi("ahorro").p50
    b = t.calcular(t.inferir(Perfil(), {"ventana": "cualquiera", "habitual": "tarde"}), 40, 1).kpi("ahorro").p50
    assert b >= a - 1e-9
