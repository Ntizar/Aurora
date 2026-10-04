# -*- coding: utf-8 -*-
"""Biseccion: que demo concreta empuja el scrollWidth del documento en 07-overlays."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PAG = Path(r"C:\Users\d_ant\Projects\Aurora-7\paginas\07-overlays.html")

JS = r"""
() => {
  const se = document.scrollingElement;
  const base = se.scrollWidth;
  const culpables = [];
  const secciones = document.querySelectorAll('section.cat-demo');
  for (const s of secciones) {
    const prev = s.style.display;
    s.style.display = 'none';
    const ahora = se.scrollWidth;
    s.style.display = prev;
    if (ahora < base) culpables.push({ dataCat: s.getAttribute('data-cat'), scrollW: ahora });
  }
  // si ninguna seccion es, buscar mas arriba: hijos directos de main y body
  if (!culpables.length) {
    for (const el of document.querySelectorAll('main > *, body > *')) {
      const prev = el.style.display;
      el.style.display = 'none';
      const ahora = se.scrollWidth;
      el.style.display = prev;
      if (ahora < base) culpables.push({ nodo: el.tagName + '.' + String(el.classList[0]||''), scrollW: ahora });
    }
  }
  return { base, culpables: culpables.slice(0, 12) };
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 320, "height": 800}, is_mobile=True, has_touch=True)
    pag = ctx.new_page()
    pag.goto(f"file:///{PAG.as_posix()}")
    pag.wait_for_load_state("load")
    print(json.dumps(pag.evaluate(JS), ensure_ascii=False, indent=1))
    b.close()
