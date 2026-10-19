#!/usr/bin/env python3
"""Pruebas de navegador de flujos concretos: escenarios (guardar/cargar/comparar), subida de CSV de Datadis y ecuaciones MathJax."""
import argparse
import asyncio
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

CHROMIUM = "/opt/pw-browsers/chromium"


def csv_datadis(dias=45):
    filas = ["CUPS;Fecha;Hora;Consumo_kWh;Metodo_obtencion"]
    d0 = dt.date(2023, 1, 1)
    for i in range(dias):
        d = d0 + dt.timedelta(days=i)
        for h in range(1, 25):
            filas.append(f"ES001;{d:%d/%m/%Y};{h};{0.25 + (0.9 if 19 <= h <= 22 else 0.0):.3f}".replace(".", ",").replace(";", ";") + ";R")
    return "\n".join(filas)


async def main(a):
    host = urlparse(a.url).netloc
    errores = []
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROMIUM)
        ctx = await b.new_context(viewport={"width": a.ancho, "height": 900}, accept_downloads=True)
        pg = await ctx.new_page()
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and "font cache" not in m.text else None)
        await pg.goto(a.url, wait_until="load")
        fr = None
        for _ in range(240):
            for f in pg.frames:
                if f != pg.main_frame and await f.query_selector("#nav_inicio"):
                    fr = f
                    break
            if fr:
                break
            await pg.wait_for_timeout(1000)
        assert fr, "la app no arrancó"
        ir = lambda tid: fr.evaluate(f"Shiny.setInputValue('nav_{tid}', Math.random(), {{priority: 'event'}})")  # noqa: E731
        click = lambda id_: fr.evaluate(f"Shiny.setInputValue('{id_}', Math.random(), {{priority: 'event'}})")  # noqa: E731
        await click("guardar_perfil")

        # --- escenarios: calcular, guardar JSON, añadir a comparación, cargar y comprobar que reproduce
        await ir("t01")
        await fr.wait_for_selector("#t01_calcular")
        await click("t01_calcular")
        await fr.wait_for_selector(".kpi-grande", timeout=240000)
        await pg.wait_for_timeout(1500)
        antes = await fr.inner_text(".kpis")
        async with pg.expect_download() as dl:
            await fr.click("#t01_dl_esc")
        ruta = Path(tempfile.mkdtemp()) / "esc.json"
        await (await dl.value).save_as(ruta)
        esc = json.loads(ruta.read_text())
        print("escenario guardado:", esc["herramienta"], esc["semilla"], len(esc["resumen"]), "KPI")
        ok &= esc["herramienta"] == "t01" and len(esc["resumen"]) >= 3
        await click("t01_addcmp")
        await pg.wait_for_timeout(500)
        await ir("comparar")
        await fr.wait_for_selector(".tabla", timeout=20000)
        filas = len(await fr.query_selector_all(".tabla tbody tr"))
        print("comparación: filas de indicadores =", filas)
        ok &= filas >= 3
        await ir("t01")
        await fr.wait_for_selector("#t01_calcular")
        await click("t01_calcular")
        await fr.wait_for_selector(".kpi-grande", timeout=240000)
        await fr.set_input_files("#t01_cargar", str(ruta))
        await pg.wait_for_timeout(8000)
        await ir("t01")
        await click("t01_calcular")
        await fr.wait_for_selector(".kpi-grande", timeout=240000)
        await pg.wait_for_timeout(1500)
        despues = await fr.inner_text(".kpis")
        print("KPI tras cargar el escenario idénticos:", antes == despues)
        ok &= antes == despues

        # --- Método con ecuaciones MathJax
        await ir("t02")
        await fr.wait_for_selector("#t02_tabs")
        await fr.evaluate("document.querySelector('#t02_tabs a[data-value=\"Método\"]').click()")
        await fr.wait_for_selector(".metodo .eq", timeout=20000)
        await pg.wait_for_timeout(4000)
        svgs = len(await fr.query_selector_all(".metodo .eq svg"))
        print("ecuaciones MathJax renderizadas (svg):", svgs)
        ok &= svgs >= 3
        await pg.screenshot(path=f"{a.capturas}/metodo_t02_{a.ancho}.png")

        # --- Datadis: subir CSV y calcular
        csv = Path(tempfile.mkdtemp()) / "datadis.csv"
        csv.write_text(csv_datadis(), encoding="utf-8")
        await ir("t16")
        await fr.wait_for_selector("#t16_q_csv", state="attached")
        await fr.set_input_files("#t16_q_csv", str(csv))
        await pg.wait_for_timeout(3000)
        await click("t16_calcular")
        await fr.wait_for_selector(".kpi-grande", timeout=240000)
        await pg.wait_for_timeout(1500)
        txt = await fr.inner_text("#main, body")
        leida = "Curva leída" in txt
        print("Datadis: curva leída ->", leida)
        ok &= leida
        print("errores de consola:", errores[:5])
        ok &= not errores
        await b.close()
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8008/")
    ap.add_argument("--ancho", type=int, default=1440)
    ap.add_argument("--capturas", default="/tmp/shots")
    sys.exit(asyncio.run(main(ap.parse_args())))
