# -*- coding: utf-8 -*-
"""Identifica los elementos clipados: demo dueña + cadena de clases + ancestro que recorta."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\d_ant\Projects\Aurora-7")

JS = r"""
() => {
  const vw = window.innerWidth;
  const res = [];
  const demoDe = (el) => {
    let a = el.closest('section.cat-demo');
    return a ? (a.getAttribute('data-cat') || '') : 'FUERA-DE-DEMO';
  };
  const clipadorDe = (el) => {
    let a = el.parentElement;
    while (a && a !== document.body) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'hidden' || cs.overflowX === 'clip') return String(a.classList[0] || a.tagName);
      a = a.parentElement;
    }
    return '?';
  };
  const enScrollLegal = (el) => {
    let a = el.parentElement;
    while (a && a !== document.body) {
      const c = getComputedStyle(a);
      if (c.overflowX === 'auto' || c.overflowX === 'scroll') return true;
      a = a.parentElement;
    }
    return false;
  };
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const rc = el.getBoundingClientRect();
    if (rc.width === 0 && rc.height === 0) continue;
    if (rc.right > vw + 1 && !enScrollLegal(el)) {
      res.push({
        demo: demoDe(el).slice(0, 50),
        tag: el.tagName, cls: String(el.className).slice(0, 60),
        w: Math.round(rc.width), right: Math.round(rc.right),
        clipador: clipadorDe(el),
        texto: (el.textContent || '').trim().slice(0, 30),
      });
    }
  }
  return res.slice(0, 20);
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 320, "height": 800}, is_mobile=True, has_touch=True)
    pag = ctx.new_page()
    for nombre in ["01-layout", "10-commerce", "13-charts", "15-apps"]:
        pag.goto(f"file:///{ROOT.as_posix()}/paginas/{nombre}.html")
        pag.wait_for_load_state("load")
        print(f"\n=== {nombre} ===")
        for r in pag.evaluate(JS)[:12]:
            print(f"  <{r['tag']} {r['cls']}> w={r['w']} right={r['right']} clipador={r['clipador']}")
            print(f"     demo={r['demo']}")
            print(f"     texto=«{r['texto']}»")
    b.close()
