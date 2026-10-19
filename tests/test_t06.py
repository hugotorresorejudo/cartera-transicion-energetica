import numpy as np
import pytest

from core import bateria
from core.perfil import Perfil
from tools import t06_bateria as t


def test_despacho_conserva_energia_y_limites():
    rng = np.random.default_rng(0)
    G = rng.uniform(0, 3, (4, 48)).astype(np.float32)
    E = rng.uniform(0, 2, (4, 48)).astype(np.float32)
    S, X, I, ciclos = bateria.despacho(G, E, 5.0, 2.0, 0.9)
    # balance: G + I = E + X + pérdidas (>= 0)
    perdidas = (G + I - E - X).sum(axis=1)
    assert (perdidas >= -1e-4).all() and (perdidas <= G.sum(axis=1) * 0.1 + 1e-3).all()
    assert (S <= E + 1e-5).all() and (X >= -1e-6).all() and (I >= -1e-6).all()


def test_bateria_nula_equivale_a_balance_directo():
    G = np.array([[0, 3, 0, 1.0]], np.float32)
    E = np.array([[1, 1, 2, 1.0]], np.float32)
    S, X, I, c = bateria.despacho(G, E, 0.0, 2.0, 0.9)
    assert np.allclose(S, np.minimum(G, E)) and c[0] == 0


def test_bateria_ideal_traslada_excedente_a_la_noche():
    G = np.array([[0, 4.0, 0]], np.float32)
    E = np.array([[0, 0, 3.0]], np.float32)
    S, X, I, c = bateria.despacho(G, E, 10.0, 10.0, 1.0)
    assert I[0, 2] == pytest.approx(0.0) and X[0, 1] == pytest.approx(0.0)


def test_t06_resultados():
    pf = Perfil(vivienda="unif_<120", personas="3-4", factura="70-120", potencia=4.6, equipos=["termo_electrico"])
    res = t.calcular(t.inferir(pf, {"tamano": "2"}), 50)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert res.kpi("ss").p50 >= res.kpi("ss0").p50 - 1e-6
    assert res.graficos
