# -*- coding: utf-8 -*-
"""Audita los enlaces locales y el camino de vuelta a la portada.

Nació de un fallo real y visible: `bloques/recetas/index.html` (dos niveles de
profundidad) enlazaba `../tokens.css`, que resuelve a `bloques/tokens.css` — un
fichero que no existe. La página se servía **sin una sola hoja de estilo** y nadie
se enteraba, porque el HTML es válido y los enlaces no se prueban en ninguna
puerta. Además no tenía forma de volver a la portada: había que editar la URL.

Comprueba dos cosas que el resto de la CI no mira:

1. **Todo enlace o recurso local existe.** `href` y `src` relativos se resuelven
   contra el directorio del fichero; si el destino no está en disco, es un fallo.
2. **Toda página sabe volver.** Cualquier HTML que no esté en la raíz debe tener
   al menos un enlace que resuelva a la portada (`index.html` de la raíz). Sin
   eso, el usuario acaba a mano en la barra de direcciones.

Uso:
  python3 scripts/auditar-enlaces.py            # puerta de CI
  python3 scripts/auditar-enlaces.py --lista    # con el detalle de cada fichero
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RE_ENLACE = re.compile(r'(?:href|src)="([^"]+)"')
EXTERNOS = ("http://", "https://", "#", "mailto:", "tel:", "data:", "javascript:", "//")
EXCLUIR = {"node_modules", ".git", "audit", "briefs"}  # briefs/: plantillas, no páginas servidas


def paginas():
    for f in sorted(ROOT.rglob("*.html")):
        partes = set(f.relative_to(ROOT).parts[:-1])
        if partes & EXCLUIR:
            continue
        if f.name.startswith("_"):  # artefactos de horneado
            continue
        yield f


def sin_codigo(texto):
    """Fuera los bloques de código: dentro van ejemplos escapados, no enlaces."""
    return re.sub(r"<(pre|code)\b.*?</\1>", "", texto, flags=re.S | re.I)


def locales(texto):
    for u in RE_ENLACE.findall(sin_codigo(texto)):
        if u.startswith(EXTERNOS):
            continue
        base = u.split("#")[0].split("?")[0]
        if base:
            yield u, base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", action="store_true", help="imprime el detalle fichero a fichero")
    args = ap.parse_args()

    portada = (ROOT / "index.html").resolve()
    rotos, sin_vuelta = [], []
    comprobados = 0

    for f in paginas():
        rel = f.relative_to(ROOT).as_posix()
        texto = f.read_text(encoding="utf-8", errors="replace")
        destinos = []
        for original, base in locales(texto):
            destino = (f.parent / base).resolve()
            destinos.append(destino)
            comprobados += 1
            if not destino.exists():
                rotos.append((rel, original))
        # Camino de vuelta: la página cuelga de una carpeta y no ofrece la portada.
        if f.resolve() != portada and portada not in destinos:
            sin_vuelta.append(rel)

    print("Aurora · enlaces y navegación")
    print("  páginas revisadas   %d" % len(list(paginas())))
    print("  enlaces locales     %d" % comprobados)
    print("  enlaces rotos       %d" % len(rotos))
    print("  sin vuelta a inicio %d" % len(sin_vuelta))

    if args.lista or rotos or sin_vuelta:
        for rel, u in rotos[:40]:
            print("  ✗ %-42s → %s" % (rel, u))
        for rel in sin_vuelta[:40]:
            print("  ! %-42s sin enlace a la portada" % rel)

    if rotos or sin_vuelta:
        print("\nRESULTADO: CON FALLOS — %d enlaces rotos, %d páginas sin vuelta"
              % (len(rotos), len(sin_vuelta)))
        return 1
    print("\nRESULTADO: VÁLIDO — todos los enlaces resuelven y todas las páginas vuelven ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
