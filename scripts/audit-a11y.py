#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auditoría de accesibilidad de las demos de Aurora.

Revisa el markup real de los 15 specs (lo que el visitante ve y puede tocar) con
un parser de verdad, contando el texto que cuelga de cada elemento:

  1. <img> sin alt.
  2. <input>/<select>/<textarea> sin etiqueta asociada (label envolvente,
     label[for], aria-label, aria-labelledby o title).
  3. controles con atributo `hidden` → no son focusables ni operables con teclado
     (el patrón sin-JS debe usar la clase .nz-vh).
  4. <button> o <a href> sin texto accesible ni aria-label.
  5. <a> sin href ni role.
  6. referencias aria-* a ids que no existen.
  7. label[for] que apunta a un control inexistente.
  8. tabindex mayor que 0.
  9. ids duplicados dentro de la misma página.

Uso:  python scripts/audit-a11y.py      (exit 1 si hay fallos)
"""
from __future__ import annotations

import json
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
CONTROLES = {"input", "select", "textarea"}
VOID = {"img", "input", "br", "hr", "meta", "link", "source", "area", "col", "kbd"}


class Demo(HTMLParser):
    """Recoge lo que necesita el auditor de una demo."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.abiertos = []       # [{tag, attrs, texto, en_label}]
        self.ids = []
        self.refs = []           # (atributo, id, etiqueta)
        self.fors = []           # ids referenciados por label[for]
        self.controles = []      # (tag, attrs, en_label)
        self.accionables = []    # (tag, attrs, texto, en_label)
        self.imgs_sin_alt = 0
        self.tabindex = []
        self._dl = 0

    # ---------- parser ----------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "label":
            self._dl += 1
        if a.get("id"):
            self.ids.append(a["id"])
        if a.get("for"):
            self.fors.append(a["for"])
        for ref in ("aria-labelledby", "aria-describedby", "aria-controls"):
            for i in a.get(ref, "").split():
                self.refs.append((ref, i, tag))
        if "tabindex" in a:
            try:
                if int(a["tabindex"]) > 0:
                    self.tabindex.append((tag, a["tabindex"]))
            except ValueError:
                pass

        if tag == "img" and "alt" not in a and "aria-hidden" not in a:
            self.imgs_sin_alt += 1
        if tag in CONTROLES:
            self.controles.append((tag, a, self._dl > 0))
        self.abiertos.append({"tag": tag, "a": a, "texto": "", "en_label": self._dl > 0})

    def handle_data(self, data):
        if data.strip():
            for n in self.abiertos:
                n["texto"] += data.strip() + " "

    def handle_endtag(self, tag):
        if tag == "label" and self._dl:
            self._dl -= 1
        for i in range(len(self.abiertos) - 1, -1, -1):
            n = self.abiertos[i]
            if n["tag"] == tag:
                self.abiertos.pop(i)
                if tag in ("button", "a"):
                    self.accionables.append((tag, n["a"], n["texto"].strip(), n["en_label"]))
                break

    def cerrar(self):
        """Elementos que quedaron abiertos (markup sin cerrar)."""
        for n in self.abiertos:
            if n["tag"] in ("button", "a"):
                self.accionables.append((n["tag"], n["a"], n["texto"].strip(), n["en_label"]))


def revisa(markup: str):
    p = Demo()
    p.feed(markup)
    p.cerrar()
    problemas = []

    if p.imgs_sin_alt:
        problemas.append(f"{p.imgs_sin_alt} <img> sin alt")
    for tag, a, en_label in p.controles:
        if a.get("type") == "hidden":
            continue
        if "hidden" in a:
            problemas.append(f"<{tag}> usa el atributo hidden: no se puede enfocar ni operar con teclado (usa la clase .nz-vh)")
            continue
        etiquetado = (
            en_label
            or any(k in a for k in ("aria-label", "aria-labelledby", "title"))
            or (a.get("id") and a["id"] in p.fors)
        )
        if not etiquetado:
            problemas.append(f"<{tag}> sin etiqueta asociada")
    for tag, a, texto, en_label in p.accionables:
        tiene_texto = bool(texto) or bool(a.get("aria-label") or a.get("title"))
        if tag == "a" and "href" not in a and "role" not in a:
            problemas.append("<a> sin href ni role")
            continue
        if not tiene_texto:
            problemas.append(f"<{tag}> sin texto accesible")
    for ref, i, tag in p.refs:
        if i not in p.ids:
            problemas.append(f'{ref}="{i}" apunta a un id que no existe')
    for f in p.fors:
        if f not in p.ids:
            problemas.append(f'label[for="{f}"] apunta a un control que no existe')
    for tag, v in p.tabindex:
        problemas.append(f"tabindex={v} (>0 rompe el orden natural de tabulación)")
    return problemas, p.ids


def main() -> int:
    total = 0
    print("Aurora · auditoría de accesibilidad de las demos\n")
    for spec_f in sorted(SPECS.glob("*.json")):
        spec = json.loads(spec_f.read_text(encoding="utf-8"))
        problemas = []
        vistos = {}
        for d in spec["demos"]:
            fallos, ids = revisa(d["markup"])
            for f in fallos:
                problemas.append(f"{d['titulo']}: {f}")
            for i in ids:
                if i in vistos:
                    problemas.append(f"{d['titulo']}: id duplicado en la página: {i}")
                vistos[i] = True
        if problemas:
            total += len(problemas)
            print(f"{spec_f.name} ({spec['nombre']}): {len(problemas)} problemas")
            unicos = []
            for x in problemas:
                if x not in unicos:
                    unicos.append(x)
            for x in unicos[:40]:
                veces = problemas.count(x)
                print(f"    ✗ {x}" + (f"   (x{veces})" if veces > 1 else ""))
    print(f"\nTOTAL: {total} problemas de accesibilidad")
    if total:
        print("RESULTADO: NO VÁLIDO")
        return 1
    print("RESULTADO: VÁLIDO — demos etiquetadas, operables con teclado y navegables ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
