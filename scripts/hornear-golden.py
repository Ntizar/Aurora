#!/usr/bin/env python3
"""Hornea las páginas de producto examples/golden/ desde sus fuentes .openui.

ÚNICA definición del horneado golden: la ejecutan tanto quien trabaja en local
como la CI (`git diff --quiet -- examples/golden` tras correr este script), así
que el HTML commiteado y el generado no pueden desviarse (E0: artefactos desde
sus fuentes, una sola fuente).

Uso:
  python scripts/hornear-golden.py            # reescribe las golden
  python scripts/hornear-golden.py --check    # solo avisa si están desfasadas
"""
import argparse
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGINAS = [
    ("examples/golden/landing.openui", "examples/golden/index.html",
     "Ntizar · Encargos — tablero de encargos de cliente"),
    ("examples/golden/detalle.openui", "examples/golden/detalle.html",
     "EN-2291 · Ficha de encargo — Ntizar"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="no escribe: compara con lo commiteado y sale en rojo si difiere")
    ns = ap.parse_args()

    fallos = 0
    for programa, salida, titulo in PAGINAS:
        destino = ROOT / salida
        previo = destino.read_text(encoding="utf-8") if ns.check and destino.exists() else None
        if ns.check:
            fd, out_salida = tempfile.mkstemp(suffix=".html")
            os.close(fd)  # Windows: sin descriptor abierto no hay PermissionError al borrar
        else:
            out_salida = str(destino)
        cmd = [sys.executable, str(ROOT / "scripts/hornear.py"), str(ROOT / programa),
               "--salida", out_salida, "--modo", "producto", "--inicio", "index.html",
               "--marca", "ntizar", "--base", "../../", "--titulo", titulo]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(r.stdout + r.stderr)
            sys.exit(1)
        if ns.check:
            nuevo = pathlib.Path(out_salida).read_text(encoding="utf-8")
            pathlib.Path(out_salida).unlink(missing_ok=True)
            if previo is None:
                print("✗ %s no existe: ejecuta scripts/hornear-golden.py" % salida)
                fallos += 1
            elif previo != nuevo:
                print("✗ %s está desfasado de su .openui: ejecuta scripts/hornear-golden.py" % salida)
                fallos += 1
            else:
                print("✓ %s al día con su fuente" % salida)
        else:
            print("horneado %s" % salida)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
