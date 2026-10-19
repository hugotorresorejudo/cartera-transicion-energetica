import pytest

from core import referencias as r


def test_todas_las_entradas_cumplen_el_esquema():
    assert r.validar(r.ref()._d) == []


def test_verificado_false_exige_nota():
    e = {"x": {"valor": 1, "unidad": "u", "fuente": "f", "url": "u", "fecha_consulta": "2026-01-01", "verificado": False}}
    assert any("nota" in m for m in r.validar(e))


def test_verificado_true_exige_fuente_y_url():
    e = {"x": {"valor": 1, "unidad": "u", "fuente": "", "url": "", "fecha_consulta": "2026-01-01", "verificado": True}}
    assert r.validar(e)


def test_rastreo_y_pendientes():
    ref = r.ref()
    with ref.rastrear() as usadas:
        ref.get("tarifa.peaje_potencia_p1")  # verificado
        ref.get("tarifa.cargo_energia_p1")  # no verificado
    assert "tarifa.cargo_energia_p1" in ref.pendientes(usadas)
    assert "tarifa.peaje_potencia_p1" not in ref.pendientes(usadas)


def test_clave_inexistente():
    with pytest.raises(r.ReferenciaError):
        r.ref().get("no.existe")


def test_json_coincide_con_yaml():
    import json
    import yaml
    from core import referencias as r
    y = r._claves_str(yaml.safe_load(r.RUTA.read_text(encoding="utf-8")))
    j = json.loads(r.RUTA.with_suffix(".json").read_text(encoding="utf-8"))
    assert y == j, "ejecuta scripts/actualizar_refs.sh: referencias.json está desactualizado"
