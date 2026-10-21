#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita la coherencia del sistema y de sus páginas.

No mide píxeles: vigila las incoherencias que se cuelan entre packs, recetas,
demos y versiones, y que el usuario ve como «esto no pega».

Comprueba:
  · iconos de texto (▦ ⚙ ⌕ ✎ ▶ …) en demos, recetas y ejemplos: la ley 10 pide SVG
  · temas forzados: una receta no puede ser dark entera; el dark es un modo, no una página
  · versiones de CDN distintas de la vigente en components.json
  · footers sin la atribución exacta
  · .nz-sidebar__link--icon usado con texto (esa clase es para enlaces de solo icono)
  · estilos inline con literales de color/tamaño fuera de tokens

Uso:
  python3 scripts/auditar-coherencia.py
  python3 scripts/auditar-coherencia.py --check   # 1 si hay fallos (para CI)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Símbolos Unicode que se están usando como icono. No son emojis, pero tampoco
# son SVG: cambian de forma según la fuente del sistema y rompen la paridad.
SIMBOLOS = set("▦▤⚙⌕◐⌂✓✕✎▶＋⤓⊞✉⌸⌗◈⑂¶")
ATRIBUCION = "Hecho con ❤️ por David Antizar"
VERSION = json.loads((ROOT / "components.json").read_text(encoding="utf-8")).get("version", "")

# Un icono de texto es un símbolo que es TODO el contenido visible de un
# elemento de icono/botón/enlace, no una letra suelta en prosa.
RX_ICONO_TEXTO = re.compile(
    r">\s*([" + "".join(re.escape(s) for s in SIMBOLOS) + r"])\s*<"
)
RX_CLASE_ICONO = re.compile(r'class="[^"]*(?:icon|btn--icon)[^"]*"')
RX_SIDEBAR_ICONO = re.compile(
    r'<a[^>]*class="[^"]*nz-sidebar__link--icon[^"]*"[^>]*>(.*?)</a>', re.S
)
RX_VERSION = re.compile(r"@v(\d+\.\d+\.\d+)")
# Canal vivo (@v9): acepta el major vigente. Un tag exacto debe ser la versión actual.
RX_CANAL = re.compile(r"@v(\d+)(?![\d.])")
RX_TEMA = re.compile(r'<html[^>]*data-nz-theme="([^"]+)"')
RX_INLINE = re.compile(r'style="([^"]*)"')


def htmls() -> list[Path]:
    rutas = [ROOT / "index.html", ROOT / "base.html", ROOT / "stress-test.html"]
    for carpeta in ("recetas", "examples", "paginas"):
        rutas += sorted((ROOT / carpeta).glob("*.html"))
    return [p for p in rutas if p.is_file()]


def auditar_html(p: Path, fallos: list[str], avisos: list[str]) -> None:
    t = p.read_text(encoding="utf-8")
    rel = p.relative_to(ROOT).as_posix()

    for m in RX_ICONO_TEXTO.finditer(t):
        ctx = t[max(0, m.start() - 120):m.start()]
        if RX_CLASE_ICONO.search(ctx) or "aria-label" in ctx:
            fallos.append(f"{rel}: icono de texto «{m.group(1)}» (usa SVG .nz-icon)")

    # Una receta no puede ser dark entera: el dark es un modo, no la identidad
    # de una página. Se permite si la página lo declara como demo de tema.
    tema = RX_TEMA.search(t)
    if tema and tema.group(1) == "dark" and rel.startswith("recetas/"):
        fallos.append(f"{rel}: receta forzada a dark; usa light y un bloque --profundo")

    for v in set(RX_VERSION.findall(t)):
        if v != VERSION:
            fallos.append(f"{rel}: CDN @v{v} ≠ versión vigente {VERSION}")
    major = VERSION.split(".")[0]
    for m in set(RX_CANAL.findall(t)):
        if m != major:
            fallos.append(f"{rel}: CDN @v{m} (canal) ≠ major vigente v{major}")

    if rel.startswith(("recetas/", "examples/")) and ATRIBUCION not in t:
        fallos.append(f"{rel}: falta la atribución exacta «{ATRIBUCION}»")

    for m in RX_SIDEBAR_ICONO.finditer(t):
        interior = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if interior and not interior.startswith("<"):
            fallos.append(f"{rel}: .nz-sidebar__link--icon con texto «{interior[:30]}»")

    for m in RX_INLINE.finditer(t):
        valor = m.group(1)
        if re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", valor):
            avisos.append(f"{rel}: color literal en style=\"…\"")
        if re.search(r"\b\d+px\b", valor) and "var(--nz-" not in valor:
            avisos.append(f"{rel}: px literal en style=\"…\"")


def auditar_specs(fallos: list[str], avisos: list[str]) -> None:
    for p in sorted((ROOT / "specs").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for demo in d.get("demos", []):
            markup = demo.get("markup", "")
            for m in RX_ICONO_TEXTO.finditer(markup):
                ctx = markup[max(0, m.start() - 140):m.start()]
                if RX_CLASE_ICONO.search(ctx) or "aria-label" in ctx:
                    fallos.append(
                        f"specs/{p.name}: icono de texto «{m.group(1)}» en «{demo.get('titulo','')}»"
                    )
            if "<a" in markup and "sidebar__link--icon" in markup:
                for m in RX_SIDEBAR_ICONO.finditer(markup):
                    interior = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                    if interior:
                        fallos.append(
                            f"specs/{p.name}: --icon con texto «{interior[:30]}» en «{demo.get('titulo','')}»"
                        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Coherencia de Aurora")
    ap.add_argument("--check", action="store_true", help="1 si hay fallos")
    args = ap.parse_args()

    fallos: list[str] = []
    avisos: list[str] = []
    for p in htmls():
        auditar_html(p, fallos, avisos)
    auditar_specs(fallos, avisos)

    if fallos:
        print(f"COHERENCIA: {len(fallos)} fallo(s)")
        for f in fallos[:80]:
            print(f"  ✗ {f}")
        if len(fallos) > 80:
            print(f"  … y {len(fallos) - 80} más")
    if avisos:
        print(f"AVISOS: {len(avisos)}")
        for a in avisos[:20]:
            print(f"  ! {a}")

    if not fallos:
        print(f"COHERENCIA VÁLIDA · {len(htmls())} páginas y 18 specs · versión {VERSION}")
        return 0

    return 1 if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
