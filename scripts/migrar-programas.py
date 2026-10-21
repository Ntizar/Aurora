# -*- coding: utf-8 -*-
"""Migra programas OpenUI cuando Aurora rompe contrato (major).

Qué puede hacer solo:
  · renombrar componentes   `Tarjeta(` → `Panel(`
  · quitar componentes      avisa y comenta la línea (no la borra a ciegas)

Qué NO puede hacer solo (y por qué):
  · renombrar props. Los argumentos de OpenUI Lang son **posicionales**: cambiar el
    nombre de una prop no cambia su sitio, pero si cambia el orden hay que reescribir la
    llamada con los datos delante. El migrador la marca como manual con la línea exacta.

Un programa migrado se valida con el mismo analizador que usa `auditar-openui.py`:
si no pasa, no se escribe nada.

Formato de la migración (`openui/migraciones/<major>.json`):
{
  "de": "1.0.0", "a": "2.0.0",
  "componentes": [{"de": "Tarjeta", "a": "Panel"}],
  "eliminados": ["Gauge"],
  "props_manual": [{"componente": "Kpi", "de": "etiqueta", "a": "titulo"}],
  "notas": "por qué rompe"
}

Uso:
  python3 scripts/migrar-programas.py --migracion openui/migraciones/2.0.json prog.openui
  python3 scripts/migrar-programas.py --migracion m.json prog.openui --en-sitio
  python3 scripts/migrar-programas.py --migracion m.json prog.openui --dry-run
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def cargar_auditor():
    ruta = ROOT / "scripts" / "auditar-openui.py"
    spec = importlib.util.spec_from_file_location("auditar_openui", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validar(programa, fuente, auditor):
    """Devuelve la lista de problemas del programa (vacía = válido)."""
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
        for i, prop in enumerate(comp["props"][:len(expr["args"])]):
            mal = auditor.tipar(prop, expr["args"][i])
            if mal:
                problemas.append("%s.%s → %s" % (nombre, prop["nombre"], mal))
    return problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programa")
    ap.add_argument("--migracion", required=True)
    ap.add_argument("--en-sitio", action="store_true", help="escribe el programa migrado")
    ap.add_argument("--dry-run", action="store_true", help="no escribe, solo cuenta")
    ap.add_argument("--salida", "-o")
    args = ap.parse_args()

    auditor = cargar_auditor()
    fuente = json.loads((ROOT / "openui" / "componentes.json").read_text(encoding="utf-8"))
    mig = json.loads(pathlib.Path(args.migracion).read_text(encoding="utf-8"))
    ruta = pathlib.Path(args.programa)
    original = ruta.read_text(encoding="utf-8")

    antes = validar(original, fuente, auditor)
    nuevo = original
    cambios = []

    for cambio in mig.get("componentes", []):
        patron = re.compile(r"\b%s\(" % re.escape(cambio["de"]))
        nuevo, n = patron.subn("%s(" % cambio["a"], nuevo)
        if n:
            cambios.append("%s → %s (%d llamadas)" % (cambio["de"], cambio["a"], n))

    avisos = []
    for nombre in mig.get("eliminados", []):
        patron = re.compile(r"\b%s\(" % re.escape(nombre))
        if patron.search(nuevo):
            avisos.append("«%s» ya no existe: reescribe esa parte a mano (o quita el bloque)" % nombre)
    for prop in mig.get("props_manual", []):
        patron = re.compile(r"\b%s\(" % re.escape(prop["componente"]))
        if patron.search(nuevo):
            avisos.append("%s: la prop «%s» pasa a «%s» y los argumentos son posicionales → revisa el orden"
                          % (prop["componente"], prop["de"], prop["a"]))

    despues = validar(nuevo, fuente, auditor)
    if despues:
        print("MIGRACIÓN NO APLICADA — el programa migrado no valida:")
        for p in despues:
            print("  ✗", p)
        return 1

    if cambios:
        for c in cambios:
            print("  ·", c)
    else:
        print("  · sin cambios automáticos")
    for a in avisos:
        print("  ! ", a)
    if antes:
        print("  · el programa original ya tenía %d problema(s); ahora valida" % len(antes))

    if args.dry_run:
        print("DRY-RUN: no se ha escrito nada")
        return 0

    destino = None
    if args.en_sitio:
        destino = ruta
    elif args.salida:
        destino = pathlib.Path(args.salida)
    if destino:
        destino.write_text(nuevo, encoding="utf-8")
        print("escrito", destino)
    else:
        sys.stdout.write(nuevo)
    print("RESULTADO: MIGRADO a spec %s" % mig.get("a", "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
