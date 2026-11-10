#!/usr/bin/env python3
"""Audita el desborde horizontal de TODOS los objetos del catálogo.

Monta cada demo de specs/*.json en una caja de 320 px (sin el chrome del
catálogo, solo tokens + packs), mide en Chrome headless y falla si algún objeto
esconde contenido sin dar acceso (overflow hidden/clip con scrollWidth mayor) o
si pinta fuera de su caja sin un ancestro que recorte o desplace.

Uso:
  python scripts/auditar-desborde.py            # informe y veredicto
  python scripts/auditar-desborde.py --ancho 280
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
import os
import shutil

CHROME = (os.environ.get("CHROME") or shutil.which("chromium") or shutil.which("google-chrome")
          or "/home/nan/.local/bin/chromium")

# Páginas y primitivas de página: su comportamiento depende del viewport por diseño.
SHELLS = (
    "nz-holy", "nz-bleed", "nz-drawer-layout", "nz-dash-grid", "nz-cq",
    "nz-grid-12", "nz-root", "nz-container", "nz-hero-bleed",
)

JS = """
const EXENTO = /nz-(truncate|visually-hidden|vh|sr-only-focusable|mapa-placeholder)/;
const SHELL = SHELLS_JSON;
function medir(){
  const res=[]; const raiz=document.getElementById('raiz');
  for(const d of DEMOS){
    if (SHELL.some(s=>d.t.includes(s))) continue;
    raiz.innerHTML='';
    const caja=document.createElement('div'); caja.style.width=ANCHO+'px';
    const env=document.createElement('div'); env.innerHTML=d.m; caja.appendChild(env); raiz.appendChild(caja);
    if([...caja.querySelectorAll('*')].some(e=>getComputedStyle(e).position==='fixed')) continue;
    const r0=caja.getBoundingClientRect(); const cortes=[], fugas=[];
    caja.querySelectorAll('*').forEach(el=>{
      if(EXENTO.test(el.className||'')||/demo-box/.test(el.className||'')) return;
      const cs=getComputedStyle(el);
      if(cs.textOverflow==='ellipsis') return;
      if((cs.overflowX==='hidden'||cs.overflowX==='clip') && el.scrollWidth>el.clientWidth+2 && el.clientWidth>0)
        cortes.push({q:(el.className||el.tagName).toString().slice(0,44),sw:el.scrollWidth,cw:el.clientWidth});
      const b=el.getBoundingClientRect();
      if(b.width>0 && b.right>r0.right+2 && cs.position!=='fixed' && cs.position!=='absolute'){
        let p=el.parentElement,cont=false;
        while(p&&p!==caja){const pc=getComputedStyle(p); if(['hidden','clip','auto','scroll'].includes(pc.overflowX)){cont=true;break;} p=p.parentElement;}
        if(!cont) fugas.push({q:(el.className||el.tagName).toString().slice(0,44),r:Math.round(b.right-r0.right)});
      }
    });
    if(cortes.length||fugas.length) res.push({f:d.f,t:d.t,cortes:cortes.slice(0,2),fugas:fugas.slice(0,2)});
  }
  document.getElementById('salida').textContent = JSON.stringify({total:DEMOS.length,mal:res.length,res:res});
}
medir();
"""


def construir(ancho: int) -> str:
    demos = []
    for sp in sorted((RAIZ / "specs").glob("*.json")):
        spec = json.loads(sp.read_text())
        for x in spec.get("demos", []):
            mk = x.get("markup") or x.get("html") or ""
            if mk.strip():
                demos.append({"f": sp.stem, "t": (x.get("tag") or x.get("titulo") or "").strip()[:70], "m": mk})
    css = sorted((RAIZ / "packs").glob("*.css"))
    links = "\n".join(f'<link rel="stylesheet" href="file://{c}">' for c in css)
    js = JS.replace("SHELLS_JSON", json.dumps(list(SHELLS))).replace("ANCHO", str(ancho))
    return (
        '<!doctype html><html lang="es" data-nz-marca="aurora"><head><meta charset="utf-8">'
        f'<link rel="stylesheet" href="file://{RAIZ}/tokens.css">\n{links}\n'
        '<style>body{margin:0}</style></head><body>'
        '<div id="raiz"></div><pre id="salida">PENDIENTE</pre>'
        f'<script>const DEMOS={json.dumps(demos, ensure_ascii=False)};</script>'
        f'<script>{js}</script></body></html>'
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ancho", type=int, default=320)
    args = ap.parse_args()

    html = construir(args.ancho)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
        ruta = fh.name
    try:
        out = subprocess.run(
            [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--hide-scrollbars", "--virtual-time-budget=20000", "--dump-dom", f"file://{ruta}"],
            capture_output=True, text=True, timeout=180,
        ).stdout
    finally:
        Path(ruta).unlink(missing_ok=True)

    m = re.search(r'<pre id="salida">(.*?)</pre>', out, re.S)
    if not m or m.group(1).strip() == "PENDIENTE":
        print("No se pudo medir en Chrome (¿ruta de chromium?)", file=sys.stderr)
        return 2
    datos = json.loads(m.group(1))

    print(f"DESBORDE HORIZONTAL · caja de {args.ancho} px · {datos['total']} objetos")
    for r in datos["res"]:
        cortes = "; ".join(f"{c['q']} {c['cw']}->{c['sw']}" for c in r["cortes"])
        fugas = "; ".join(f"{c['q']}+{c['r']}" for c in r["fugas"])
        print(f"  ✗ [{r['f']}] {r['t'][:46]:46s} corta: {cortes[:60]}  sale: {fugas[:52]}")
    if datos["mal"]:
        print(f"\nRESULTADO: NO VÁLIDO ❌ — {datos['mal']} objetos esconden o se salen de su caja")
        return 1
    print("\nRESULTADO: VÁLIDO ✅ — ningún objeto esconde contenido a este ancho")
    return 0


if __name__ == "__main__":
    sys.exit(main())
