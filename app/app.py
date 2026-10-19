"""Cartera de herramientas de transición energética — aplicación Shiny for Python (se ejecuta en el navegador con shinylive)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np  # noqa: F401
import pandas  # noqa: F401  (declara las dependencias de Pyodide para que shinylive las cargue)
import scipy.optimize  # noqa: F401
import yaml  # noqa: F401
from shiny import App, reactive, render, ui

import config
import graficos as G
import ui_comun as U
from core import datos, escenarios, montecarlo as mc
from core.perfil import Perfil, aplicar
from core.referencias import ref
from tools import CATALOGO, CATEGORIAS, MODULOS, PRIORIDAD, cargar

AQUI = Path(__file__).resolve().parent
try:
    METODO = json.loads((AQUI / "data" / "metodo.json").read_text(encoding="utf-8"))
except FileNotFoundError:
    METODO = {}
CAMPOS_PERFIL = ["cp", "vivienda", "personas", "ocupacion", "equipos", "factura", "potencia", "limitador"]
NMC_DEFECTO, SEMILLA_DEFECTO = 500, 42


def _barra_lateral():
    items = [ui.div(ui.input_action_link("nav_inicio", "Inicio"), class_="nav-item"),
             ui.div(ui.input_action_link("nav_asistente", "Mi hogar"), class_="nav-item"),
             ui.div(ui.input_action_link("nav_comparar", "Comparar escenarios"), class_="nav-item")]
    for cat, ids in CATEGORIAS:
        items.append(ui.div(cat, class_="nav-grupo"))
        for tid in ids:
            items.append(ui.div(ui.input_action_link(f"nav_{tid}", ui.TagList(ui.span(tid.upper(), class_="id"), CATALOGO[tid][0])),
                                class_="nav-item"))
    return ui.sidebar(*items, width=290, open={"desktop": "open", "mobile": "closed"})


app_ui = ui.page_sidebar(
    _barra_lateral(),
    ui.tags.head(
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ui.tags.link(rel="stylesheet", href="app.css"),
        ui.tags.script(src="app.js"),
        ui.tags.script(src="mathjax/tex-svg.js", async_=True, onload="tipografiar()"),
    ),
    ui.output_ui("aviso_global"),
    ui.div(ui.output_ui("principal"), class_="contenido"),
    ui.output_ui("pie"),
    title=config.TITULO,
    fillable=False,
)


def server(input, output, session):
    perfil = reactive.value(Perfil())
    pagina = reactive.value("asistente")
    respuestas = {tid: reactive.value({}) for tid in MODULOS}
    resultados = {tid: reactive.value(None) for tid in MODULOS}
    usados = {tid: reactive.value(None) for tid in MODULOS}
    cmp_lista = reactive.value([])
    ver = reactive.value(0)

    # ---- navegación: los <a> de la barra lateral se convierten en eventos mediante input_action_link por JS
    @reactive.effect
    async def _marcar():
        await session.send_custom_message("activo", f"nav_{pagina()}")

    def _ir(destino):
        pagina.set(destino)

    for destino in ["inicio", "asistente", "comparar"] + list(MODULOS):
        ui_id = f"nav_{destino}"

        def _crear(ui_id=ui_id, destino=destino):
            @reactive.effect
            @reactive.event(input[ui_id])
            def _():
                _ir(destino)
        _crear()

    for tid in MODULOS:
        def _crear_go(tid=tid):
            @reactive.effect
            @reactive.event(input[f"go_{tid}"])
            def _():
                _ir(tid)
        _crear_go()

    # ---- perfil compartido: se actualiza al editar sus preguntas
    @reactive.effect
    def _sync_perfil():
        with reactive.isolate():
            p = Perfil.from_dict(perfil.get().to_dict())
        cambiado = False
        for c in CAMPOS_PERFIL:
            try:
                v = input[f"p_{c}"]()
            except Exception:
                continue
            antes = getattr(p, c)
            aplicar(p, c, v if c != "equipos" else list(v or []))
            cambiado = cambiado or (getattr(p, c) != antes)
        if cambiado:
            with reactive.isolate():
                perfil.set(p)

    @reactive.effect
    @reactive.event(input.guardar_perfil)
    def _guardar_perfil():
        pagina.set("inicio")

    # ---- avisos y pie
    @output
    @render.ui
    def aviso_global():
        return U.aviso_datos()

    @output
    @render.ui
    def pie():
        return ui.div(
            ui.p("Herramienta orientativa, no constituye asesoramiento financiero."),
            ui.p(f"Datos actualizados: {datos.fecha_datos()} · ", ui.a("Repositorio", href=config.REPO_URL, target="_blank"),
                 f" · {config.AUTOR}"),
            class_="pie")

    # ---- página principal
    @output
    @render.ui
    def principal():
        p = pagina()
        ver()
        if p == "asistente":
            with reactive.isolate():
                return _pagina_asistente(perfil.get())
        if p == "inicio":
            return _pagina_inicio()
        if p == "comparar":
            return _pagina_comparar()
        return _pagina_herramienta(p)

    def _pagina_asistente(pf: Perfil):
        t01 = cargar("t01")
        qs = t01.preguntas()
        controles = []
        for q in qs:
            val = getattr(pf, q.perfil)
            if q.perfil == "potencia":
                val = "nose" if pf.potencia is None else str(pf.potencia)
            controles.append(U.entrada(q, val, "p"))
        return ui.div(
            ui.h2("Mi hogar"),
            ui.p("Responde estas preguntas una sola vez: todas las herramientas usan este perfil. No necesitas datos medidos; "
                 "si no sabes algo, elige «No lo sé»."),
            ui.layout_columns(*controles, col_widths={"sm": 12, "md": 6}),
            ui.input_action_button("guardar_perfil", "Guardar y continuar", class_="btn-primary"))

    def _pagina_inicio():
        bloques = []
        for cat, ids in CATEGORIAS:
            bloques.append(ui.h4(cat, class_="mt-3"))
            tarjetas = []
            for tid in ids:
                nombre, desc = CATALOGO[tid]
                tarjetas.append(ui.div(ui.div(f"{tid.upper()} · prioridad {PRIORIDAD[tid]}", class_="meta"), ui.h4(nombre), ui.p(desc),
                                       ui.input_action_button(f"go_{tid}", "Abrir", class_="btn-sm btn-outline-primary"), class_="tarjeta"))
            bloques.append(ui.div(*tarjetas, class_="tarjetas-inicio"))
        return ui.div(ui.h2("Cartera de herramientas de transición energética"),
                      ui.p("22 herramientas de decisión energética para hogares en España. Cada una funciona con unas pocas preguntas "
                           "y muestra rangos (P10–P50–P90) en lugar de cifras únicas."), *bloques)

    # ---- página de herramienta
    def _pagina_herramienta(tid):
        nombre, desc = CATALOGO[tid]
        return ui.div(
            ui.h2(f"{tid.upper()} · {nombre}"), ui.p(desc, class_="text-muted"),
            ui.div(ui.input_action_button(f"{tid}_calcular", "Calcular", class_="btn-primary"),
                   ui.span(" Monte Carlo con semilla fija: mismos datos, mismos resultados.", class_="text-muted small"),
                   class_="barra-acciones"),
            ui.navset_tab(
                ui.nav_panel("Simple", ui.output_ui(f"{tid}_simple")),
                ui.nav_panel("Avanzado", ui.output_ui(f"{tid}_avanzado")),
                ui.nav_panel("Resultados", ui.output_ui(f"{tid}_resultados")),
                ui.nav_panel("Método", ui.output_ui(f"{tid}_metodo")),
                id=f"{tid}_tabs"))

    def _respuestas_actuales(tid, mod):
        """Respuestas SIMPLE: valores de los controles si existen, o las guardadas, o los valores por defecto."""
        out = dict(respuestas[tid].get())
        for q in mod.preguntas():
            if q.perfil:
                continue
            try:
                v = input[f"{tid}_q_{q.id}"]()
            except Exception:
                v = out.get(q.id, q.defecto)
            if q.tipo == "archivo":
                if v:  # fichero subido -> texto
                    out[q.id] = Path(v[0]["datapath"]).read_text(encoding="utf-8", errors="replace")
                continue
            out[q.id] = list(v) if isinstance(v, (list, tuple)) else v
        pf = perfil.get()
        for q in mod.preguntas():
            if q.perfil:
                out[q.id] = getattr(pf, q.perfil)
        return out

    def registrar(tid):
        mod_cache = {}

        def modulo():
            if tid not in mod_cache:
                mod_cache[tid] = cargar(tid)
            return mod_cache[tid]

        @output(id=f"{tid}_simple")
        @render.ui
        def _simple():
            try:
                mod = modulo()
            except ModuleNotFoundError:
                return ui.p("Herramienta en construcción.")
            ver()
            with reactive.isolate():
                guardado, pf = respuestas[tid].get(), perfil.get()
            cs = []
            for q in mod.preguntas():
                if q.perfil:
                    val = getattr(pf, q.perfil)
                    if q.perfil == "potencia":
                        val = "nose" if pf.potencia is None else str(pf.potencia)
                    cs.append(U.entrada(q, val, "p"))
                elif q.tipo == "archivo":
                    cs.append(U.entrada(q, None, f"{tid}_q"))
                else:
                    cs.append(U.entrada(q, guardado.get(q.id, q.defecto), f"{tid}_q"))
            return ui.div(ui.p("Máximo 8 preguntas. El resto de datos sale de tu perfil «Mi hogar» y de datos reales; "
                               "puedes verlos y editarlos en la pestaña Avanzado.", class_="text-muted small"),
                          ui.layout_columns(*cs, col_widths={"sm": 12, "md": 6}))

        @output(id=f"{tid}_avanzado")
        @render.ui
        def _avanzado():
            try:
                mod = modulo()
            except ModuleNotFoundError:
                return ui.p("Herramienta en construcción.")
            par = mod.inferir(perfil.get(), _respuestas_actuales(tid, mod))
            filas = [U.fila_param(tid, p) for p in par.params.values()]
            return ui.div(
                ui.p("Valores inferidos a partir de tus respuestas. Edita cualquiera para fijarlo (el campo pasa a «editado») y pulsa Calcular.",
                     class_="text-muted small"),
                ui.layout_columns(ui.input_numeric(f"{tid}_nmc", "Muestras Monte Carlo (N)", NMC_DEFECTO, min=20, max=5000, step=50),
                                  ui.input_numeric(f"{tid}_semilla", "Semilla", SEMILLA_DEFECTO, step=1), col_widths={"sm": 6, "md": 3}),
                ui.div(*filas, class_="adv-grid"))

        @reactive.effect
        @reactive.event(input[f"{tid}_calcular"])
        def _calcular():
            try:
                mod = modulo()
            except ModuleNotFoundError:
                ui.notification_show("Herramienta en construcción", type="warning")
                return
            resp = _respuestas_actuales(tid, mod)
            respuestas[tid].set(resp)
            par = mod.inferir(perfil.get(), resp)
            editados = {}
            for k, p in par.params.items():
                try:
                    v = input[f"{tid}_adv_{k}"]()
                except Exception:
                    continue
                if v is not None and abs(float(v) - float(f"{p.central:.6g}")) > 1e-9 * max(1.0, abs(p.central)):
                    par.editar(k, float(v))
                    editados[k] = float(v)
            try:
                n = int(input[f"{tid}_nmc"]())
                semilla = int(input[f"{tid}_semilla"]())
            except Exception:
                n, semilla = NMC_DEFECTO, SEMILLA_DEFECTO
            with ui.Progress(min=0, max=1) as prog:
                prog.set(0.3, message="Calculando…", detail=f"{n} simulaciones Monte Carlo")
                res = mod.calcular(par, n, semilla)
            resultados[tid].set(res)
            usados[tid].set({"resp": resp, "editados": editados, "n": n, "semilla": semilla})
            ui.update_navset(f"{tid}_tabs", selected="Resultados")

        @output(id=f"{tid}_resultados")
        @render.ui
        def _resultados():
            res = resultados[tid].get()
            if res is None:
                return ui.p("Aún no hay resultados. Pulsa «Calcular».")
            nombre = CATALOGO[tid][0]
            n_graf = len(res.graficos)
            return ui.div(
                U.tarjetas_kpi(res), U.bloque_pendientes(res, ref()),
                ui.tags.ul(*[ui.tags.li(n) for n in res.notas], class_="notas"),
                *[ui.output_plot(f"{tid}_g{i}", height="340px") for i in range(n_graf)],
                ui.output_plot(f"{tid}_torn", height=f"{int(60 * max(len(res.tornado), 1) + 90)}px") if res.tornado else "",
                U.tabla_html(res.tabla),
                ui.div(ui.download_button(f"{tid}_dl_csv", "Descargar tabla (CSV)", class_="btn-sm btn-outline-secondary") if res.tabla else "",
                       ui.download_button(f"{tid}_dl_esc", "Guardar escenario (JSON)", class_="btn-sm btn-outline-secondary"),
                       ui.input_action_button(f"{tid}_addcmp", "Añadir a la comparación", class_="btn-sm btn-outline-secondary"),
                       class_="barra-acciones"),
                ui.input_file(f"{tid}_cargar", "Cargar escenario (JSON)", accept=[".json"], button_label="Elegir archivo"),
                ui.p(f"N = {res.n_mc} · semilla = {res.semilla} · datos: {datos.fecha_datos()}", class_="text-muted small"))

        for i in range(3):
            def _g(i=i):
                @output(id=f"{tid}_g{i}")
                @render.plot
                def _():
                    res = resultados[tid].get()
                    return G.dibujar(res.graficos[i])
            _g()

        @output(id=f"{tid}_torn")
        @render.plot
        def _torn():
            res = resultados[tid].get()
            k = next((k for k in res.kpis if k.id == res.extra.get("kpi_tornado")), res.kpis[0])
            return G.tornado(res.tornado, f"Sensibilidad de «{k.nombre}» (parámetro en P10 / P90)", k.unidad)

        @output(id=f"{tid}_metodo")
        @render.ui
        def _metodo():
            m = METODO.get(tid)
            r_ = ref()
            res = resultados[tid].get()
            claves = (res.extra.get("refs_usadas") if res else None) or []
            filas = []
            for k in claves:
                e = r_.entrada(k)
                enlace = ui.a(e["fuente"], href=e["url"], target="_blank") if e.get("url") else e["fuente"]
                filas.append({"Referencia": k, "Valor": str(e["valor"])[:60], "Fuente": str(e["fuente"])[:80],
                              "Estado": "verificada" if e["verificado"] else "pendiente de verificar", "Consulta": e["fecha_consulta"]})
            return ui.div(
                ui.HTML(m["html"]) if m else ui.p("Ficha en construcción."),
                ui.h3("Referencias utilizadas en el último cálculo"),
                U.tabla_html(filas) if filas else ui.p("Calcula primero para ver las referencias utilizadas.", class_="text-muted"),
                ui.p(f"Fecha de los datos: {datos.fecha_datos()}.", class_="text-muted small"),
                class_="metodo")

        @output(id=f"{tid}_dl_csv")
        @render.download_button(filename=f"{tid}_tabla.csv")
        def _dl_csv():
            res = resultados[tid].get()
            filas = res.tabla
            cols = list(filas[0])
            yield ";".join(cols) + "\n"
            for f in filas:
                yield ";".join(str(f[c]) for c in cols) + "\n"

        def _esc_actual():
            u = usados[tid].get()
            return escenarios.crear(tid, perfil.get(), u["resp"], u["editados"], u["n"], u["semilla"], f"{tid.upper()} · {CATALOGO[tid][0]}",
                                    resultados[tid].get())

        @output(id=f"{tid}_dl_esc")
        @render.download_button(filename=f"escenario_{tid}.json")
        def _dl_esc():
            yield escenarios.a_json(_esc_actual())

        @reactive.effect
        @reactive.event(input[f"{tid}_addcmp"])
        def _addcmp():
            cmp_lista.set((cmp_lista.get() + [_esc_actual()])[-3:])
            ui.notification_show("Escenario añadido a la comparación", type="message")

        @reactive.effect
        @reactive.event(input[f"{tid}_cargar"])
        def _cargar():
            f = input[f"{tid}_cargar"]()
            if not f:
                return
            esc = escenarios.de_json(Path(f[0]["datapath"]).read_text(encoding="utf-8"))
            if esc["herramienta"] != tid:
                ui.notification_show("El escenario es de otra herramienta", type="error")
                return
            perfil.set(Perfil.from_dict(esc["perfil"]))
            respuestas[tid].set(esc["respuestas"])
            res = escenarios.reproducir(esc, modulo())
            resultados[tid].set(res)
            usados[tid].set({"resp": esc["respuestas"], "editados": esc["editados"], "n": esc["n_mc"], "semilla": esc["semilla"]})
            ver.set(ver.get() + 1)

    for _tid in MODULOS:
        registrar(_tid)

    # ---- comparación lado a lado
    def _pagina_comparar():
        lista = cmp_lista.get()
        if not lista:
            return ui.div(ui.h2("Comparar escenarios"),
                          ui.p("Aún no hay escenarios. Calcula una herramienta y pulsa «Añadir a la comparación» (hasta 3), "
                               "o carga archivos JSON guardados."),
                          ui.input_file("cmp_archivos", "Cargar escenarios (JSON)", accept=[".json"], multiple=True, button_label="Elegir"))
        filas = escenarios.comparar(lista)
        tabla = []
        for f in filas:
            fila = {"Indicador": f["indicador"]}
            for k, v in f.items():
                if k != "indicador":
                    fila[k] = "—" if v is None else f"{U.num(v[1], '{:,.4g}')} ({U.num(v[0], '{:,.4g}')}–{U.num(v[2], '{:,.4g}')})"
            tabla.append(fila)
        return ui.div(ui.h2("Comparar escenarios"), ui.p("P50 (P10–P90) de cada indicador.", class_="text-muted"), U.tabla_html(tabla),
                      ui.input_action_button("cmp_vaciar", "Vaciar comparación", class_="btn-sm btn-outline-secondary"),
                      ui.input_file("cmp_archivos", "Cargar escenarios (JSON)", accept=[".json"], multiple=True, button_label="Elegir"))

    @reactive.effect
    @reactive.event(input.cmp_vaciar)
    def _vaciar():
        cmp_lista.set([])

    @reactive.effect
    @reactive.event(input.cmp_archivos)
    def _cmp_archivos():
        fs = input.cmp_archivos()
        nuevos = [escenarios.de_json(Path(f["datapath"]).read_text(encoding="utf-8")) for f in (fs or [])]
        cmp_lista.set((cmp_lista.get() + nuevos)[-3:])


app = App(app_ui, server, static_assets=AQUI / "www")
