# -*- coding: utf-8 -*-
"""Consolida las clases tactiles pequenas de todo el catalogo con sus tamanos tipicos."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\d_ant\Projects\Aurora-7")
datos = json.loads((ROOT / "audit" / "movil.json").read_text(encoding="utf-8"))

tam = {}      # clase -> Counter de "wxh"
total = Counter()
for pag, por_vp in datos.items():
    for vp, d in por_vp.items():
        if str(vp) != "320":
            continue
        for it in d["tactil"]["peq"]:
            k = it["clase"]
            total[k] += 1
            tam.setdefault(k, Counter())[f"{it['w']}x{it['h']}"] += 1

print(f"{'clase':32} {'n':>4}  tamanos tipicos")
for k, n in total.most_common(30):
    print(f"{k:32} {n:>4}  {dict(tam[k].most_common(4))}")
