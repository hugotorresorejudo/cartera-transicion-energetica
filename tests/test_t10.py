import numpy as np

from core.perfil import Perfil
from tools import t10_huella as t


def test_t10_resultados():
    res = t.calcular(t.inferir(Perfil(personas="2"), {"gas_usos": ["cocina", "acs"]}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert 0.5 < res.kpi("total").p50 < 20
    assert len(res.tabla) == 4


def test_t10_eliminar_coche_reduce():
    con = t.calcular(t.inferir(Perfil(), {"coche": "gasolina"}), 40, 1).kpi("total").p50
    sin = t.calcular(t.inferir(Perfil(), {"coche": "ninguno"}), 40, 1).kpi("total").p50
    assert con > sin


def test_t10_ve_emite_menos_que_gasolina():
    g = t.calcular(t.inferir(Perfil(), {"coche": "gasolina"}), 40, 1)
    v = t.calcular(t.inferir(Perfil(), {"coche": "ve"}), 40, 1)
    assert v.kpi("total").p50 < g.kpi("total").p50
