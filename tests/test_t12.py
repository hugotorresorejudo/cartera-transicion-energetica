import numpy as np

from core.perfil import Perfil
from tools import t12_envolvente as t


def test_t12_resultados():
    res = t.calcular(t.inferir(Perfil(cp="28001"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert 0 < res.kpi("red").p50 < 90 and res.kpi("capex").p50 > 500


def test_t12_reduccion_combinada_menor_que_suma():
    res = t.calcular(t.inferir(Perfil(), {"medidas": ["fachada", "cubierta", "ventanas"], "tipo": "aislada"}), 60)
    sumas = sum(res.tabla[i]["Reducción de la demanda P50 (%)"] for i in range(3))
    assert res.kpi("red").p50 < sumas


def test_t12_antiguo_ahorra_mas_que_nuevo():
    a = t.calcular(t.inferir(Perfil(), {"edad": "pre1980"}), 40, 1).kpi("ahorro").p50
    b = t.calcular(t.inferir(Perfil(), {"edad": "2007"}), 40, 1).kpi("ahorro").p50
    assert a > b


def test_t12_ayuda_reduce_inversion_neta():
    par = t.inferir(Perfil(), {"edad": "pre1980", "medidas": ["fachada", "cubierta", "ventanas"], "tipo": "aislada"})
    sin = t.calcular(par, 40, 1).kpi("van").p50
    par2 = t.inferir(Perfil(), {"edad": "pre1980", "medidas": ["fachada", "cubierta", "ventanas"], "tipo": "aislada"})
    par2.editar("incluir_ayuda", 1)
    con = t.calcular(par2, 40, 1).kpi("van").p50
    assert con >= sin
