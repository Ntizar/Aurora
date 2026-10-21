# -*- coding: utf-8 -*-
"""Plantillas por arquetipo: el esqueleto que el modelo rellena.

Una plantilla es un programa OpenUI **completo y válido** con variables de texto
(`{{titulo}}`, `{{entidad}}`). No es un motor de plantillas con lógica: es el esqueleto
del arquetipo + los datos que cambian. La estructura la decide Aurora, no el modelo.

Uso:
  python3 scripts/plantilla.py --lista
  python3 scripts/plantilla.py --validar-todas          # puerta de CI
  python3 scripts/plantilla.py --index                  # openui/plantillas/index.json
  python3 scripts/plantilla.py panel-operativo --var titulo="Octubre" --salida /tmp/p.openui
  python3 scripts/plantilla.py panel-operativo --salida /tmp/p.openui   # con los defectos
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLANTILLAS = ROOT / "openui" / "plantillas"
VAR_RE = re.compile(r"\{\{(\w+)\}\}")


def cargar_auditor():
    ruta = ROOT / "scripts" / "auditar-openui.py"
    spec = importlib.util.spec_from_file_location("auditar_openui", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cargar_plantillas():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(PLANTILLAS.glob("*.json")) if p.name != "index.json"]


def sustituir(plantilla, valores):
    programa = plantilla["programa"]
    for var in plantilla["variables"]:
        clave = var["nombre"]
        valor = valores.get(clave, var.get("defecto", ""))
        programa = programa.replace("{{%s}}" % clave, str(valor))
    return programa


def validar(programa, fuente, auditor):
    componentes = {c["nombre"]: c for c in fuente["componentes"]}
    try:
        llamadas, _ = auditor.analizar(programa)
    except ValueError as exc:
        return ["no parsea: %s" % exc]
    problemas = []
    if "root" not in llamadas:
        problemas.append("no define root")
    for nombre, expr in llamadas.items():
        if expr.get("k") != "call":
            continue
        comp = componentes.get(expr["nombre"])
        if not comp:
            problemas.append("«%s» no existe en la biblioteca" % expr["nombre"])
            continue
        if len(expr["args"]) > len(comp["props"]):
            problemas.append("%s recibe %d argumentos y admite %d"
                             % (expr["nombre"], len(expr["args"]), len(comp["props"])))
        for i, prop in enumerate(comp["props"][:len(expr["args"])]):
            mal = auditor.tipar(prop, expr["args"][i])
            if mal:
                problemas.append("%s.%s → %s" % (nombre, prop["nombre"], mal))
    restos = VAR_RE.findall(programa)
    if restos:
        problemas.append("variables sin rellenar: %s" % ", ".join(sorted(set(restos))))
    return problemas


def escribir_index(plantillas):
    datos = [
        {
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "marca": p.get("marca", "aurora"),
            "variables": [{"nombre": v["nombre"], "defecto": v.get("defecto", "")} for v in p["variables"]],
            "programa": p["programa"],
        }
        for p in plantillas
    ]
    (PLANTILLAS / "index.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("openui/plantillas/index.json · %d plantillas" % len(datos))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plantilla", nargs="?")
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--validar-todas", action="store_true")
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--var", action="append", default=[], help="clave=valor (repetible)")
    ap.add_argument("--salida", "-o")
    args = ap.parse_args()

    plantillas = cargar_plantillas()
    auditor = cargar_auditor()
    fuente = json.loads((ROOT / "openui" / "componentes.json").read_text(encoding="utf-8"))

    if args.lista:
        for p in plantillas:
            vars_ = ", ".join("%s=%s" % (v["nombre"], v.get("defecto", "")) for v in p["variables"])
            print("%-16s · %s" % (p["nombre"], p["descripcion"]))
            print("%-16s   variables: %s" % ("", vars_))
        return 0

    if args.index:
        escribir_index(plantillas)
        return 0

    if args.validar_todas:
        fallos = 0
        for p in plantillas:
            problemas = validar(sustituir(p, {}), fuente, auditor)
            estado = "OK" if not problemas else "%d problemas" % len(problemas)
            print("%-16s %s" % (p["nombre"], estado))
            for prob in problemas:
                fallos += 1
                print("   ✗", prob)
        print("RESULTADO:", "VÁLIDO" if not fallos else "%d FALLOS" % fallos)
        return 1 if fallos else 0

    if not args.plantilla:
        ap.print_help()
        return 2

    elegida = next((p for p in plantillas if p["nombre"] == args.plantilla), None)
    if not elegida:
        print("No existe la plantilla %r. Disponibles: %s"
              % (args.plantilla, ", ".join(p["nombre"] for p in plantillas)))
        return 1

    valores = {}
    for par in args.var:
        if "=" not in par:
            print("--var espera clave=valor, llegó %r" % par)
            return 2
        k, v = par.split("=", 1)
        valores[k.strip()] = v
    programa = sustituir(elegida, valores)
    problemas = validar(programa, fuente, auditor)
    if problemas:
        print("PLANTILLA NO GENERADA — no valida:")
        for prob in problemas:
            print("  ✗", prob)
        return 1
    if args.salida:
        pathlib.Path(args.salida).write_text(programa + "\n", encoding="utf-8")
        print("escrito %s · %d líneas · marca sugerida %s"
              % (args.salida, len(programa.splitlines()), elegida.get("marca", "aurora")))
        print("siguiente: python3 scripts/programa-a-html.py %s -o <salida.html>" % args.salida)
    else:
        sys.stdout.write(programa + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
