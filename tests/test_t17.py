import numpy as np

from core import emisiones
from core.perfil import Perfil
from tools import t17_emisiones as t


def test_serie_ef_8760_positiva():
    ef = emisiones.serie_ef_8760()
    assert ef.shape == (8760,) and np.all(ef >= 0) and np.all(np.isfinite(ef))


def test_t17_resultados():
    res = t.calcular(t.inferir(Perfil(), {}), 40)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90 or np.isnan(k.p50)
    assert res.kpi("reduccion").p50 >= 0
    assert res.kpi("ef_best").p50 <= res.kpi("ef_hab").p50 + 1e-9
    assert len(res.tabla) == 4


def test_t17_ventana_amplia_reduce_mas():
    a = t.calcular(t.inferir(Perfil(), {"ventana": "noche"}), 30, 1).kpi("reduccion").p50
    b = t.calcular(t.inferir(Perfil(), {"ventana": "cualquiera"}), 30, 1).kpi("reduccion").p50
    assert b >= a - 1e-9
