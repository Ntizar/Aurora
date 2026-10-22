# -*- coding: utf-8 -*-
"""De un programa OpenUI a una página Aurora completa, sin escribir una clase a mano.

Hace la mitad determinista del «regenerar todas las webs con un modelo»:
el modelo escribe el programa (`.openui`), y esto lo convierte en una página con
cabecera correcta, solo los packs que usa y el canal resuelto en el CDN.

Uso:
  python3 scripts/programa-a-html.py openui/ejemplos/flota.openui --salida /tmp/flota.html
  python3 scripts/programa-a-html.py prog.openui --salida x.html --marca ntizar --tema dark
  python3 scripts/programa-a-html.py prog.openui --packs      # solo imprime los packs

El render en el navegador lo hace `openui/aurora-openui.js` (streaming incluido).
Sin JS, la página avisa; no finge un HTML que no ha pintado.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPENUI = ROOT / "openui"

RE_LLAMADA = re.compile(r"\b([A-ZÁÉÍÓÚÑ][\w]*)\s*\(")


def cargar():
    fuente = json.loads((OPENUI / "componentes.json").read_text(encoding="utf-8"))
    censo = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    return fuente, censo


def packs_de(programa, fuente, censo):
    """Packs mínimos: componente → familia del censo → pack."""
    por_nombre = {c["nombre"]: c for c in fuente["componentes"]}
    clase_a_pack = {c: o["pack"] for c, o in censo["objetos"].items()}
    packs, desconocidos = set(), set()
    for nombre in RE_LLAMADA.findall(programa):
        comp = por_nombre.get(nombre)
        if not comp:
            desconocidos.add(nombre)
            continue
        for clase in comp["clases"]:
            pack = clase_a_pack.get(clase)
            if pack:
                packs.add(pack)
    packs.discard("p0-catalog.css")
    packs.add("p12-system.css")  # skip-link y helpers del propio shell
    return sorted(packs), sorted(desconocidos)


def ref_de_canal(canal):
    if canal == "congelado":
        canales = json.loads((ROOT / "datos" / "canales.json").read_text(encoding="utf-8"))
        return canales["canales"]["congelado"]["tag"]
    if canal == "local":
        return None
    canales = json.loads((ROOT / "datos" / "canales.json").read_text(encoding="utf-8"))
    return canales["canales"]["vivo"]["rango"]


def plantilla(programa, packs, ref, marca, tema, titulo, descripcion):
    if ref is None:  # rutas locales: la página se sirve desde el propio repo
        base = "../"
        hojas = ["%stokens.css" % base] + ["%spacks/%s" % (base, p) for p in packs]
        runtime = "%sopenui/aurora-openui.js" % base
        spec = "%sopenui/aurora.spec.json" % base
    else:
        base = "https://cdn.jsdelivr.net/gh/Ntizar/Aurora@%s/" % ref
        hojas = ["%stokens.css" % base] + ["%spacks/%s" % (base, p) for p in packs]
        runtime = "%sopenui/aurora-openui.js" % base
        spec = "%sopenui/aurora.spec.json" % base
    enlaces = "\n".join('<link rel="stylesheet" href="%s">' % h for h in hojas)
    return """<!DOCTYPE html>
<html lang="es" data-nz-theme="{tema}" data-nz-marca="{marca}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
{enlaces}
</head>
<body class="nz">
<a class="nz-skip-link" href="#contenido">Saltar al contenido</a>
<main id="contenido"></main>
<noscript><div class="nz-container"><div class="nz-alert nz-alert--warning"><span class="nz-alert__icon" aria-hidden="true">!</span><div class="nz-alert__body"><span class="nz-alert__title">Esta página se pinta en el navegador</span><span class="nz-alert__msg">Activa JavaScript: el programa OpenUI se convierte en markup de Aurora al cargar.</span></div></div></div></noscript>
<footer class="nz-container"><p>Hecho con ❤️ por David Antizar</p></footer>

<script type="text/plain" id="programa">{programa}</script>
<script src="{runtime}"></script>
<script>
  AuroraOpenUI.iniciar({{ spec: "{spec}" }}).then(function () {{
    AuroraOpenUI.pintar(document.getElementById("programa").textContent, "main");
  }}).catch(function (e) {{
    document.querySelector("main").innerHTML = '<div class="nz-container"><div class="nz-alert nz-alert--danger"><span class="nz-alert__icon">!</span><div class="nz-alert__body"><span class="nz-alert__title">No se pudo cargar la capa OpenUI</span><span class="nz-alert__msg">' + e.message + "</span></div></div></div>";
  }});
</script>
</body>
</html>
""".format(tema=tema, marca=marca, titulo=titulo, descripcion=descripcion,
           enlaces=enlaces, programa=programa.strip(), runtime=runtime, spec=spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programa")
    ap.add_argument("--salida", "-o")
    ap.add_argument("--marca", default="aurora")
    ap.add_argument("--tema", default="light", choices=["light", "dark"])
    ap.add_argument("--canal", default="vivo", choices=["vivo", "congelado", "local"])
    ap.add_argument("--titulo")
    ap.add_argument("--descripcion", default="Página generada con Aurora a partir de un programa OpenUI Lang.")
    ap.add_argument("--packs", action="store_true", help="solo imprime los packs que necesita")
    args = ap.parse_args()

    ruta = pathlib.Path(args.programa)
    programa = ruta.read_text(encoding="utf-8")
    fuente, censo = cargar()
    packs, desconocidos = packs_de(programa, fuente, censo)
    if desconocidos:
        print("  ✗ componentes que no existen en la biblioteca: %s" % ", ".join(desconocidos))
        return 1
    if args.packs:
        print(" ".join(packs))
        return 0
    if not args.salida:
        print("Falta --salida (o usa --packs)")
        return 2

    ref = ref_de_canal(args.canal)
    titulo = args.titulo or ruta.stem.replace("-", " ").capitalize()
    html = plantilla(programa, packs, ref, args.marca, args.tema, titulo, args.descripcion)
    salida = pathlib.Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    print("escrito %s · canal %s (%s) · %d packs: %s"
          % (salida, args.canal, ref or "local", len(packs), ", ".join(packs)))
    print("siguiente paso: python3 scripts/auditar-uso.py %s" % salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
