# -*- coding: utf-8 -*-
"""Anatomia de la demo nz-drawer: anchos reales de su arbol y ancestros con transform."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PAG = Path(r"C:\Users\d_ant\Projects\Aurora-7\paginas\07-overlays.html")

JS = r"""
() => {
  const secciones = [...document.querySelectorAll('section.cat-demo')];
  const s = secciones.find(x => (x.getAttribute('data-cat')||'').includes('nz-drawer'));
  const vw = window.innerWidth;
  const anchos = [];
  const escan = (el, nivel) => {
    if (nivel > 4) return;
    const rc = el.getBoundingClientRect();
    if (rc.right > vw + 1 || rc.width > vw + 1) {
      anchos.push({
        niv: nivel, tag: el.tagName, cls: String(el.classList[0]||''),
        w: Math.round(rc.width), x: Math.round(rc.left),
        pos: getComputedStyle(el).position,
      });
    }
    for (const h of el.children) escan(h, nivel + 1);
  };
  escan(s, 0);
  // ancestros con transform (convierten fixed en absoluto)
  const ancestros = [];
  let a = s.parentElement;
  while (a && a !== document.body) {
    const cs = getComputedStyle(a);
    if (cs.transform !== 'none' || cs.filter !== 'none' || cs.willChange.includes('transform')) {
      ancestros.push({ cls: String(a.classList[0]||a.tagName), transform: cs.transform.slice(0,40) });
    }
    a = a.parentElement;
  }
  return { vw, anchos: anchos.slice(0, 20), ancestrosConTransform: ancestros,
           html: s.outerHTML.slice(0, 600) };
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
