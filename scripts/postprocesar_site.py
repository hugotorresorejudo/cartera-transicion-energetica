#!/usr/bin/env python3
"""Ajusta site/index.html tras `shinylive export`: título, idioma y pantalla de carga con el mensaje de arranque de Pyodide."""
import sys
from pathlib import Path

CARGA = """
    <style>
      #carga-inicial{position:fixed;inset:0;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem;
        background:#f6f8fa;color:#1d2630;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;text-align:center;padding:1rem}
      #carga-inicial .spin{width:44px;height:44px;border:4px solid #d5dbe1;border-top-color:#0f5c7a;border-radius:50%;animation:giro 1s linear infinite}
      #carga-inicial small{color:#5b6773}
      @keyframes giro{to{transform:rotate(360deg)}}
    </style>
    <script>
      // La pantalla de carga se retira cuando la app de Shiny ha pintado su navegación.
      var t0 = setInterval(function () {
        var fr = document.querySelector('#root iframe');
        try {
          if (fr && fr.contentDocument && fr.contentDocument.querySelector('#nav_inicio')) {
            var c = document.getElementById('carga-inicial'); if (c) c.remove(); clearInterval(t0);
          }
        } catch (e) {}
      }, 400);
    </script>
"""
BLOQUE = """    <div id="carga-inicial"><div class="spin"></div><div><strong>Cargando motor de cálculo (solo la primera vez)</strong><br>
      <small>Se está iniciando Python en tu navegador; las visitas siguientes arrancan mucho más rápido.</small></div></div>
"""


def main(carpeta: str = "site"):
    p = Path(carpeta) / "index.html"
    h = p.read_text(encoding="utf-8")
    meta = ("\n    <link rel=\"icon\" href=\"data:,\">"
            "\n    <meta name=\"description\" content=\"22 herramientas de decisión energética para hogares en España (Pyodide, sin servidor).\">")
    h = h.replace('<html lang="en">', '<html lang="es">').replace("<title>Shiny App</title>", "<title>Cartera de herramientas de transición energética</title>" + meta)
    if "carga-inicial" not in h:
        h = h.replace("</head>", CARGA + "  </head>").replace('<div style="height: 100vh; width: 100vw" id="root"></div>', BLOQUE + '    <div style="height: 100vh; width: 100vw" id="root"></div>')
    p.write_text(h, encoding="utf-8")
    print("index.html actualizado")


if __name__ == "__main__":
    main(*sys.argv[1:])
