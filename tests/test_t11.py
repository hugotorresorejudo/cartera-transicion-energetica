import numpy as np

from core.perfil import Perfil
from tools import t11_ayudas as t


def test_t11_beneficio_acotado_por_inversion():
    res = t.calcular(t.inferir(Perfil(), {"medidas": ["fv", "aerotermia", "ve", "punto"], "convocatoria": "si", "ordenanza": "si"}), 80)
    assert res.kpi("pct").p90 <= 100.5
    assert res.kpi("total").p50 > 0
    assert len(res.tabla) == 4


def test_t11_sin_irpf_ni_ayudas_es_cero():
    res = t.calcular(t.inferir(Perfil(), {"medidas": ["fv"], "irpf": "no", "convocatoria": "no", "ordenanza": "no"}), 40)
    assert res.kpi("total").p90 == 0


def test_t11_ordenanza_si_mejora():
    a = t.calcular(t.inferir(Perfil(), {"medidas": ["fv"], "ordenanza": "no", "irpf": "no", "convocatoria": "no"}), 40, 1).kpi("total").p50
    b = t.calcular(t.inferir(Perfil(), {"medidas": ["fv"], "ordenanza": "si", "irpf": "no", "convocatoria": "no"}), 40, 1).kpi("total").p50
    assert b > a
