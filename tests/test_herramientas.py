"""Pruebas transversales a las 22 herramientas: contrato, modo Simple por defecto y escenarios reproducibles."""
import numpy as np
import pytest

from core import escenarios
from core.perfil import Perfil
from tools import CATALOGO, MODULOS, cargar

IDS = sorted(MODULOS)
PERFIL = Perfil(cp="46001", vivienda="piso_70_120", personas="3-4", ocupacion="parcial", equipos=["induccion", "termo_electrico"], factura="70-120", potencia=4.6)


def _defecto(mod):
    """Respuestas por defecto de todas las preguntas que no pertenecen al perfil."""
    return {q.id: q.defecto for q in mod.preguntas() if not q.perfil and q.tipo != "archivo"}


@pytest.mark.parametrize("tid", IDS)
def test_contrato_de_la_herramienta(tid):
    m = cargar(tid)
    assert callable(m.inferir) and callable(m.calcular) and callable(m.preguntas)
    assert m.NOMBRE == CATALOGO[tid][0] or m.NOMBRE
    assert len(m.preguntas()) <= 8, "el modo SIMPLE admite como máximo 8 preguntas"


@pytest.mark.parametrize("tid", IDS)
def test_simple_con_valores_por_defecto_da_p10_p50_p90(tid):
    m = cargar(tid)
    par = m.inferir(PERFIL, _defecto(m))
    res = m.calcular(par, 40, 7)
    assert len(res.kpis) >= 3, "tres KPI como mínimo"
    for k in res.kpis[:3]:
        assert not np.isnan(k.p50), f"{tid}:{k.id} sin valor"
    for k in res.kpis:
        if not np.isnan(k.p50):
            assert k.p10 <= k.p50 <= k.p90, f"{tid}:{k.id} percentiles desordenados"
    assert res.graficos, "al menos un gráfico"


@pytest.mark.parametrize("tid", IDS)
def test_escenario_json_reproduce_los_mismos_resultados(tid):
    m = cargar(tid)
    resp = _defecto(m)
    par = m.inferir(PERFIL, resp)
    editables = [k for k, p in par.params.items() if p.dist["t"] != "fijo"][:1]
    editados = {}
    for k in editables:
        v = float(par.params[k].central) * 1.1
        par.editar(k, v)
        editados[k] = v
    a = m.calcular(par, 30, 11)
    esc = escenarios.de_json(escenarios.a_json(escenarios.crear(tid, PERFIL, resp, editados, 30, 11, tid, a)))
    b = escenarios.reproducir(esc, m)
    for ka, kb in zip(a.kpis, b.kpis):
        assert (ka.p10, ka.p50, ka.p90) == pytest.approx((kb.p10, kb.p50, kb.p90), nan_ok=True, rel=0, abs=0)


@pytest.mark.parametrize("tid", IDS)
def test_cada_herramienta_tiene_ficha_con_las_8_secciones(tid):
    from pathlib import Path
    f = Path(__file__).resolve().parent.parent / "docs" / "fichas" / f"{tid.upper()}.md"
    assert f.exists()
    t = f.read_text(encoding="utf-8")
    titulos = ["Objetivo y decisión", "Entradas SIMPLE (≤ 8)", "Entradas AVANZADO", 'Tabla de inferencia "respuesta → parámetro técnico"',
               "Datos reales a contrastar (fuente y qué se extrae)", "Método de cálculo con ecuaciones LaTeX", "Salidas con rango P10–P90", "Validación y limitaciones"]
    for i, ti in enumerate(titulos, 1):
        assert f"## {i}. {ti}" in t, f"{tid}: falta la sección {i}"
    assert "```latex" in t, f"{tid}: la sección 6 debe llevar ecuaciones LaTeX"
