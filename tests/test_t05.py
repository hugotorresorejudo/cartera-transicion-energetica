import numpy as np
import pytest

from core import termico
from core.perfil import Perfil
from tools import t05_acs as t


def test_energia_util_formula():
    # 100 L subiendo de 10 a 40 ºC = 1,163 · 100 · 30 / 1000 = 3,489 kWh
    q = termico.energia_util_mensual(np.array([100.0]), np.array([40.0]), np.full(12, 10.0))
    assert q[0, 0] == pytest.approx(3.489, abs=1e-3)


def test_cop_carnot_calibrado_reproduce_nominal():
    eta = termico.eta_carnot_desde_cop_nominal(3.3, 7.0, 55.0)
    assert termico.cop_carnot(7.0, 55.0, eta) == pytest.approx(3.3, rel=1e-6)
    assert termico.cop_carnot(20.0, 55.0, eta) > termico.cop_carnot(0.0, 55.0, eta)


def test_v60_equivalente():
    assert termico.v60_equivalente(100.0, 40.0, 10.0, 60.0) == pytest.approx(100 * 30 / 50)


def test_t05_resultados_coherentes():
    res = t.calcular(t.inferir(Perfil(personas="3-4"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    # la BdC consume bastante menos energía eléctrica que el termo: coste menor, CO2 menor
    assert res.kpi("c_bdc").p50 < res.kpi("c_termo").p50
    assert res.kpi("co2_bdc").p50 < res.kpi("co2_termo").p50
    assert 20 < res.kpi("v60").p50 < 250
    assert res.kpi("ahorro_prog").p50 >= -1


def test_t05_sistema_actual_gas_y_butano():
    for act in ("gas", "butano", "mixta", "nose"):
        r = t.calcular(t.inferir(Perfil(), {"actual": act}), 30)
        assert np.isfinite(r.kpi("van").p50)


def test_t05_mas_duchas_mas_coste():
    a = t.calcular(t.inferir(Perfil(), {"duchas": "<1"}), 40, 2).kpi("c_termo").p50
    b = t.calcular(t.inferir(Perfil(), {"duchas": ">1"}), 40, 2).kpi("c_termo").p50
    assert b > a
