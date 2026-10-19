import numpy as np

from core.perfil import Perfil
from tools import t20_curvas as t


def _r(**kw):
    return t.calcular(t.inferir(Perfil(), kw), 60)


def test_t20_resultados():
    res = _r()
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert 0 <= res.kpi("ren").p50 <= 100 and res.graficos and res.tabla


def test_t20_gas_caro_sube_el_precio_nocturno():
    base = _r(franja="noche", gas="ninguno").kpi("precio").p50
    caro = _r(franja="noche", gas="mas100").kpi("precio").p50
    assert caro >= base


def test_t20_menos_renovable_no_baja_el_precio():
    base = _r(franja="mediodia", renovable="ninguno").kpi("precio").p50
    malo = _r(franja="mediodia", renovable="menos50").kpi("precio").p50
    assert malo >= base - 1e-9
