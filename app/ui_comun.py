"""Componentes de interfaz reutilizables (formato es-ES, entradas de preguntas, tarjetas de KPI)."""
from __future__ import annotations

import math

from htmltools import HTML, tags
from shiny import ui

from core import datos, montecarlo as mc
from core.herramienta import Pregunta, Resultados


def num(x, fmt: str = "{:,.0f}") -> str:
    """Formato numérico español: separador de miles '.' y decimal ','."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = fmt.format(x)
    return s.replace(",", "\0").replace(".", ",").replace("\0", ".")


def entrada(q: Pregunta, valor, prefijo: str):
    """Control de formulario para una pregunta; el id es `<prefijo>_<id>`."""
    id_ = f"{prefijo}_{q.id}"
    if q.tipo == "select":
        ops = {str(v): e for v, e in q.opciones}
        if len(ops) <= 4:
            return ui.input_radio_buttons(id_, q.texto, ops, selected=str(valor))
        return ui.input_select(id_, q.texto, ops, selected=str(valor))
    if q.tipo == "multi":
        return ui.input_checkbox_group(id_, q.texto, {str(v): e for v, e in q.opciones}, selected=[str(x) for x in (valor or [])])
    if q.tipo == "numero":
        return ui.input_numeric(id_, q.texto, valor)
    return ui.input_text(id_, q.texto, valor or "")


def _bloque_kpi(k, grande: bool, sintetico_o_pendiente: bool) -> tags.div:
    cls = {"ahorro": "kpi-ahorro", "coste": "kpi-coste"}.get(k.tipo, "")
    hijos = [tags.div(k.nombre, class_="kpi-nombre"),
             tags.div(tags.span(num(k.p50, k.fmt), class_="kpi-valor"), tags.span(f" {k.unidad}", class_="kpi-unidad"), class_="kpi-p50"),
             tags.div(f"P10 {num(k.p10, k.fmt)} – P90 {num(k.p90, k.fmt)}", class_="kpi-rango")]
    if k.prob is not None:
        hijos.append(tags.div(f"{k.prob_texto}: {num(100 * k.prob, '{:.0f}')} %", class_="kpi-prob"))
    if sintetico_o_pendiente and grande:
        hijos.append(tags.span("pendiente de verificar", class_="chip chip-pend", title="Depende de referencias sin fuente primaria verificada"))
    return tags.div(*hijos, class_=f"kpi {cls} {'kpi-grande' if grande else 'kpi-pequeno'}")


def tarjetas_kpi(res: Resultados):
    pend = bool(res.refs_pendientes)
    grandes = [_bloque_kpi(k, True, pend) for k in res.kpis[:3]]
    resto = [_bloque_kpi(k, False, False) for k in res.kpis[3:]]
    return tags.div(tags.div(*grandes, class_="kpis"),
                    tags.details(tags.summary("Más indicadores"), tags.div(*resto, class_="kpis kpis-extra"), open=False) if resto else "")


def aviso_datos():
    if datos.es_sintetico():
        return tags.div(tags.strong("Datos de demostración. "),
                        "Las series de precios, producción solar y generación son sintéticas (el workflow de datos aún no las ha sustituido por las reales de OMIE, REData y PVGIS). Los resultados no son representativos.",
                        class_="aviso aviso-datos")
    return ""


def bloque_pendientes(res: Resultados, ref):
    if not res.refs_pendientes:
        return ""
    items = []
    for k in res.refs_pendientes:
        e = ref.entrada(k)
        items.append(tags.li(tags.code(k), f" — {e.get('nota', '')[:220]}"))
    return tags.details(tags.summary(f"⚠ {len(res.refs_pendientes)} referencias pendientes de verificar intervienen en este resultado"),
                        tags.ul(*items, class_="lista-pend"), class_="aviso aviso-pend")


def tabla_html(filas: list[dict]):
    if not filas:
        return ""
    cols = list(filas[0])
    cab = tags.tr(*[tags.th(c) for c in cols])
    cuerpo = [tags.tr(*[tags.td(str(f[c])) for c in cols]) for f in filas]
    return tags.div(tags.table(tags.thead(cab), tags.tbody(*cuerpo), class_="tabla"), class_="tabla-wrap")


def rango_txt(dist: dict) -> str:
    if dist["t"] == "fijo":
        return ""
    return f"P10–P90: {num(mc.cuantil(dist, 0.1), '{:.4g}')} – {num(mc.cuantil(dist, 0.9), '{:.4g}')}"


def fila_param(tid: str, p) -> tags.div:
    centro = float(f"{p.central:.6g}")
    return tags.div(
        tags.div(tags.span(p.etiqueta, class_="adv-etq"), tags.span(f" ({p.unidad})", class_="adv-unidad"), class_="adv-cab"),
        tags.div(ui.input_numeric(f"{tid}_adv_{p.id}", None, centro, width="100%"),
                 tags.span("inferido" if p.origen != "editado" else "editado", class_="chip chip-inf"), class_="adv-ctrl"),
        tags.div(rango_txt(p.dist), class_="adv-rango"),
        class_="adv-fila", **{"data-central": str(centro)})
