# -*- coding: utf-8 -*-
"""Caza el origen del overflow que no se ve: elementos con scrollWidth interno > viewport."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PAG = Path(r"C:\Users\d_ant\Projects\Aurora-7\paginas\07-overlays.html")

JS = r"""
() => {
  const vw = window.innerWidth;
  const filas = [];
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    if (el.scrollWidth > vw + 1) {
      filas.push({
        cls: String(el.classList[0] || el.tagName),
        id: el.id || '',
        scrollW: el.scrollWidth,
        clientW: el.clientWidth,
        ownW: Math.round(el.getBoundingClientRect().width),
        pos: cs.position,
        ovX: cs.overflowX,
        primera: (el.firstElementChild ? String(el.firstElementChild.classList[0] || el.firstElementChild.tagName) : '')
      });
    }
  }
  filas.sort((a, b) => b.scrollW - a.scrollW);
  return filas.slice(0, 14);
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
