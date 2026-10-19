import numpy as np
import pytest

from core import carga
from core.perfil import Perfil
from tools import t04_ve as t


def test_voraz_coincide_con_linprog():
    rng = np.random.default_rng(3)
    for _ in range(20):
        k = 12
        p = rng.uniform(0.02, 0.4, k)
        E = rng.uniform(1, 30)
        x, c_lp = carga.plan_lp(p, np.ones(k), 3.7, E)
        c_v, falta, _ = carga.coste_voraz(p, 3.7, E)
        if x is None:
            assert falta > 0
        else:
            assert c_v == pytest.approx(c_lp, rel=1e-9)


def test_lp_respeta_disponibilidad_y_potencia():
    p = np.array([0.3, 0.1, 0.2, 0.05])
    a = np.array([1, 1, 1, 0])
    x, c = carga.plan_lp(p, a, 3.0, 5.0)
    assert x[3] == pytest.approx(0) and x.max() <= 3.0 + 1e-9 and x.sum() == pytest.approx(5.0)
    assert c == pytest.approx(3 * 0.1 + 2 * 0.2)


def test_t04_resultados():
    res = t.calcular(t.inferir(Perfil(), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert res.kpi("ahorro_carga").p50 >= 0
    assert 0.05 < res.kpi("ckm_ev").p50 < 0.6 and 0.05 < res.kpi("ckm_alt").p50 < 0.8
    assert res.kpi("dtco").prob is not None


def test_t04_mas_km_favorece_al_ve():
    poco = t.calcular(t.inferir(Perfil(), {"km_lab": "<20", "viajes": "ninguno"}), 60, 1).kpi("dtco").p50
    mucho = t.calcular(t.inferir(Perfil(), {"km_lab": "50-100", "viajes": "6-15"}), 60, 1).kpi("dtco").p50
    assert mucho > poco


def test_t04_calle_sin_ahorro_de_carga():
    res = t.calcular(t.inferir(Perfil(), {"parking": "calle"}), 40)
    assert res.kpi("ahorro_carga").p50 == pytest.approx(0)


def test_t04_todas_las_alternativas():
    for alt in ("gasolina", "diesel", "hibrido", "phev"):
        assert np.isfinite(t.calcular(t.inferir(Perfil(), {"alternativa": alt}), 30).kpi("dtco").p50)
