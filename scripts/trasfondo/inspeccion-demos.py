# -*- coding: utf-8 -*-
"""Inspeccion rapida: como van las demos en las paginas del catalogo (inline vs iframe)."""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\d_ant\Projects\Aurora-7")
for pag in sorted((ROOT / "paginas").glob("*.html")):
    html = pag.read_text(encoding="utf-8")
    n_iframes = len(re.findall(r"<iframe", html))
    n_demos = len(re.findall(r'class="demo', html))
    print(f"{pag.name}: iframes={n_iframes} demos_inline={n_demos}")
