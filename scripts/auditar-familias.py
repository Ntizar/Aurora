#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurora — repaso OBJETO A OBJETO (el método de COMPOSICION.md §... del plan)

Recorre las 350 familias del sistema y emite una ficha por familia con 8
comprobaciones y un veredicto. No se hace mirando: se hace cruzando el CSS
declarado con los specs, las recetas y las reglas del léxico.

Salida:
  · audit/familias.csv   — la ficha completa (editable, revisable)
  · resumen por pantalla — el mapa de averías y de dónde faltan opciones

Uso: python scripts/auditar-familias.py
"""
from __future__ import annotations
import csv
import json
import pathlib
import re
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent

CLASE = re.compile(r"\.(nz-[A-Za-z0-9_-]+)")
SELECTOR_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
PX = re.compile(r"\b\d+(?:\.\d+)?px\b")
NUM_SUFIJO = re.compile(r"^(nz-[a-z-]+?)-(\d+)$")

# Conceptos que se repiten entre familias distintas (posible solape)
CONCEPTOS = [
    ("etiqueta", {"nz-lbl", "nz-badge", "nz-chip", "nz-eyebrow", "nz-caps", "nz-kbd", "nz-atajo-teclado"}),
    ("titulo", {"nz-h1", "nz-h2", "nz-h3", "nz-h4", "nz-h5", "nz-h6", "nz-display", "nz-text"}),
    ("aviso", {"nz-alert", "nz-callout", "nz-nota", "nz-banner", "nz-toast"}),
    ("vacio", {"nz-empty", "nz-errorstate", "nz-appempty"}),
    ("carga", {"nz-spinner", "nz-spin", "nz-skeleton", "nz-progress", "nz-loading-bar", "nz-pulse"}),
    ("tarjeta", {"nz-article", "nz-bento", "nz-thirds", "nz-kpi", "nz-record"}),
]
DEUDA_V6 = re.compile(r"glass|orb|mesh|gradient|skin|aurora-")
SIN_VARIANTE_RELEVANTE = 0  # las que no tienen ni un modificador


def bloques_del_pack(ruta: pathlib.Path):
    """[(selector, cuerpo)] del CSS, entrando dentro de @media."""
    css = ruta.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return SELECTOR_RE.findall(css)


def main() -> int:
    datos = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    objetos = datos["objetos"]

    # CSS por pack, indexado por clase declarada
    por_pack = defaultdict(list)
    for ruta in sorted((ROOT / "packs").glob("p*.css")):
        por_pack[ruta.name] = bloques_del_pack(ruta)

    recetas = ""
    for r in sorted((ROOT / "recetas").glob("*.html")):
        recetas += r.read_text(encoding="utf-8")

    familias = sorted(objetos)
    bases = {f.rsplit("-", 1)[0] for f in familias if "-" in f}
    conteo_bases = Counter(f.rsplit("-", 1)[0] for f in familias if "-" in f)

    filas = []
    for fam in familias:
        o = objetos[fam]
        clases, mods, partes = o["clases"], o["modificadores"], o["partes"]

        # CSS propio de la familia (bloques que la mencionan)
        cuerpo = "\n".join(b for sel, b in por_pack.get(o["pack"], [])
                           if any(c in sel for c in clases))
        hex_crudo = len(HEX.findall(cuerpo))
        px_crudo = len(PX.findall(cuerpo))
        en_recetas = sum(1 for c in clases if c in recetas)

        m = NUM_SUFIJO.match(fam)
        grupo_num = m.group(1) if m else ""
        casi_dup = ""
        if fam.endswith("s") and fam[:-1] in objetos:
            casi_dup = f"{fam[:-1]} (sin s)"
        elif fam + "s" in objetos:
            casi_dup = f"{fam}s (con s)"
        solape = next((n for n, s in CONCEPTOS if fam in s and len(s & set(familias)) > 1), "")
        deuda = "sí" if DEUDA_V6.search(fam) else ""
        alias = next((k for k, v in datos.get("alias", {}).items() if v == fam), "")

        # ---- veredicto ----
        if deuda:
            veredicto = "RETIRAR (deuda v6)"
        elif hex_crudo:
            veredicto = "ARREGLAR (color a mano)"
        elif not mods and not en_recetas:
            veredicto = "SIN VARIANTES"
        elif casi_dup:
            veredicto = "PAR singular/plural"
        elif grupo_num:
            veredicto = "AGRUPAR (numerico)"
        elif solape:
            veredicto = f"REVISAR (solape: {solape})"
        elif len(mods) >= 6 and clases:
            veredicto = "OK (completa)"
        else:
            veredicto = "OK"

        filas.append({
            "familia": fam, "pack": o["pack"], "categoria": o["categoria"],
            "clases": len(clases), "modificadores": len(set(mods)), "partes": len(set(partes)),
            "hex_crudo": hex_crudo, "px_crudo": px_crudo, "en_recetas": en_recetas,
            "alias_es": alias, "grupo_num": grupo_num, "casi_duplicado": casi_dup,
            "solape": solape, "deuda_v6": deuda, "veredicto": veredicto,
        })

    destino = ROOT / "audit" / "familias.csv"
    with destino.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    cuenta = Counter(f["veredicto"] for f in filas)
    print(f"Familias revisadas: {len(filas)}  →  {destino.relative_to(ROOT)}")
    print()
    for v, n in cuenta.most_common():
        print(f"  {n:4d}  {v}")
    print()
    print(f"Familias con 0 modificadores: {sum(1 for f in filas if f['modificadores'] == 0)}")
    print(f"Familias usadas en recetas/: {sum(1 for f in filas if f['en_recetas'])}")
    print(f"Familias con color a mano:    {sum(1 for f in filas if f['hex_crudo'])}")
    print()
    print("Grupos numéricos (candidatos a colapsar):",
          ", ".join(sorted({f["grupo_num"] for f in filas if f["grupo_num"]})[:12]))
    print()
    print("Casi-duplicados:")
    for f in filas:
        if f["casi_duplicado"]:
            print(f"   {f['familia']}  ↔  {f['casi_duplicado']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
