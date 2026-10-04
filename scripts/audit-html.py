# -*- coding: utf-8 -*-
"""Genera audit/index.html: el informe de auditoría, contado con Aurora.

La idea: si el sistema sirve, sirve también para documentarse a sí mismo. El
informe se construye con las clases reales del design system (.nz-*), así que
si algo del sistema se rompe, se rompe aquí primero y se ve a la legua.

Uso: python scripts/audit-html.py   (después de audit-catalog.py)
"""
import html
import json
import pathlib
import sys
from importlib import import_module

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
bc = import_module("build-catalog")

ROOT = bc.ROOT
OUT = ROOT / "audit"


def fila(etiqueta, valor, bien):
    icono = "✓" if bien is True else ("!" if bien is None else "✗")
    clase = "nz-badge--success" if bien is True else ("nz-badge--neutral" if bien is None else "nz-badge--danger")
    return (f'<tr><td>{html.escape(etiqueta)}</td><td class="nz-table__strong">{valor}</td>'
            f'<td><span class="nz-badge {clase}"><i></i>{icono}</span></td></tr>')


def main():
    datos = json.loads((OUT / "auditoria.json").read_text(encoding="utf-8"))
    r = datos["resumen"]
    h = datos["hallazgos"]

    comprobaciones = [
        ("Objetos declarados", r["objetos_declarados"], None),
        ("Familias de objeto", r["familias"], None),
        ("Demos en vivo", r["demos"], None),
        ("Categorías", r["categorias"], None),
        ("Clases usadas en demos", r["clases_usadas_en_demos"], None),
        ("Objetos fantasma (usados y no declarados)", r["fantasmas"], r["fantasmas"] == 0),
        ("Clases declaradas sin demo", r["clases_sin_demo"], r["clases_sin_demo"] == 0),
        ("Familias sin demo", r["familias_sin_demo"], r["familias_sin_demo"] == 0),
        ("Clases declaradas por 2+ packs", r["duplicados"], r["duplicados"] == 0),
        ("Tokens inexistentes en uso", r["tokens_fantasma"], r["tokens_fantasma"] == 0),
        ("Gradientes fuera de la capa de cristal", r["gradientes"], r["gradientes"] == 0),
        ("Glass fuera de la capa de cristal", r["glass"], r["glass"] == 0),
        ("Colores a mano fuera de tokens.css", r["hex"], r["hex"] == 0),
        ("!important", r["important"], r["important"] <= 3),
    ]
    total_fallos = sum(1 for _, _, ok in comprobaciones if ok is False)

    filas_packs = "\n".join(
        f'<tr><td><code>{html.escape(n)}</code></td><td class="nz-table__num">{d["lineas"]}</td>'
        f'<td class="nz-table__num">{d["clases"]}</td><td class="nz-table__num">{d["familias"]}</td>'
        f'<td class="nz-table__num">{d["hex"]}</td><td class="nz-table__num">{d["gradientes"]}</td>'
        f'<td class="nz-table__num">{d["important"]}</td></tr>'
        for n, d in datos["packs"].items())

    filas_cat = "\n".join(
        f'<tr><td class="nz-table__num">{int(k):02d}</td><td>{html.escape(v["nombre"])}</td>'
        f'<td><code>{html.escape(v["pack"])}</code></td>'
        f'<td class="nz-table__num">{v["objetos"]}</td><td class="nz-table__num">{v["familias"]}</td>'
        f'<td class="nz-table__num">{v["demos"]}</td>'
        f'<td class="nz-table__num">{len(v["sin_demo"]) or "—"}</td>'
        f'<td class="nz-table__num">{len(v["familias_sin_demo"]) or "—"}</td></tr>'
        for k, v in datos["categorias"].items())

    lista_fant = ", ".join(f"<code>{html.escape(c)}</code>" for c in h["fantasmas"]) or \
        "Ninguno: todo lo que usan las demos existe en algún pack."
    lista_dup = "<br>".join(f'<code>{html.escape(c)}</code> → {html.escape(", ".join(v))}'
                            for c, v in h["duplicados"].items()) or \
        "Ninguno: cada objeto tiene un único dueño."
    lista_tok = ", ".join(f"<code>{html.escape(t)}</code>" for t in h["tokens_fantasma"]) or "Ninguno."
    sin_var = datos.get("sin_variantes", [])

    pag = f"""<!DOCTYPE html>
<html lang="es" data-nz-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Auditoría · Aurora</title>
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="../packs/p0-catalog.css">
<!--PACKS-->
</head>
<body class="nz">
<a class="nz-skip-link" href="#contenido">Saltar al contenido</a>
<header class="cat-topbar">
  <a class="cat-brandmark" href="../index.html"><i></i><i></i> Aurora</a>
  <span class="cat-count">auditoría del sistema</span>
  <span class="cat-topbar__tools">
    <a class="cat-icobtn" href="../index.html" title="Portada" aria-label="Volver a la portada">⌂</a>
    <button class="cat-icobtn" id="btnTheme" aria-label="Cambiar tema">◐</button>
  </span>
</header>

<main class="nz-container cat-main" id="contenido">
  <div class="cat-pagehead">
    <p class="cat-pagehead__over">Informe generado por scripts/audit-catalog.py</p>
    <h1>Auditoría <em>campo a campo</em></h1>
    <p>Cada objeto del sistema, cruzado contra las demos que lo enseñan. Lo que sale de aquí
    no es una opinión: son cuentas hechas leyendo el CSS y los specs.</p>
    <div class="cat-pagehead__stats">
      <span class="nz-badge nz-badge--brand"><i></i>{r['objetos_declarados']} objetos</span>
      <span class="nz-badge nz-badge--neutral">{r['familias']} familias</span>
      <span class="nz-badge nz-badge--accent">{r['demos']} demos</span>
      <span class="nz-badge {'nz-badge--success' if total_fallos == 0 else 'nz-badge--danger'}">
        <i></i>{'sistema coherente' if total_fallos == 0 else str(total_fallos) + ' avisos'}</span>
    </div>
  </div>

  <section class="cat-demo cat-in">
    <div class="cat-demo__title"><span class="cat-demo__num">1</span><span class="cat-demo__name">Veredicto</span></div>
    <div class="cat-stage">
      <div class="nz-table-wrap">
        <table class="nz-table nz-table--striped">
          <thead><tr><th>Comprobación</th><th>Valor</th><th>Estado</th></tr></thead>
          <tbody>
{chr(10).join(fila(e, v, ok) for e, v, ok in comprobaciones)}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="cat-demo cat-in">
    <div class="cat-demo__title"><span class="cat-demo__num">2</span><span class="cat-demo__name">Por pack</span><span class="cat-demo__tag">objetos = clases .nz-* propias</span></div>
    <div class="cat-stage">
      <div class="nz-table-wrap">
        <table class="nz-table nz-table--striped">
          <thead><tr><th>Pack</th><th>Líneas</th><th>Objetos</th><th>Familias</th><th>Colores a mano</th><th>Grad.</th><th>!imp.</th></tr></thead>
          <tbody>{filas_packs}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="cat-demo cat-in">
    <div class="cat-demo__title"><span class="cat-demo__num">3</span><span class="cat-demo__name">Por categoría</span></div>
    <div class="cat-stage">
      <div class="nz-table-wrap">
        <table class="nz-table nz-table--striped">
          <thead><tr><th>#</th><th>Categoría</th><th>Pack</th><th>Objetos</th><th>Familias</th><th>Demos</th><th>Sin demo</th><th>Familias sin demo</th></tr></thead>
          <tbody>{filas_cat}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="cat-demo cat-in">
    <div class="cat-demo__title"><span class="cat-demo__num">4</span><span class="cat-demo__name">Coherencia</span></div>
    <div class="cat-stage">
      <div class="nz-stack nz-stack--sm">
        <p><strong>Objetos fantasma.</strong> {lista_fant}</p>
        <p><strong>Clases con más de un dueño.</strong> {lista_dup}</p>
        <p><strong>Tokens inexistentes.</strong> {lista_tok}</p>
      </div>
    </div>
  </section>

  <section class="cat-demo cat-in">
    <div class="cat-demo__title"><span class="cat-demo__num">5</span><span class="cat-demo__name">Margen de ampliación</span><span class="cat-demo__tag">familias sin variantes: {len(sin_var)}</span></div>
    <div class="cat-stage">
      <div class="nz-cluster">
        {''.join(f'<span class="nz-lbl">{html.escape(b)}</span>' for b in sin_var[:120])}
        {'<span class="nz-lbl nz-lbl--brand">…</span>' if len(sin_var) > 120 else ''}
      </div>
    </div>
  </section>
</main>

<footer class="cat-footer">
  Aurora · Informe de auditoría · {r['objetos_declarados']} objetos, {r['demos']} demos ·
  Hecho con ❤️ por David Antizar
</footer>
<script src="../js/catalog.js"></script>
</body>
</html>
"""
    packs, _, _, _ = bc.censo()
    pag, packs_usados = bc.inyecta_packs(pag, packs, "../packs/")
    (OUT / "index.html").write_text(pag, encoding="utf-8")
    print("audit/index.html generado ·", total_fallos, "avisos ·", len(packs_usados), "packs")


if __name__ == "__main__":
    main()
