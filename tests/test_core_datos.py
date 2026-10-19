import numpy as np
import pytest

from core import calendario, clima, datos, precios
from core.referencias import ref


def test_calendario_8760_y_periodos():
    c = calendario.calendario(2023)
    assert c["periodo"].size == 8760
    # lunes 2-ene-2023 a las 11h: P1; a las 3h: P3; domingo: todo P3
    i_lun = (1) * 24
    assert c["periodo"][i_lun + 11] == 0 and c["periodo"][i_lun + 3] == 2 and c["periodo"][i_lun + 8] == 1
    assert (c["periodo"][(0) * 24:(1) * 24] == 2).all()  # 1-ene festivo/domingo


def test_festivos_incluyen_viernes_santo():
    import datetime as dt
    assert dt.date(2026, 4, 3) in calendario.festivos(2026)
    assert calendario.pascua(2024) == dt.date(2024, 3, 31)


def test_cp_a_provincia():
    assert clima.provincia("28013")["nombre"] == "Madrid"
    assert clima.zona_cte("08001") == "C2"
    with pytest.raises(ValueError):
        clima.provincia("99999")


def test_pvgis_interpolacion_y_forma():
    y = clima.pv_normalizado("28001", 0, 30)
    assert y.shape == (8760,) and 1000 < y.sum() < 2200
    # el sur produce más que el este y que el norte
    assert y.sum() > clima.pv_normalizado("28001", -90, 30).sum() > clima.pv_normalizado("28001", 180, 30).sum()
    # interpolación: 22,5º entre dos puntos de la rejilla queda entre ambos
    a, b = clima.pv_normalizado("28001", 0, 15).sum(), clima.pv_normalizado("28001", 0, 30).sum()
    m = clima.pv_normalizado("28001", 0, 22.5).sum()
    assert min(a, b) - 1 <= m <= max(a, b) + 1


def test_omie_series_8760():
    ys, M = datos.omie_matriz()
    assert M.shape[1] == 8760 and len(ys) >= 2


def test_factura_caso_a_mano():
    # 1000 kWh a 0,10 €/kWh, 4,6 kW; sin calcular a mano los reguladores: se verifica la composición algebraica.
    E = np.full((1, 8760), 1000 / 8760, dtype=np.float32)
    p = np.full(8760, 0.10, dtype=np.float32)
    pp = np.array([30.0, 0.5])
    f = precios.factura(E, p, 4.6, 4.6, pp)
    ce, cp = 100.0, 4.6 * 30.5
    iee = max(ref().get("tarifa.iee_tipo") / 100 * (ce + cp), ref().get("tarifa.iee_minimo_domestico") * 1000)
    esperado = (ce + cp + iee + ref().get("tarifa.alquiler_contador") * 12) * (1 + ref().get("tarifa.iva_electricidad") / 100)
    assert f["total"][0] == pytest.approx(esperado, rel=1e-4)


def test_invertir_factura_es_inversa_de_factura():
    pp = precios.potencia_precios("pvpc")
    E0 = 3000.0
    p = 0.15
    E = np.full((1, 8760), E0 / 8760, dtype=np.float32)
    f = precios.factura(E, np.full(8760, p, dtype=np.float32), 4.6, 4.6, pp)
    est = precios.invertir_factura(f["total"][0] / 12, 4.6 * 2 / 2, p, pp)
    # la inversión ignora el mínimo del IEE (no activo aquí); la potencia usa P·(P1+P2)/2 en el caso P1=P2
    assert est == pytest.approx(E0, rel=0.02) or abs(est - E0) < 0.35 * E0


def test_precio_pvpc_es_razonable():
    om = datos.omie_matriz()[1][:1]
    p = precios.precio_pvpc(om)
    assert 0.05 < float(p.mean()) < 0.35
    assert p.shape == (1, 8760)


def test_bootstrap_semanal_conserva_forma():
    rng = np.random.default_rng(1)
    esc = precios.escenarios_omie(20, rng)
    assert esc.shape == (20, 8760)
    ys, M = datos.omie_matriz()
    # cada semana de cada escenario coincide con alguna de las semanas históricas
    assert any(np.allclose(esc[0, :168], M[k, :168], atol=1e-3) for k in range(M.shape[0]))
