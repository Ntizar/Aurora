#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auditoría de tema de Aurora: ¿todo sobrevive al modo oscuro?

El modo oscuro solo redefine los tokens semánticos (--nz-bg, --nz-text, --nz-surface...).
Si un pack usa directamente un token de la PALETA (--nz-gray-900, --nz-blue-100...)
para pintar texto o bordes sin declarar su propio fondo, ese pack se rompe al
cambiar de tema: texto oscuro sobre superficie oscura.

Este auditor busca exactamente eso:

  1. Reglas que pintan texto (color/fill/stroke) con un token de paleta y NO
     declaran fondo propio en la misma regla  → posible texto invisible en oscuro.
  2. Reglas que pintan fondo de paleta y NO declaran color propio → posible
     texto heredado ilegible.
  3. Tokens de paleta usados en packs que NO existen en tokens.css.

Uso:  python scripts/audit-tema.py        (exit 1 si hay algo roto)
"""
from __future__ import annotations

import re
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
TOKENS = ROOT / "tokens.css"

# un token "de paleta" es el que lleva sufijo numérico de escala
PALETA = re.compile(r"--nz-(blue|orange|gray|green|red|amber)-\d+$")
TOKEN = re.compile(r"var\((--nz-[a-z0-9-]+)")
PROPS_FG = ("color", "fill", "stroke")
PROPS_BG = ("background", "background-color")
PROPS_BD = ("border-color", "border-top-color", "border-bottom-color")


def reglas(css: str):
    """Devuelve (selector, declaraciones) de cada regla, a cualquier profundidad."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    pila, buf = [], ""
    i = 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            pila.append(buf.strip())
            buf = ""
        elif ch == "}":
            preludio = pila.pop() if pila else ""
            if pila and preludio and not preludio.startswith("@"):
                yield preludio, buf
            buf = ""
        else:
            buf += ch
        i += 1


def declaraciones(txt: str):
    for d in txt.split(";"):
        if ":" in d:
            prop, val = d.split(":", 1)
            yield prop.strip().lower(), val.strip()


def analiza(nombre: str, css: str):
    fallos, avisos = [], []
    for sel, cuerpo in reglas(css):
        decls = list(declaraciones(cuerpo))
        fg = [t for p, v in decls if p in PROPS_FG for t in TOKEN.findall(v) if PALETA.match(t)]
        bg = [t for p, v in decls if p in PROPS_BG for t in TOKEN.findall(v) if PALETA.match(t)]
        bg_literal = any(p in PROPS_BG and ("var(--nz-" not in v and v not in ("transparent", "none", "inherit", "currentColor")) for p, v in decls)
        bd = [t for p, v in decls if p in PROPS_BD for t in TOKEN.findall(v) if PALETA.match(t)]
        if fg and not bg and not bg_literal:
            fallos.append((sel, "texto de paleta sin fondo propio", fg))
        if bg and not fg:
            avisos.append((sel, "fondo de paleta sin color propio", bg))
        if bd and not bg and not bg_literal and not fg:
            avisos.append((sel, "borde de paleta sin fondo propio", bd))
    return fallos, avisos


def main() -> int:
    tokens = TOKENS.read_text(encoding="utf-8")
    declarados = set(re.findall(r"(--nz-[a-z0-9-]+)\s*:", tokens))
    total_f = total_a = 0
    print("Aurora · auditoría de tema (supervivencia al modo oscuro)\n")
    for pack in sorted(PACKS.glob("p[0-9]*.css")):
        if pack.name.startswith("p0"):
            continue
        css = pack.read_text(encoding="utf-8")
        usados = set(TOKEN.findall(css))
        fantasmas = sorted(t for t in usados if t not in declarados)
        fallos, avisos = analiza(pack.name, css)
        total_f += len(fallos) + len(fantasmas)
        total_a += len(avisos)
        if fallos or fantasmas or avisos:
            print(f"{pack.name}: {len(fallos)} fallos · {len(avisos)} avisos · {len(fantasmas)} tokens inexistentes")
            for t in fantasmas:
                print(f"    ✗ token inexistente: {t}")
            for sel, motivo, toks in fallos:
                print(f"    ✗ {sel}  [{motivo}: {', '.join(toks)}]")
            for sel, motivo, toks in avisos:
                print(f"    · {sel}  [{motivo}: {', '.join(toks)}]")
    print(f"\nTOTAL: {total_f} fallos · {total_a} avisos")
    if total_f:
        print("RESULTADO: NO VÁLIDO — hay reglas que se rompen en modo oscuro")
        return 1
    print("RESULTADO: VÁLIDO — los packs usan tokens semánticos o declaran su propio fondo ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
