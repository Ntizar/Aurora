#!/usr/bin/env python3
"""Audita el MOVIMIENTO de los packs de Aurora — la pieza que el lint no ve.

El manifiesto (validar-css.py) cazó siempre gradientes, glass, colores y pesos.
El movimiento no tenía juez: duraciones a mano, curvas a mano y animaciones con
`forwards` sin salida de emergencia entraban en silencio. Esto es su puerta.

Qué comprueba:
  1. DURACIONES  — toda duración de transition/animation sale de un token
     (--nz-dur-* / --nz-mov-vida) o es un fallback junto al token. Bucles
     `infinite` exentos: la cadencia de un spinner es dato, no cromo.
  2. CURVAS      — cero cubic-bezier a mano en los packs: la curva es un
     token (--nz-ease-*). Definirla en un pack es escribirla dos veces.
  3. TECHO       — ninguna animación de entrada/salida sobrepasa --nz-mov-max
     (400ms) sin token de vida (--nz-mov-vida) ni exención por nombre.
  4. EMERGENCIA  — toda animación con `forwards` (deja estado permanente)
     lleva bloque `prefers-reduced-motion` propio en el pack: el congelador
     global acorta la duración, no anula la huella del fill.

Exención por línea: un comentario «movimiento: exento» en la línea del código.

Uso:
  python3 scripts/auditar-movimiento.py              # juez normal
  python3 scripts/auditar-movimiento.py --selftest   # arnés con CSS saboteado
  python3 scripts/auditar-movimiento.py --json
"""
import argparse
import json
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"

# Animaciones exentas por diseño (el shell del catálogo y la vida del toast):
EXENTAS = ("catIn", "nzToastVida")

RX_DURACION = re.compile(
    r"(?:transition|animation)(?:-duration)?\s*:[^;{}]*?([0-9]+(?:\.[0-9]+)?)(ms|s)\b"
)
RX_MEDIA_REDUCED = re.compile(r"@media[^{]*prefers-reduced-motion[^{]*\{")
RX_TOKEN_DUR = re.compile(r"--nz-dur-[a-z-]+|--nz-mov-vida")
RX_CURVA = re.compile(r"cubic-bezier\([^)]*\)")
RX_KEYFRAMES = re.compile(r"@keyframes\s+([A-Za-z0-9_-]+)")
RX_REDUCED = re.compile(r"prefers-reduced-motion")
RX_ANIM_USO = re.compile(r"animation\s*:[^;{}]*")
RX_INFINITE = re.compile(r"infinite")
RX_FORWARDS = re.compile(r"forwards")
RX_MS_S = re.compile(r"([0-9]+(?:\.[0-9]+)?)(ms|s)\b")


def ms(valor, unidad):
    return float(valor) * (1 if unidad == "ms" else 1000)


def rangos_reduced(limpio):
    """Rangos de bloque @media prefers-reduced-motion (apertura simple y anidada)."""
    rangos = []
    for m in RX_MEDIA_REDUCED.finditer(limpio):
        ini, prof, i = m.end() - 1, 0, m.end() - 1
        while i < len(limpio) and (prof > 0 or i == m.end() - 1):
            if limpio[i] == "{":
                prof += 1
            elif limpio[i] == "}":
                prof -= 1
                if prof == 0:
                    break
            i += 1
        rangos.append((ini, i + 1))
    return rangos


def auditar_pack(ruta):
    crudo = ruta.read_text(encoding="utf-8")
    limpio = re.sub(r"/\*.*?\*/", "", crudo, flags=re.S)
    reduced = rangos_reduced(limpio)
    exentas = {
        i + 1 for i, l in enumerate(crudo.splitlines()) if "movimiento: exento" in l
    }

    def en_reduced(pos):
        return any(a <= pos < b for a, b in reduced)

    fallos, avisos = [], []
    nombre = ruta.name

    def linea_de(pos):
        return limpio[:pos].count("\n") + 1

    # ---- 1. duraciones literales fuera de token ----
    for m in RX_DURACION.finditer(limpio):
        if en_reduced(m.start()):
            continue  # dentro de prefers-reduced-motion: es la salida de emergencia
        ini = max(limpio.rfind(";", 0, m.start()), limpio.rfind("{", 0, m.start())) + 1
        fin = next(
            (p for p in (limpio.find(";", m.start()), limpio.find("}", m.start())) if p != -1),
            m.end(),
        )
        declaracion = limpio[ini:fin]
        linea = linea_de(m.start())
        if RX_TOKEN_DUR.search(declaracion):
            continue  # el literal es fallback del token
        if RX_INFINITE.search(declaracion):
            continue  # cadencia de un bucle: dato, no cromo
        if any(e in declaracion for e in EXENTAS):
            continue
        if linea in exentas:
            continue
        avisos.append(
            f"{nombre}:{linea}: duración literal «{m.group(1)}{m.group(2)}» fuera de "
            f"token — usa --nz-dur-* o comenta «movimiento: exento» en la línea"
        )

    # ---- 2. curvas a mano ----
    for m in RX_CURVA.finditer(limpio):
        linea = linea_de(m.start())
        if linea in exentas:
            continue
        fallos.append(
            f"{nombre}:{linea}: cubic-bezier a mano — la curva es un token (--nz-ease-*)"
        )

    # ---- 3. techo de --nz-mov-max en entradas/salidas ----
    for m in RX_ANIM_USO.finditer(limpio):
        frag = m.group(0)
        linea = linea_de(m.start())
        if RX_INFINITE.search(frag) or RX_TOKEN_DUR.search(frag):
            continue
        if any(e in frag for e in EXENTAS) or linea in exentas:
            continue
        d = RX_MS_S.search(frag)
        if d and ms(d.group(1), d.group(2)) > 400:
            fallos.append(
                f"{nombre}:{linea}: animación de {d.group(1)}{d.group(2)} sobrepasa "
                f"--nz-mov-max (400ms) sin token de vida"
            )

    # ---- 4. `forwards` sin salida de emergencia ----
    usa_forwards = any(RX_FORWARDS.search(m.group(0)) for m in RX_ANIM_USO.finditer(limpio))
    if usa_forwards and not RX_REDUCED.search(limpio):
        avisos.append(
            f"{nombre}: usa animación con forwards (huella permanente) sin bloque "
            f"prefers-reduced-motion propio — el congelador global acorta la duración, "
            f"no anula el fill: decláralo"
        )

    return fallos, avisos


def selftest():
    """Arnés: el CSS saboteado canta los 4 grupos; el bueno calla entero."""
    malo = (
        "/* p99-fantasma.css */\n"
        ".nz-demo { transition: opacity 250ms; }\n"
        ".nz-demo2 { animation: nzDemoEntra .9s cubic-bezier(0.34, 1.56, 0.64, 1); }\n"
        "@keyframes nzDemoEntra { from { opacity: 0; } }\n"
        ".nz-demo4 { animation: nzDemoFuera .2s forwards; }\n"
        "@keyframes nzDemoFuera { to { opacity: 0; } }\n"
    )
    bueno = (
        "/* p98-bueno.css */\n"
        ".nz-ok { transition: opacity var(--nz-dur-base) var(--nz-ease-out); }\n"
        ".nz-ok2 { animation: nzSpin .7s linear infinite; }\n"
        ".nz-ok3 { animation: nzOkEntra var(--nz-dur-entrada) var(--nz-ease-out); }\n"
        "@keyframes nzOkEntra { from { opacity: 0.55; } }\n"
        ".nz-ok4 { animation: nzOkFuera var(--nz-dur-salida) forwards; }\n"
        "@keyframes nzOkFuera { to { opacity: 0; } }\n"
        "@media (prefers-reduced-motion: reduce) { .nz-ok4 { animation: none; } }\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / "p99-fantasma.css").write_text(malo, encoding="utf-8")
        (d / "p98-bueno.css").write_text(bueno, encoding="utf-8")
        fl_malo, av_malo = auditar_pack(d / "p99-fantasma.css")
        fl_bueno, av_bueno = auditar_pack(d / "p98-bueno.css")

    texto_malo = "\n".join(fl_malo + av_malo)
    ok = True
    if fl_bueno or av_bueno:
        ok = False
        print("SELFTEST FALSO POSITIVO en el CSS bueno:")
        print("  fallos:", fl_bueno)
        print("  avisos:", av_bueno)
    for esperado, etiqueta in [
        ("duración literal", "duraciones"),
        ("cubic-bezier", "curvas"),
        ("sobrepasa", "techo"),
        ("forwards", "emergencia"),
    ]:
        if esperado not in texto_malo:
            ok = False
            print(f"SELFTEST INCOMPLETO — el saboteado no cantó {etiqueta}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        if selftest():
            print("SELFTEST: VÁLIDO — el juez canta el CSS saboteado y calla el bueno ✅")
            return 0
        print("SELFTEST: NO VÁLIDO")
        return 1

    fallos, avisos = [], []
    packs = sorted(PACKS.glob("p*.css"))
    if not packs:
        print("NO HAY PACKS — algo va mal")
        return 1
    for f in packs:
        fl, av = auditar_pack(f)
        fallos.extend(fl)
        avisos.extend(av)

    if args.json:
        print(json.dumps({"fallos": fallos, "avisos": avisos}, ensure_ascii=False, indent=1))
    else:
        for a in avisos:
            print("AVISO:", a)
        for f in fallos:
            print("FALLO:", f)

    if fallos:
        print(f"\nMOVIMIENTO: NO VÁLIDO — {len(fallos)} fallo(s), {len(avisos)} aviso(s)")
        return 1
    print(f"\nMOVIMIENTO VÁLIDO — 0 fallos, {len(avisos)} aviso(s) ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
