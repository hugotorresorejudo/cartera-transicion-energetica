import numpy as np

from core.perfil import Perfil
from tools import t14_comunidad as t


def test_t14_resultados():
    res = t.calcular(t.inferir(Perfil(cp="28001"), {}), 40)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert 0 < res.kpi("sc").p50 <= 100 and len(res.tabla) == 3


def test_t14_dinamico_no_pierde_autoconsumo_frente_a_estaticos():
    res = t.calcular(t.inferir(Perfil(cp="28001"), {"ocupacion": "mixto"}), 40, 1)
    sc = {f["Reparto"]: f["Autoconsumo P50 (%)"] for f in res.tabla}
    assert sc["Dinámico horario"] >= sc["Estático igual"] - 1
    assert sc["Dinámico horario"] >= sc["Estático por consumo"] - 1


def test_t14_mas_potencia_por_vecino_baja_autoconsumo():
    a = t.calcular(t.inferir(Perfil(), {"tamano": "pequena"}), 30, 1).kpi("sc").p50
    b = t.calcular(t.inferir(Perfil(), {"tamano": "grande"}), 30, 1).kpi("sc").p50
    assert b < a
