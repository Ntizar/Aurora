#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita el responsive multifunción de Aurora (v9.2).

No mide píxeles (eso exige un navegador real): comprueba la estructura que hace
posible la medición y que la prueba viva exista y pase el lint:

  · ≥4 packs declaran container-type de verdad (no en comentarios)
  · ≥3 packs tienen escalón @media (min-width: 1440px)
  · ≥2 packs tienen escalón @media (min-width: 1200px)
  · .nz-cq y .nz-kanban-wrap existen en components.json (clase con demo)
  · stress-test.html existe, enlaza tokens + all.css y pasa auditar-uso.py con 0 fallos

Uso: python3 scripts/auditar-responsive.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
STRESS = ROOT / "stress-test.html"
MIN_PACKS_CQ = 4
MIN_PACKS_1440 = 3
MIN_PACKS_1200 = 2


def sin_comentarios(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def main() -> int:
    fallos = []

    cq, m1440, m1200, m640 = [], [], [], []
    for p in sorted(PACKS.glob("p*.css")):
        css = sin_comentarios(p.read_text(encoding="utf-8"))
        if re.search(r"container-type\s*:\s*(inline-size|size)", css):
            cq.append(p.name)
        if re.search(r"@media\s*\(\s*min-width\s*:\s*1440px\s*\)", css):
            m1440.append(p.name)
        if re.search(r"@media\s*\(\s*min-width\s*:\s*1200px\s*\)", css):
            m1200.append(p.name)
        if re.search(r"@media\s*\(\s*min-width\s*:\s*640px\s*\)", css):
            m640.append(p.name)

    if len(cq) < MIN_PACKS_CQ:
        fallos.append(f"container-type: {len(cq)} packs < {MIN_PACKS_CQ} ({', '.join(cq) or 'ninguno'})")
    if len(m1440) < MIN_PACKS_1440:
        fallos.append(f"@1440: {len(m1440)} packs < {MIN_PACKS_1440} ({', '.join(m1440) or 'ninguno'})")
    if len(m1200) < MIN_PACKS_1200:
        fallos.append(f"@1200: {len(m1200)} packs < {MIN_PACKS_1200} ({', '.join(m1200) or 'ninguno'})")
    if len(m640) < 10:
        fallos.append(f"@640: {len(m640)} packs < 10 — el mobile-first se ha debilitado")

    # Las clases nuevas deben existir en el censo (con demo).
    comp = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    objetos = comp.get("objetos", {})
    for clase in ("nz-cq", "nz-kanban-wrap"):
        if clase not in objetos:
            fallos.append(f"{clase} no está en components.json: falta demo en specs/")

    # La prueba viva.
    if not STRESS.is_file():
        fallos.append("falta stress-test.html")
    else:
        html = STRESS.read_text(encoding="utf-8")
        if "tokens.css" not in html:
            fallos.append("stress-test.html no enlaza tokens.css")
        if "packs/all.css" not in html:
            fallos.append("stress-test.html no enlaza packs/all.css")
        if html.count("nz-cq") < 4:
            fallos.append("stress-test.html no declara los 4 contenedores con .nz-cq")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "auditar-uso.py"), str(STRESS)],
            capture_output=True, text=True, cwd=ROOT,
        )
        if r.returncode != 0:
            fallos.append("stress-test.html no pasa auditar-uso.py:\n" + (r.stdout or r.stderr)[-1200:])

    if fallos:
        print("RESPONSIVE: FALLOS")
        for f in fallos:
            print(f"  ✗ {f}")
        return 1

    print(
        f"RESPONSIVE VÁLIDO · {len(cq)} packs con container queries ({', '.join(cq)}) · "
        f"{len(m1440)} con @1440 · {len(m1200)} con @1200 · {len(m640)} con @640 · stress-test OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
