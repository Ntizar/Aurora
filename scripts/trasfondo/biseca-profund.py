# -*- coding: utf-8 -*-
"""Biseccion profunda DENTRO de main.nz-container hasta la hoja culpable."""
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
  let actual = document.querySelector('main#contenido');
  if (!actual) return { base, ruta: [{error: 'no main'}] };
  for (let nivel = 0; nivel < 16; nivel++) {
    const hijos = [...actual.children];
    if (!hijos.length) break;
    let mejor = null;
    for (const h of hijos) {
      const prev = h.style.display;
      h.style.display = 'none';
      const sw = se.scrollWidth;
      h.style.display = prev;
      if (!mejor || sw < mejor.sw) mejor = { sw, el: h };
    }
    if (mejor.sw >= base) break;
    ruta.push({
      nivel,
      tag: mejor.el.tagName,
      cls: String(mejor.el.classList[0] || ''),
      dataCat: mejor.el.getAttribute ? mejor.el.getAttribute('data-cat') : null,
      sw: mejor.sw,
    });
    actual = mejor.el;
    if (mejor.sw <= 321) break;
  }
  // hoja: listar sus hijos con anchos getBoundingClientRect (viewport esta expandido)
  const hoja = [...actual.children].slice(0, 12).map(h => {
    const rc = h.getBoundingClientRect();
    return { tag: h.tagName, cls: String(h.classList[0] || ''), w: Math.round(rc.width), x: Math.round(rc.left) };
  });
  return { base, ruta, hojaDe: actual.tagName + '.' + String(actual.classList[0] || ''), hoja };
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
        print(f"\n=== {nombre} (base {r['base']}) hoja={r.get('hojaDe')}")
        for paso in r["ruta"]:
            extra = f" dataCat={str(paso['dataCat'])[:60]}" if paso.get("dataCat") else ""
            print(f"  n{paso['nivel']} sw={paso['sw']:>4}  <{paso['tag']} .{paso['cls']}>{extra}")
        for h in r.get("hoja", [])[:10]:
            print(f"    hoja: <{h['tag']} .{h['cls']}> w={h['w']} x={h['x']}")
    b.close()
