import numpy as np
import pytest

from core import montecarlo as mc


def test_semilla_fija_reproduce():
    d = {"a": mc.tri(1, 2, 4), "b": mc.logn(10, 1.3), "c": mc.unif(0, 1)}
    a, b = mc.muestras(d, 200, 7), mc.muestras(d, 200, 7)
    assert all(np.array_equal(a[k], b[k]) for k in d)


def test_triangular_media():
    x = mc.muestrear(mc.tri(0, 3, 6), 200000, np.random.default_rng(1))
    assert x.mean() == pytest.approx(3.0, abs=0.02)


def test_lognormal_mediana():
    x = mc.muestrear(mc.logn(100, 1.5), 200000, np.random.default_rng(1))
    assert np.median(x) == pytest.approx(100, rel=0.01)


def test_percentiles_y_prob():
    x = np.arange(101.0)
    assert mc.p10_50_90(x) == (10.0, 50.0, 90.0)
    assert mc.prob(x, lambda v: v > 49) == pytest.approx(51 / 101)


def test_tornado_lineal_ordena_por_impacto():
    d = {"x": mc.unif(0, 10), "y": mc.unif(0, 1), "z": mc.fijo(5)}
    filas = mc.tornado(lambda S: {"o": 2 * S["x"] + 3 * S["y"] + S["z"]}, d, "o")
    assert [f["parametro"] for f in filas] == ["x", "y"]
    assert filas[0]["alto"] - filas[0]["bajo"] == pytest.approx(2 * 8, rel=0.02)
