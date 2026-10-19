import numpy as np

from core.perfil import Perfil
from tools import t21_lcoe as t


def test_t21_resultados():
    res = t.calcular(t.inferir(Perfil(), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert len(res.tabla) == 4
    assert 15 < res.kpi("lcoe_solar_fv_utility").p50 < 150
    assert res.kpi("lcoe_solar_fv_utility").p50 < res.kpi("lcoe_solar_fv_residencial").p50 if "lcoe_solar_fv_residencial" in [k.id for k in res.kpis] else True


def test_t21_gas_caro_encarece_ciclo_combinado():
    a = t.calcular(t.inferir(Perfil(), {"gas": "bajo"}), 40, 1).kpi("lcoe_ciclo_combinado").p50
    b = t.calcular(t.inferir(Perfil(), {"gas": "alto"}), 40, 1).kpi("lcoe_ciclo_combinado").p50
    assert b > a


def test_t21_co2_sube_ciclo_combinado():
    sin = t.calcular(t.inferir(Perfil(), {"co2": "no"}), 40, 1).kpi("lcoe_ciclo_combinado").p50
    con = t.calcular(t.inferir(Perfil(), {"co2": "si"}), 40, 1).kpi("lcoe_ciclo_combinado").p50
    assert con > sin


def test_t21_solar_captura_menos_que_media():
    res = t.calcular(t.inferir(Perfil(), {}), 30)
    assert res.kpi("cap_solar").p50 < res.kpi("cap_media").p50
