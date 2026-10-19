import numpy as np

from core import escenarios
from core.perfil import Perfil
from tools import t01_tarifas as t


def _perfil(**kw):
    return Perfil(cp="28001", vivienda="piso_70_120", personas="3-4", ocupacion="parcial", equipos=["induccion", "termo_electrico"],
                  factura="70-120", potencia=4.6, **kw)


def test_t01_resultados_percentiles_ordenados():
    res = t.calcular(t.inferir(_perfil()), n_mc=80)
    for k in res.kpis:
        assert k.p10 <= k.p50 <= k.p90
    assert 500 < res.kpi("coste_mejor").p50 < 4000
    assert len(res.tabla) == 4 and res.tornado


def test_t01_coste_coherente_con_factura():
    # factura de 70–120 €/mes -> coste anual del orden de 840–1440 € (el mejor contrato queda por debajo del actual)
    res = t.calcular(t.inferir(_perfil()), n_mc=80)
    assert 500 < res.kpi("coste_mejor").p50 < 1500


def test_t01_semilla_fija_reproduce_y_escenario_json():
    perfil = _perfil()
    par = t.inferir(perfil)
    a = t.calcular(par, 60, 5)
    b = t.calcular(t.inferir(perfil), 60, 5)
    assert [k.p50 for k in a.kpis] == [k.p50 for k in b.kpis]
    esc = escenarios.de_json(escenarios.a_json(escenarios.crear("t01", perfil, {}, {}, 60, 5, "x", a)))
    c = escenarios.reproducir(esc, t)
    assert [k.p50 for k in c.kpis] == [k.p50 for k in a.kpis]


def test_t01_editar_parametro_cambia_resultado():
    perfil = _perfil()
    par = t.inferir(perfil)
    base = t.calcular(par, 50, 1).kpi("coste_mejor").p50
    par.editar("f_consumo", 1.5)
    assert par.params["f_consumo"].origen == "editado"
    assert t.calcular(par, 50, 1).kpi("coste_mejor").p50 > base


def test_t01_potencia_optima_normalizada():
    res = t.calcular(t.inferir(_perfil()), 40)
    assert any("P* =" in n for n in res.notas)
