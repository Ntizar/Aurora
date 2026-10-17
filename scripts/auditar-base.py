#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita datos/base-diseno.json — la base de datos de diseño de Aurora.

Comprueba que el índice no miente:
  · que todo fichero referenciado existe (demos, páginas, recetas, combos, marcas, packs)
  · que cada familia tiene pack, demo, markup y frase de uso
  · que los tokens tienen nombre y valor
  · que no hay rutas absolutas ni escapes del repo
  · con --check, que el JSON del disco coincide con el que produce el generador

Uso:
  python3 scripts/auditar-base.py
  python3 scripts/auditar-base.py --check
  python3 scripts/auditar-base.py --min-familias 409 --min-tokens 189
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "datos" / "base-diseno.json"


def cargar_generador():
    ruta = ROOT / "scripts" / "generar-base-datos.py"
    spec = importlib.util.spec_from_file_location("generar_base_datos", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def existe(rel: str, fallos: list[str], campo: str) -> None:
    if not rel:
        fallos.append(f"{campo}: ruta vacía")
        return
    if rel.startswith("/") or ".." in Path(rel).parts:
        fallos.append(f"{campo}: ruta no relativa al repo → {rel}")
        return
    if not (ROOT / rel).is_file():
        fallos.append(f"{campo}: no existe → {rel}")


def auditar(min_familias: int, min_tokens: int) -> list[str]:
    fallos: list[str] = []
    if not BASE.is_file():
        return ["falta datos/base-diseno.json"]

    try:
        d = json.loads(BASE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"]

    for clave in ("resumen", "principios", "categorias", "familias", "tokens", "recetas", "combos", "marcas"):
        if clave not in d:
            fallos.append(f"falta la clave {clave}")

    familias = d.get("familias", [])
    tokens = d.get("tokens", [])
    if len(familias) < min_familias:
        fallos.append(f"familias: {len(familias)} < mínimo {min_familias}")
    if len(tokens) < min_tokens:
        fallos.append(f"tokens: {len(tokens)} < mínimo {min_tokens}")

    ids = set()
    for f in familias:
        fid = f.get("id", "")
        if not fid:
            fallos.append("familia sin id")
            continue
        if fid in ids:
            fallos.append(f"familia duplicada: {fid}")
        ids.add(fid)
        for campo in ("pack", "demo", "markup", "cuandoUsar"):
            if not f.get(campo):
                fallos.append(f"{fid}: sin {campo}")
        if f.get("pack"):
            existe(f"packs/{f['pack']}", fallos, fid)
        if f.get("demo"):
            existe(f["demo"], fallos, fid)

    for c in d.get("categorias", []):
        if c.get("pack"):
            existe(f"packs/{c['pack']}", fallos, f"categoría {c.get('id')}")
        if c.get("pagina"):
            existe(c["pagina"], fallos, f"categoría {c.get('id')}")
        if not c.get("cuandoUsar"):
            fallos.append(f"categoría {c.get('id')}: sin cuandoUsar")

    for grupo in ("recetas", "ejemplos"):
        for r in d.get(grupo, []):
            existe(r.get("fichero", ""), fallos, f"{grupo}/{r.get('id')}")
            if not r.get("packs"):
                fallos.append(f"{grupo}/{r.get('id')}: sin packs")

    for c in d.get("combos", []):
        existe(c.get("fichero", ""), fallos, f"combo/{c.get('id')}")
        if not c.get("packs"):
            fallos.append(f"combo/{c.get('id')}: sin packs")

    for m in d.get("marcas", []):
        existe(m.get("fichero", ""), fallos, f"marca/{m.get('id')}")

    for t in tokens:
        if not t.get("nombre", "").startswith("--nz-"):
            fallos.append(f"token sin nombre --nz-*: {t.get('nombre')!r}")
        if not t.get("valor"):
            fallos.append(f"token sin valor: {t.get('nombre')}")

    if len(d.get("principios", [])) < 12:
        fallos.append(f"principios: {len(d.get('principios', []))} < 12")
    if not d.get("alias"):
        fallos.append("alias vacío")

    # Los conteos del resumen no pueden contradecir a las listas.
    r = d.get("resumen", {})
    for clave, lista in (("familias", familias), ("tokens", tokens)):
        if r.get(clave) != len(lista):
            fallos.append(f"resumen.{clave}={r.get(clave)} no cuadra con {len(lista)}")

    return fallos


def comparar_generado() -> list[str]:
    gen = cargar_generador()
    esperado = gen.serializar(gen.construir())
    actual = BASE.read_text(encoding="utf-8") if BASE.is_file() else ""
    if actual != esperado:
        return ["datos/base-diseno.json desincronizado: regenera con scripts/generar-base-datos.py"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Audita la base de datos de diseño de Aurora")
    ap.add_argument("--check", action="store_true", help="comprueba también que el JSON está sincronizado")
    ap.add_argument("--min-familias", type=int, default=0)
    ap.add_argument("--min-tokens", type=int, default=0)
    args = ap.parse_args()

    fallos = auditar(args.min_familias, args.min_tokens)
    if args.check and not fallos:
        fallos += comparar_generado()

    if fallos:
        print("AUDITORÍA DE LA BASE DE DATOS: FALLOS")
        for f in fallos:
            print(f"  ✗ {f}")
        return 1

    d = json.loads(BASE.read_text(encoding="utf-8"))
    r = d["resumen"]
    print(
        f"BASE DE DATOS VÁLIDA · {r['familias']} familias · {r['clases']} clases · "
        f"{r['tokens']} tokens · {r['recetas']} recetas · {r['ejemplos']} ejemplos · "
        f"{r['combos']} combos · {r['marcas']} marcas · {r['principios']} principios"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
