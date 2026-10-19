#!/usr/bin/env python3
"""Prueba de humo en navegador (Playwright + Chromium del sistema) de la app exportada en site/.

Uso: python scripts/e2e.py [--url http://localhost:8008/] [--ancho 1440] [--tools t01,t02,...] [--capturas DIR]
Recorre las herramientas en modo Simple con los valores por defecto, pulsa «Calcular» y comprueba que aparecen KPI y que no hay
errores en la consola ni peticiones a dominios externos."""
import argparse
import asyncio
import sys
from urllib.parse import urlparse

from playwright.async_api import async_playwright

CHROMIUM = "/opt/pw-browsers/chromium"


async def main(a):
    host = urlparse(a.url).netloc
    errores, externas = [], set()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROMIUM)
        ctx = await b.new_context(viewport={"width": a.ancho, "height": 900})
        pg = await ctx.new_page()
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errores.append("pageerror: " + str(e)))
        fallidas = []
        pg.on("response", lambda r: fallidas.append(f"{r.status} {r.url}") if r.status >= 400 else None)
        pg.on("request", lambda r: externas.add(r.url) if urlparse(r.url).netloc not in (host, "") and not r.url.startswith(("data:", "blob:")) else None)
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
        if not fr:
            print("ERROR: la app no arrancó en 240 s")
            await pg.screenshot(path=f"{a.capturas}/fallo_{a.ancho}.png")
            return 1
        print("app lista")
        await pg.screenshot(path=f"{a.capturas}/asistente_{a.ancho}.png")
        await fr.evaluate("Shiny.setInputValue('guardar_perfil', Math.random(), {priority: 'event'})")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{a.capturas}/inicio_{a.ancho}.png")
        fallos = 0
        for tid in a.tools.split(","):
            try:
                await fr.evaluate(f"Shiny.setInputValue('nav_{tid}', Math.random(), {{priority: 'event'}})")
                await fr.wait_for_selector(f"#{tid}_calcular", timeout=30000)
                await fr.evaluate(f"Shiny.setInputValue('{tid}_calcular', Math.random(), {{priority: 'event'}})")
                await fr.wait_for_selector(".kpi-grande", timeout=240000)
                await pg.wait_for_timeout(2500)
                n = len(await fr.query_selector_all(".kpi-grande"))
                graf = len(await fr.query_selector_all(".shiny-plot-output img"))
                print(f"{tid}: KPI={n} gráficos={graf}")
                await pg.screenshot(path=f"{a.capturas}/{tid}_{a.ancho}.png", full_page=False)
                if n < 3:
                    fallos += 1
            except Exception as e:  # noqa: BLE001
                fallos += 1
                print(f"{tid}: FALLO {type(e).__name__}: {str(e)[:200]}")
                await pg.screenshot(path=f"{a.capturas}/fallo_{tid}_{a.ancho}.png")
        # El aviso de Matplotlib al construir su caché de fuentes llega a la consola como "error" pero es informativo.
        errores = [e for e in errores if "building the font cache" not in e]
        print("errores de consola:", len(errores))
        for e in errores[:15]:
            print("  ", e[:300])
        print("respuestas HTTP >= 400:", fallidas[:10])
        print("peticiones externas:", sorted(externas)[:10])
        await b.close()
        return 1 if (fallos or externas or errores) else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8008/")
    ap.add_argument("--ancho", type=int, default=1440)
    ap.add_argument("--tools", default="t01")
    ap.add_argument("--capturas", default="/tmp/shots")
    sys.exit(asyncio.run(main(ap.parse_args())))
