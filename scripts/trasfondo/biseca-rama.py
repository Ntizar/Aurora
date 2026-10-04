# -*- coding: utf-8 -*-
"""Biseccion recursiva por rama: localiza el nodo hoja que empuja el min-content."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\d_ant\Projects\Aurora-7")
PAGINAS = ["06-feedback", "07-overlays", "13-charts"]

JS = r"""
() => {
  const se = document.scrollingElement;
  const base = se.scrollWidth;
  const ruta = [];
  let actual = document.body;
  for (let nivel = 0; nivel < 14; nivel++) {
    const hijos = [...actual.children];
    let mejor = null;
    for (const h of hijos) {
      const prev = h.style.display;
      h.style.display = 'none';
      const sw = se.scrollWidth;
      h.style.display = prev;
      if (!mejor || sw < mejor.sw) mejor = { sw, el: h };
    }
    if (!mejor || mejor.sw >= base) break;
    ruta.push({
      nivel,
      tag: mejor.el.tagName,
      cls: String(mejor.el.classList[0] || '') + (mejor.el.id ? '#' + mejor.el.id : ''),
      dataCat: mejor.el.getAttribute ? mejor.el.getAttribute('data-cat') : null,
      sw: mejor.sw,
    });
    base2 = base; // (no usado)
    actual = mejor.el;
    if (mejor.sw <= window.innerWidth + 1) break;
  }
  return { base: document.scrollingElement.scrollWidth, ruta };
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
        print(f"\n=== {nombre} (base {r['base']}) ===")
        for paso in r["ruta"]:
            extra = f" dataCat={paso['dataCat'][:60]}" if paso["dataCat"] else ""
            print(f"  n{paso['nivel']} sw={paso['sw']:>4}  <{paso['tag']} .{paso['cls']}>{extra}")
    b.close()
