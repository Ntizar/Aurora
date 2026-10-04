# -*- coding: utf-8 -*-
"""Donde estan los +5px de 06-feedback: biseccion dentro de la demo nz-progress."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PAG = Path(r"C:\Users\d_ant\Projects\Aurora-7\paginas\06-feedback.html")

JS = r"""
() => {
  const se = document.scrollingElement;
  const base = se.scrollWidth;
  const s = [...document.querySelectorAll('section.cat-demo')].find(x => (x.getAttribute('data-cat')||'').includes('nz-progress'));
  const res = { base, seccionW: Math.round(s.getBoundingClientRect().width) };
  const prueba = (el, nombre) => {
    if (!el) { res[nombre] = 'no encontrado'; return; }
    const prev = el.style.display;
    el.style.display = 'none';
    res[nombre] = se.scrollWidth;
    el.style.display = prev;
  };
  const [title, stage, code] = s.children;
  prueba(title, 'sinTitle');
  prueba(stage, 'sinStage');
  prueba(code, 'sinCode');
  const prog = stage.querySelector('.nz-progress');
  prueba(prog, 'sinProgress');
  const bar = stage.querySelector('.nz-progress__bar');
  prueba(bar, 'sinBar');
  const tag = s.querySelector('.cat-demo__tag');
  prueba(tag, 'sinTag');
  const num = s.querySelector('.cat-demo__num');
  prueba(num, 'sinNum');
  const name = s.querySelector('.cat-demo__name');
  prueba(name, 'sinName');
  return res;
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
