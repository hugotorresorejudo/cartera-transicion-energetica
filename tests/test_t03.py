import numpy as np

from core.perfil import Perfil
from tools import t03_omie as t


def _r(**kw):
    return t.calcular(t.inferir(Perfil(factura="70-120"), kw), 40)


def test_t03_indicadores_basicos():
    r = _r(ponderar="solar", periodo="anio")
    assert 10 < r.kpi("media").p50 < 200
    assert 0.2 < r.kpi("fc").p50 < 1.2          # el precio capturado solar queda por debajo del medio (canibalización)
    assert r.kpi("spread").p50 > 0 and r.kpi("horas_bajo").p50 >= 0
    assert r.graficos and r.tabla


def test_t03_captura_solar_menor_que_plano():
    solar, nada = _r(ponderar="solar").kpi("fc").p50, _r(ponderar="nada").kpi("fc").p50
    assert abs(nada - 1) < 1e-6 and solar < nada


def test_t03_todas_las_vistas_y_ponderaciones():
    for vista in ("perfil", "calor", "duracion", "serie"):
        assert _r(vista=vista, zona="ambas").graficos
    for pond in ("nada", "solar", "eolica", "mi_fv", "mi_consumo"):
        assert np.isfinite(_r(ponderar=pond, periodo="mes").kpi("capturado").p50)


def test_t03_marca_mecanismo_de_ajuste_en_2023():
    r = _r(periodo="comparar")
    assert any("mecanismo de ajuste" in n for n in r.notas)
