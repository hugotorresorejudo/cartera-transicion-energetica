"""Convertidor mínimo de Markdown a HTML para las fichas (títulos, tablas, listas, código/LaTeX, énfasis y enlaces)."""
import html
import re


def _inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md2html(md: str, nivel_base: int = 3) -> str:
    out, lineas, i = [], md.splitlines(), 0
    while i < len(lineas):
        ln = lineas[i]
        if ln.startswith("```"):
            lang = ln[3:].strip()
            j = i + 1
            cuerpo = []
            while j < len(lineas) and not lineas[j].startswith("```"):
                cuerpo.append(lineas[j])
                j += 1
            txt = "\n".join(cuerpo)
            if lang == "latex":
                out.append(f'<div class="eq">\\[{html.escape(txt, quote=False)}\\]</div>')
            else:
                out.append(f"<pre><code>{html.escape(txt, quote=False)}</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            n = min(len(m.group(1)) + nivel_base - 2, 6)
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
            i += 1
            continue
        if ln.lstrip().startswith("|") and i + 1 < len(lineas) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lineas[i + 1]):
            cab = [c.strip() for c in ln.strip().strip("|").split("|")]
            filas, j = [], i + 2
            while j < len(lineas) and lineas[j].lstrip().startswith("|"):
                filas.append([c.strip() for c in lineas[j].strip().strip("|").split("|")])
                j += 1
            t = "<div class='tabla-md'><table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in cab) + "</tr></thead><tbody>"
            for f in filas:
                t += "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in f) + "</tr>"
            out.append(t + "</tbody></table></div>")
            i = j
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items, j = [], i
            while j < len(lineas) and re.match(r"^\s*[-*]\s+", lineas[j]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lineas[j]))
                j += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
            i = j
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items, j = [], i
            while j < len(lineas) and re.match(r"^\s*\d+\.\s+", lineas[j]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lineas[j]))
                j += 1
            out.append("<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ol>")
            i = j
            continue
        if ln.strip():
            par, j = [ln.strip()], i + 1
            while j < len(lineas) and lineas[j].strip() and not re.match(r"^(#|```|\s*\||\s*[-*]\s|\s*\d+\.\s)", lineas[j]):
                par.append(lineas[j].strip())
                j += 1
            out.append(f"<p>{_inline(' '.join(par))}</p>")
            i = j
            continue
        i += 1
    return "\n".join(out)
