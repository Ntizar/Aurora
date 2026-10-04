# -*- coding: utf-8 -*-
"""Auditoría campo a campo de Aurora (v2).

Cruza objeto por objeto:
  · clases DECLARADAS por cada pack (declaraciones propias, no contextos del shell)
  · clases USADAS en las demos de cada categoría (specs/*.json)
  · objetos FANTASMA (usados y que ningún pack declara)
  · objetos SIN DEMO (declarados y que su categoría nunca muestra)
  · DUPLICADOS reales (la misma clase declarada por 2+ packs)
  · cumplimiento del manifiesto: gradientes, glass, hex, !important, tokens inexistentes
  · familias sin ninguna variante (dónde falta ampliar)

Salida: audit/auditoria.json + audit/AUDITORIA.md
Uso:    python scripts/audit-catalog.py
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from importlib import import_module

bc = import_module("build-catalog")

ROOT = bc.ROOT
PACKS = bc.PACKS
# La capa de cristal puede usar backdrop-filter y gradientes (es su razón de ser).
PACKS_CRISTAL = getattr(bc, "PACKS_CRISTAL", set())
SPECS = bc.SPECS
OUT = ROOT / "audit"

CLASE = bc.CLASE
COMENT_RE = re.compile(r"/\*.*?\*/", re.S)
VAR_DEF_RE = re.compile(r"(--nz-[A-Za-z0-9_-]+)\s*:")
VAR_USE_RE = re.compile(r"var\(\s*(--nz-[A-Za-z0-9_-]+)")
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def limpio(p):
    return COMENT_RE.sub("", p.read_text(encoding="utf-8", errors="replace"))


def reglas_contextuales(txt, clase):
    """¿En cuántas REGLAS aparece la clase? (para distinguir declaración de mera referencia)"""
    n = 0
    for regla in bc.selectores(txt):
        if clase in regla:
            n += 1
    return n


def _txt(f):
    """Lee un fichero y normaliza los fines de línea a LF.

    El informe publica líneas y bytes de cada pack, así que la medida tiene que
    ser idéntica en Windows (CRLF en disco) y en Linux (LF en CI): si no, la
    comparación de «lo generado coincide con lo commiteado» falla siempre.
    """
    return f.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def main():
    tokens_def = set(VAR_DEF_RE.findall(limpio(ROOT / "tokens.css")))
    specs = bc.carga_specs()
    packs, censo_cat, total_clases, total_bases = bc.censo()

    # ---------- packs ----------
    info_pack = {}
    for pack, datos in packs.items():
        f = PACKS / pack
        t = limpio(f)
        info_pack[pack] = {
            "clases": datos["clases"],
            "bases": datos["bases"],
            # OJO: se miden sobre el texto normalizado a LF. Si se usara el tamaño en
            # disco, el informe saldría distinto en Windows (CRLF) que en Linux (LF) y
            # la CI marcaría diferencias falsas en cada push.
            "lineas": _txt(f).count("\n") + 1,
            "bytes": len(_txt(f).encode("utf-8")),
            "hex": HEX_RE.findall(t),
            "gradientes": 0 if pack in PACKS_CRISTAL else len(re.findall(r"\b(?:linear|radial|conic)-gradient\(", t)),
            "glass": 0 if pack in PACKS_CRISTAL else len(re.findall(r"backdrop-filter", t)),
            "important": len(re.findall(r"!important", t)),
            "vars": set(VAR_USE_RE.findall(t)),
        }

    # ---------- duplicados reales ----------
    duplicados = defaultdict(list)
    for pack, d in info_pack.items():
        for c in d["clases"]:
            duplicados[c].append(pack)
    duplicados = {c: v for c, v in duplicados.items() if len(v) > 1}

    # ---------- uso real en demos ----------
    usadas_global = set()
    por_cat = {}
    for s in specs:
        usadas = set()
        for d in s["demos"]:
            usadas |= bc.clases_de_markup(d["markup"])
        usadas_global |= usadas
        declaradas = censo_cat.get(s["cat"], {"clases": set(), "bases": []})
        propias = declaradas["clases"]
        por_cat[s["cat"]] = {
            "nombre": s["nombre"],
            "pack": s["pack"],
            "fichero": s["fichero"],
            "demos": len(s["demos"]),
            "declaradas": propias,
            "bases": declaradas["bases"],
            "usadas": usadas,
            "sin_demo": sorted(c for c in propias if c not in usadas),
            "familias_sin_demo": sorted(b for b in declaradas["bases"]
                                        if not any(u == b or u.startswith(b + "__") or u.startswith(b + "--")
                                                   for u in usadas)),
        }

    # ---------- fantasmas ----------
    todas_declaradas = {c for d in info_pack.values() for c in d["clases"]}
    shell = bc.clases_declaradas(PACKS / bc.PACK_SHELL) if (PACKS / bc.PACK_SHELL).exists() else set()
    registradas = todas_declaradas | shell
    fantasmas = sorted(c for c in usadas_global if c not in registradas)

    # ---------- manifiesto ----------
    tokens_usados = {v for d in info_pack.values() for v in d["vars"]}
    hallazgos = {
        "hex_en_packs": {n: sorted(set(d["hex"])) for n, d in info_pack.items() if d["hex"]},
        "glass_en_packs": {n: d["glass"] for n, d in info_pack.items() if d["glass"]},
        "gradientes_en_packs": {n: d["gradientes"] for n, d in info_pack.items() if d["gradientes"]},
        "important_en_packs": {n: d["important"] for n, d in info_pack.items() if d["important"]},
        "tokens_fantasma": sorted(tokens_usados - tokens_def),
        "duplicados": duplicados,
        "fantasmas": fantasmas,
    }

    # ---------- familias: dónde falta ampliar ----------
    familias = defaultdict(lambda: {"cat": None, "pack": None, "clases": set()})
    for num, s in por_cat.items():
        for c in s["declaradas"]:
            b = bc.base_de(c)
            fam = familias[b]
            fam["cat"] = num
            fam["pack"] = s["pack"]
            fam["clases"].add(c)
    for b, fam in familias.items():
        fam["mods"] = sorted(c.split("--", 1)[1] for c in fam["clases"] if "--" in c[len(b):])
        fam["partes"] = sorted(c.split("__", 1)[1] for c in fam["clases"] if "__" in c)
        fam["demostrado"] = any(u.startswith(b) for u in usadas_global)

    sin_variantes = sorted(b for b, f in familias.items() if not f["mods"])

    resumen = {
        "objetos_declarados": total_clases,
        "familias": total_bases,
        "demos": sum(len(s["demos"]) for s in specs),
        "categorias": len(specs),
        "clases_usadas_en_demos": len(usadas_global),
        "clases_sin_demo": sum(len(s["sin_demo"]) for s in por_cat.values()),
        "familias_sin_demo": sum(len(s["familias_sin_demo"]) for s in por_cat.values()),
        "fantasmas": len(fantasmas),
        "duplicados": len(duplicados),
        "tokens_fantasma": len(hallazgos["tokens_fantasma"]),
        "hex": sum(len(v) for v in hallazgos["hex_en_packs"].values()),
        "glass": sum(hallazgos["glass_en_packs"].values()),
        "gradientes": sum(hallazgos["gradientes_en_packs"].values()),
        "important": sum(hallazgos["important_en_packs"].values()),
        "familias_sin_variantes": len(sin_variantes),
        "packs": len(info_pack),
    }

    OUT.mkdir(exist_ok=True)
    (OUT / "auditoria.json").write_text(json.dumps({
        "resumen": resumen,
        "packs": {n: {"lineas": d["lineas"], "bytes": d["bytes"], "clases": len(d["clases"]),
                      "familias": len(d["bases"]), "hex": len(d["hex"]),
                      "gradientes": d["gradientes"], "glass": d["glass"],
                      "important": d["important"]}
                  for n, d in sorted(info_pack.items())},
        "categorias": {str(k): {"nombre": v["nombre"], "pack": v["pack"], "demos": v["demos"],
                                "objetos": len(v["declaradas"]), "familias": len(v["bases"]),
                                "sin_demo": v["sin_demo"], "familias_sin_demo": v["familias_sin_demo"]}
                       for k, v in sorted(por_cat.items())},
        "hallazgos": hallazgos,
        "familias": {b: {"cat": f["cat"], "pack": f["pack"], "n_clases": len(f["clases"]),
                         "mods": f["mods"], "partes": f["partes"], "demostrado": f["demostrado"]}
                     for b, f in sorted(familias.items())},
        "sin_variantes": sin_variantes,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- informe ----------
    L = []
    A = L.append
    sem = lambda n: "🟢" if n == 0 else "🟡"
    A("# Auditoría campo a campo · Aurora\n")
    A("Generada por `scripts/audit-catalog.py` a partir de los packs CSS y de `specs/*.json`.\n")
    A("## Veredicto\n")
    A("| Comprobación | Valor | |")
    A("|---|---|---|")
    for etiqueta, valor, cero in [
        ("Objetos declarados", resumen["objetos_declarados"], None),
        ("Familias de objeto", resumen["familias"], None),
        ("Demos en vivo", resumen["demos"], None),
        ("Clases usadas en demos", resumen["clases_usadas_en_demos"], None),
        ("Objetos fantasma (usados y no declarados)", resumen["fantasmas"], True),
        ("Clases declaradas sin demo", resumen["clases_sin_demo"], True),
        ("Familias sin demo", resumen["familias_sin_demo"], True),
        ("Duplicados entre packs", resumen["duplicados"], True),
        ("Tokens inexistentes en uso", resumen["tokens_fantasma"], True),
        ("Gradientes fuera del cristal", resumen["gradientes"], True),
        ("Glass fuera del cristal", resumen["glass"], True),
        ("Colores a mano fuera de tokens.css", resumen["hex"], True),
        ("!important", resumen["important"], True),
    ]:
        marca = "" if cero is None else sem(valor)
        A(f"| {etiqueta} | {valor} | {marca} |")
    A(f"\nFamilias sin ninguna variante (`--mod`): **{resumen['familias_sin_variantes']}** de "
      f"{resumen['familias']} — ahí está el margen de ampliación.\n")

    A("## 1. Por pack\n")
    A("| pack | líneas | objetos | familias | hex | grad. | glass | !imp. |")
    A("|---|---|---|---|---|---|---|---|")
    for n, d in sorted(info_pack.items()):
        A(f"| {n} | {d['lineas']} | {len(d['clases'])} | {len(d['bases'])} | {len(d['hex'])} | "
          f"{d['gradientes']} | {d['glass']} | {d['important']} |")
    A("")

    A("## 2. Por categoría\n")
    A("| # | categoría | pack | objetos | familias | demos | sin demo | familias sin demo |")
    A("|---|---|---|---|---|---|---|---|")
    for num, v in sorted(por_cat.items()):
        A(f"| {num:02d} | {v['nombre']} | {v['pack']} | {len(v['declaradas'])} | {len(v['bases'])} | "
          f"{v['demos']} | {len(v['sin_demo'])} | {len(v['familias_sin_demo'])} |")
    A("")

    A("## 3. Objetos fantasma\n")
    A("\n".join(f"- `{c}`" for c in fantasmas) if fantasmas
      else "Ninguno: todo lo que usan las demos existe en algún pack. ✅")
    A("")

    A("## 4. Duplicados entre packs\n")
    A("\n".join(f"- `{c}` → {', '.join(v)}" for c, v in duplicados.items()) if duplicados
      else "Ninguno: cada objeto tiene un único dueño. ✅")
    A("")

    A("## 5. Cumplimiento del manifiesto\n")
    A(f"- Colores a mano fuera de tokens.css: **{resumen['hex']}**")
    for n, v in hallazgos["hex_en_packs"].items():
        A(f"  - {n}: {', '.join(f'`{x}`' for x in v[:16])}")
    A(f"- `backdrop-filter`: **{resumen['glass']}**")
    A(f"- Gradientes: **{resumen['gradientes']}**")
    A(f"- `!important`: **{resumen['important']}**")
    for n, v in hallazgos["important_en_packs"].items():
        A(f"  - {n}: {v}")
    A(f"- Tokens inexistentes: **{resumen['tokens_fantasma']}**")
    if hallazgos["tokens_fantasma"]:
        A("  - " + ", ".join(f"`{t}`" for t in hallazgos["tokens_fantasma"]))
    A("")

    A("## 6. Objetos declarados sin demo (por categoría)\n")
    algo = False
    for num, v in sorted(por_cat.items()):
        if v["sin_demo"]:
            algo = True
            A(f"- **{v['nombre']}** ({len(v['sin_demo'])}): " + ", ".join(f"`{c}`" for c in v["sin_demo"]))
    if not algo:
        A("Ninguno. ✅")
    A("")

    A("## 7. Familias sin variantes (margen de ampliación)\n")
    A(", ".join(f"`{b}`" for b in sin_variantes) if sin_variantes else "Todas tienen variantes. ✅")
    A("")
    (OUT / "AUDITORIA.md").write_text("\n".join(L), encoding="utf-8")

    print("=== VEREDICTO ===")
    for k, v in resumen.items():
        print(f"  {k:<28} {v}")
    print("\nInforme:", OUT / "AUDITORIA.md")


if __name__ == "__main__":
    main()
