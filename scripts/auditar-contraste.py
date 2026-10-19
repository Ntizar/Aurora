#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurora — auditoría de contraste de tokens (WCAG) + paridad OKLch
=================================================================

Audita los PARES SEMANTICOS de color de tokens.css en cada tema (claro y oscuro)
y en cada preset de marca (marcas/*.css), resolvendo cadenas var() hasta el hex.
Tambien verifica la paridad de la doble declaracion oklch(): cada --nz-x: #hex
debe llevar debajo su oklch(...) y la conversión debe devolver el hex original.

Umbrales minimos por rol (WCAG 2.1):
  - texto normal:            4.5:1
  - texto grande / UI 3:1:   3.0:1
  - informativo (solo datos): se informa, avisa si < 3.0
Los bordes son decorativos (separan, no codifican informacion): solo se informa.

Uso:
    python scripts/auditar-contraste.py            # informe + exit 1 si falla
    python scripts/auditar-contraste.py --informe  # solo informe, exit 0

Hecho con ❤️ por David Antizar
"""
from __future__ import annotations
import math
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ADVISORY = "--informe" in sys.argv

# ---------------------------------------------------------------- conversion
def _lin(u: float) -> float:
    u /= 255.0
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4

def luminancia(h: str) -> float:
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contraste(a: str, b: str) -> float:
    l1, l2 = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

def oklch_a_hex(L: float, C: float, H: float) -> str:
    h = math.radians(H)
    a, bb = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * bb
    m_ = L - 0.1055613458 * a - 0.0638541728 * bb
    s_ = L - 0.0894841775 * a - 1.2914855480 * bb
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    def enc(c: float) -> int:
        c = max(0.0, min(1.0, c))
        u = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        return round(u * 255)
    return "#{:02x}{:02x}{:02x}".format(enc(r), enc(g), enc(b))

def hex_a_oklch(h: str):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    C = math.sqrt(a * a + bb * bb)
    H = math.degrees(math.atan2(bb, a)) % 360
    return L, C, H

# ---------------------------------------------------------------- css parsing
RE_DECL = re.compile(r"(--nz-[a-z0-9-]+)\s*:\s*([^;]+);")
RE_VAR = re.compile(r"^var\(\s*(--nz-[a-z0-9-]+)\s*(?:,\s*([^)]+))?\)$")
RE_MIX = re.compile(r"^color-mix\(\s*in\s+oklab\s*,\s*(#[0-9a-fA-F]{6}|var\(\s*(--nz-[a-z0-9-]+)\s*\))\s+([\d.]+)%,\s*transparent\s*\)$")

def declaraciones(css: str) -> dict:
    """{token: valor} — con doble declaracion hex+oklch, manda el hex (el fallback garantizado);
    si solo hay var()/oklch(), el primero. La paridad oklch garantiza que hex y oklch coinciden."""
    vals: dict[str, list] = {}
    for k, v in RE_DECL.findall(css):
        vals.setdefault(k, []).append(v.strip())
    out = {}
    for k, lista in vals.items():
        out[k] = next((x for x in lista if x.startswith("#")), lista[0])
    return out

def _bloque_balanceado(css: str, ini_llave: int) -> str:
    prof = 0
    for j in range(ini_llave, len(css)):
        if css[j] == "{":
            prof += 1
        elif css[j] == "}":
            prof -= 1
            if prof == 0:
                return css[ini_llave:j + 1]
    return css[ini_llave:]

def bloques(tokens_css: str):
    """[(nombre, css_base_sin_dark, css_del_tema)] — claro y oscuro."""
    m = re.search(r'\[data-nz-theme="dark"\]\s*\{', tokens_css)
    if not m:
        return [("claro", tokens_css, tokens_css)]
    dark = _bloque_balanceado(tokens_css, m.end() - 1)
    base = tokens_css.replace(dark, "")
    return [("claro", base, base), ("oscuro", base, dark)]

def resuelve(tok: str, decl: dict, bg_alpha: str | None = None, prof: int = 0) -> str | None:
    """Resuelve var() hasta hex. bg_alpha: hex sobre el que componer color-mix ... transparent."""
    if prof > 6 or tok not in decl:
        return None
    v = decl[tok]
    if v.startswith("#"):
        return v
    m = RE_VAR.match(v)
    if m:
        return resuelve(m.group(1), decl, bg_alpha, prof + 1)
    m = RE_MIX.match(v)
    if m and bg_alpha:
        fuente = m.group(1) if m.group(1).startswith("#") else resuelve(m.group(2), decl, bg_alpha, prof + 1)
        if not fuente:
            return None
        a = float(m.group(3)) / 100.0
        f, b = fuente.lstrip("#"), bg_alpha.lstrip("#")
        mix = "#{:02x}{:02x}{:02x}".format(
            *(round(int(f[i:i + 2], 16) * a + int(b[i:i + 2], 16) * (1 - a)) for i in (0, 2, 4)))
        return mix
    return None

# ---------------------------------------------------------------- pares
# (nombre, fg, bg, minimo)  -- None = informativo
PARES = [
    ("texto normal s/ fondo",            "--nz-text",        "--nz-bg",        4.5),
    ("texto normal s/ superficie",       "--nz-text",        "--nz-surface",   4.5),
    ("texto secundario s/ fondo",        "--nz-text-soft",   "--nz-bg",        4.5),
    ("texto terciario s/ fondo",         "--nz-text-mute",   "--nz-bg",        4.5),
    ("texto tenue s/ fondo (solo datos)","--nz-text-faint",  "--nz-bg",        None),
    ("texto invertido s/ marca",         "--nz-text-invert", "--nz-brand",     4.5),
    ("tinta acento s/ relleno acento",   "--nz-accent-ink",  "--nz-accent",    4.5),
    ("texto acento s/ fondo",            "--nz-accent-text", "--nz-bg",        4.5),
    ("texto acento s/ acento-soft",      "--nz-accent-text", "--nz-accent-soft", 4.5),
    ("marca s/ fondo (enlaces)",         "--nz-brand",       "--nz-bg",        4.5),
    ("acento fuerte s/ fondo (bordes)",  "--nz-accent-strong","--nz-bg",       3.0),
]

def audita_tema(nombre: str, decl: dict):
    bg = resuelve("--nz-bg", decl)
    filas = []
    for nombre_par, fg, bg_tok, minimo in PARES:
        fv = resuelve(fg, decl, bg_alpha=bg)
        bv = resuelve(bg_tok, decl, bg_alpha=bg)
        if fv is None or bv is None or bg is None:
            filas.append((nombre_par, None, None, minimo, f"no resoluble ({fg}={fv}, {bg_tok}={bv})"))
            continue
        r = contraste(fv, bv)
        if minimo is None:
            estado = "info" if r >= 3.0 else "aviso"
        else:
            estado = "ok" if r >= minimo else "FALLA"
        filas.append((nombre_par, r, (fv, bv), minimo, estado))
    return filas

# ---------------------------------------------------------------- paridad oklch
RE_HEX = re.compile(r"^\s*(--nz-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6});\s*$")
RE_OKL = re.compile(r"^\s*(--nz-[a-z0-9-]+):\s*oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\);\s*$")

def paridad_oklch(tokens_css: str):
    lineas = tokens_css.splitlines()
    faltan, descoordinados = [], []
    for i, l in enumerate(lineas):
        m = RE_HEX.match(l)
        if not m:
            continue
        tok, h = m.group(1), m.group(2)
        sig = lineas[i + 1] if i + 1 < len(lineas) else ""
        m2 = RE_OKL.match(sig)
        if not m2 or m2.group(1) != tok:
            faltan.append(tok)
            continue
        L, C, H = float(m2.group(2)), float(m2.group(3)), float(m2.group(4))
        if oklch_a_hex(L, C, H).lower() != h.lower():
            descoordinados.append((tok, h, oklch_a_hex(L, C, H)))
    return faltan, descoordinados

# ---------------------------------------------------------------- main
def main() -> int:
    tokens = (RAIZ / "tokens.css").read_text(encoding="utf-8")
    print("Aurora · auditoría de contraste y paridad OKLch")
    print("=" * 58)

    # paridad primero: la auditoria lee hex, deben ser fieles
    faltan, descuadrados = paridad_oklch(tokens)
    if faltan or descuadrados:
        for t in faltan:
            print(f"  PARIDAD  {t}: falta su declaracion oklch() gemela")
        for t, h, r in descuadrados:
            print(f"  PARIDAD  {t}: oklch() no convierte a {h} (da {r})")
        if not ADVISORY:
            print("PARIDAD: FALLA")
            return 1
    else:
        print("PARIDAD: ok — toda declaracion hex lleva su gemela oklch() fiel")

    # base + presets de marca — cascada: tokens base -> tema -> marca
    temas = bloques(tokens)
    presets = sorted((RAIZ / "marcas").glob("*.css"))
    fallos = 0
    for nombre_tema, css_base, css_tema in temas:
        base = declaraciones(css_base)
        tema = dict(base)
        tema.update(declaraciones(css_tema))
        fuentes = [(f"tema {nombre_tema}", tema)]
        for p in presets:
            decl = dict(tema)
            decl.update(declaraciones(p.read_text(encoding="utf-8")))
            fuentes.append((f"tema {nombre_tema} · marca {p.stem}", decl))
        for nombre_fuente, decl in fuentes:
            print(f"\n--- {nombre_fuente} ---")
            for nombre_par, r, colores, minimo, estado in audita_tema(nombre_tema, decl):
                if r is None:
                    print(f"  FALLA {nombre_par}: {estado}")
                    fallos += 1
                    continue
                minimo_txt = f"min {minimo}" if minimo else "informativo"
                print(f"  {estado:5} {nombre_par}: {r:.2f}:1 ({minimo_txt})")
                if estado == "FALLA":
                    fallos += 1

    print()
    if fallos:
        print(f"RESULTADO: {fallos} PAR(ES) POR DEBAJO DEL MINIMO" + ("  (informativo)" if ADVISORY else "  → corregir"))
        return 0 if ADVISORY else 1
    print("RESULTADO: VÁLIDO — todos los pares semánticos en su mínimo WCAG")
    return 0

if __name__ == "__main__":
    sys.exit(main())
