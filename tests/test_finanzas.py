import numpy as np
import pytest

from core import finanzas as f


def test_van_caso_de_libro():
    # -1000 + 500/1.1 + 500/1.21 + 500/1.331 = 243.426...
    assert f.van([-1000, 500, 500, 500], 0.10) == pytest.approx(243.4261, abs=1e-3)


def test_van_r_cero_es_suma():
    assert f.van([-100, 30, 30, 60], 0.0) == pytest.approx(20.0)


def test_van_vectorizado_en_tasas():
    flujos = np.tile([-1000.0, 500, 500, 500], (3, 1))
    v = f.van(flujos, np.array([0.0, 0.10, 0.20]))
    assert v[0] == pytest.approx(500.0)
    assert v[1] == pytest.approx(243.4261, abs=1e-3)
    assert v[2] == pytest.approx(-1000 + 500 / 1.2 + 500 / 1.44 + 500 / 1.728, abs=1e-6)


def test_tir_simple():
    assert f.tir([-100, 110]) == pytest.approx(0.10, abs=1e-6)
    assert f.tir([-1000, 400, 400, 400]) == pytest.approx(0.0970, abs=1e-3)


def test_tir_sin_cambio_de_signo_es_nan():
    assert np.isnan(f.tir([100, 100, 100]))


def test_payback_interpolado():
    assert f.payback([-1000, 400, 400, 400]) == pytest.approx(2.5)
    assert np.isnan(f.payback([-1000, 100, 100]))


def test_crf():
    # 0,05·1,05^10 / (1,05^10 − 1) = 0,129505
    assert f.crf(0.05, 10) == pytest.approx(0.129505, abs=1e-6)
    assert f.crf(0.0, 10) == pytest.approx(0.1)


def test_serie_anual_inflacion_y_degradacion():
    s = f.serie_anual(100.0, 3, inflacion=0.02, degradacion=0.01)
    assert s[0] == pytest.approx(100.0)
    assert s[2] == pytest.approx(100 * 1.02 ** 2 * 0.99 ** 2)


def test_flujos_proyecto_y_van_con_opex():
    cf = f.flujos_proyecto(1000.0, np.array([300.0, 300.0, 300.0, 300.0]), opex=50.0)
    assert cf.tolist() == [-1000.0, 250.0, 250.0, 250.0, 250.0]
    assert f.van(cf, 0.05) == pytest.approx(-1000 + 250 * (1 - 1.05 ** -4) / 0.05, abs=1e-6)


def test_lcoe_sin_descuento():
    # r=0: (CAPEX + n·OPEX)/(n·E)
    assert f.lcoe(1000.0, 10.0, 1000.0, 0.0, 10) == pytest.approx((1000 + 100) / 10000)
