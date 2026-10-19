import numpy as np

from core.perfil import Perfil
from tools import t08_aerotermia as t


def test_t08_resultados_y_orden():
    res = t.calcular(t.inferir(Perfil(cp="28001", vivienda="piso_70_120"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    # radiadores eléctricos son el sistema más caro y la aerotermia más barata que ellos
    assert res.kpi("c_electrica").p50 > res.kpi("c_aero").p50
    assert res.kpi("c_electrica").p50 > res.kpi("c_gas").p50


def test_t08_actual_electrica_da_mayor_ahorro_que_gas():
    g = t.calcular(t.inferir(Perfil(), {"actual": "gas"}), 50, 1).kpi("ahorro").p50
    e = t.calcular(t.inferir(Perfil(), {"actual": "electrica"}), 50, 1).kpi("ahorro").p50
    assert e > g


def test_t08_clima_frio_mas_demanda():
    frio = t.calcular(t.inferir(Perfil(cp="09001"), {}), 40, 2).kpi("c_gas").p50
    calido = t.calcular(t.inferir(Perfil(cp="29001"), {}), 40, 2).kpi("c_gas").p50
    assert frio > calido
