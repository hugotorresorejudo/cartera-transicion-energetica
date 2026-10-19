import numpy as np

from core import fv
from core.perfil import Perfil
from tools import t02_fv as t


def _perfil():
    return Perfil(cp="28001", vivienda="unif_<120", personas="3-4", ocupacion="parcial", equipos=["termo_electrico"],
                  factura="70-120", potencia=4.6)


def test_balance_conserva_energia():
    G = np.array([[0, 2, 5, 1.0]])
    E = np.array([[1, 1, 1, 3.0]])
    S, X, I = fv.balance(G, E)
    assert (S + X == G).all() and (S + I == E).all() and (S <= np.minimum(G, E) + 1e-12).all()


def test_compensacion_limitada_por_energia_importada():
    X = np.zeros((1, 8760), np.float32)
    I = np.zeros((1, 8760), np.float32)
    X[0, :24] = 10.0  # enero: 240 kWh excedentes a 0,1 -> 24 €
    I[0, :24] = 1.0   # enero: 24 kWh importados a 0,2 -> tope 4,8 €
    B = fv.compensacion(X, I, np.float32(0.1), np.float32(0.2))
    assert B[0] == np.float32(4.8) or abs(B[0] - 4.8) < 1e-4


def test_t02_simple_produce_p10_p50_p90():
    res = t.calcular(t.inferir(_perfil(), {"orientacion": "S", "tamano": "2"}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert 0 < res.kpi("sc").p50 <= 100
    assert res.kpi("Pp").p50 > 0
    assert res.kpi("ahorro1").p50 > 0


def test_t02_orientacion_norte_rinde_menos_que_sur():
    s = t.calcular(t.inferir(_perfil(), {"orientacion": "S"}), 40, 3).kpi("ahorro1").p50
    n = t.calcular(t.inferir(_perfil(), {"orientacion": "N"}), 40, 3).kpi("ahorro1").p50
    assert n < s


def test_t02_potencia_fija_respeta_el_valor():
    par = t.inferir(_perfil(), {})
    par.editar("P_p_fija", 2.0)
    res = t.calcular(par, 30)
    assert abs(res.kpi("Pp").p50 - 2.0) < 1e-6
