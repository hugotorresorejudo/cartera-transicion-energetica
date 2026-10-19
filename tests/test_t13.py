import numpy as np

from core.perfil import Perfil
from tools import t13_solar_termica as t


def test_t13_resultados():
    res = t.calcular(t.inferir(Perfil(cp="41001", personas="3-4"), {}), 50)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert 0 < res.kpi("frac").p90 <= 100


def test_t13_mas_captadores_mas_fraccion():
    a = t.calcular(t.inferir(Perfil(cp="41001"), {"captadores": "1"}), 40, 1).kpi("frac").p50
    b = t.calcular(t.inferir(Perfil(cp="41001"), {"captadores": "3+"}), 40, 1).kpi("frac").p50
    assert b > a


def test_t13_sur_supera_a_norte_en_fraccion():
    sur = t.calcular(t.inferir(Perfil(cp="41001"), {}), 40, 2).kpi("frac").p50
    norte = t.calcular(t.inferir(Perfil(cp="15001"), {}), 40, 2).kpi("frac").p50
    assert sur > norte
