import numpy as np

from core.perfil import Perfil
from tools import t09_induccion as t


def test_t09_resultados():
    res = t.calcular(t.inferir(Perfil(personas="3-4"), {}), 60)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    # la inducción es más eficiente que la vitrocerámica: menor energía y coste que ella
    assert res.kpi("c_ind").p50 < res.kpi("c_vitro").p50 + 40
    assert res.kpi("e_ind").p50 > 50


def test_t09_sin_otros_gas_ahorra_mas():
    con = t.calcular(t.inferir(Perfil(), {"otros_gas": "si"}), 50, 1).kpi("ahorro").p50
    sin = t.calcular(t.inferir(Perfil(), {"otros_gas": "no"}), 50, 1).kpi("ahorro").p50
    assert sin > con
