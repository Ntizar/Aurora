# -*- coding: utf-8 -*-
"""Tabla global: que demo empuja el min-content de cada pagina que desborda."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\d_ant\Projects\Aurora-7")
PAGINAS = ["06-feedback", "07-overlays", "10-commerce", "13-charts", "15-apps"]

JS = r"""
() => {
  const se = document.scrollingElement;
  const base = se.scrollWidth;
  const fuera = [];
  const medir = (el, etiqueta) => {
    const prev = el.style.display;
    el.style.display = 'none';
    const ahora = se.scrollWidth;
    el.style.display = prev;
    if (ahora < base) fuera.push({ etiqueta, delta: base - ahora });
  };
  for (const s of document.querySelectorAll('section.cat-demo')) {
    medir(s, (s.getAttribute('data-cat') || '').split(' ').slice(0, 4).join(' '));
  }
  for (const el of document.querySelectorAll('body > *, main > *')) {
    if (el.matches('section.cat-demo')) continue;
    medir(el, 'estructura:' + el.tagName + '.' + String(el.classList[0] || ''));
  }
  fuera.sort((a, b) => b.delta - a.delta);
  return { base, fuera };
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 320, "height": 800}, is_mobile=True, has_touch=True)
    pag = ctx.new_page()
    for nombre in PAGINAS:
        pag.goto(f"file:///{ROOT.as_posix()}/paginas/{nombre}.html")
        pag.wait_for_load_state("load")
        r = pag.evaluate(JS)
        print(f"\n=== {nombre} base={r['base']} ===")
        for f in r["fuera"][:8]:
            print(f"  +{f['delta']:>3}px  {f['etiqueta'][:80]}")
    b.close()
