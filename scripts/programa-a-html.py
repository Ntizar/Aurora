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

FIRMAS = ("full", "subtle", "none")
PIE_FULL = "Hecho con ❤️ por David Antizar"


def cargar():
    fuente = json.loads((OPENUI / "componentes.json").read_text(encoding="utf-8"))
    censo = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    return fuente, censo


def marcas_disponibles():
    """Presets publicados (marcas/registro.json). Si no está, el perfil pedido no existe."""
    reg = json.loads((ROOT / "marcas" / "registro.json").read_text(encoding="utf-8"))
    return [m["nombre"] for m in reg]


def validar_marca(marca):
    """B02: el perfil pedido debe EXISTIR. Un fallback silencioso al azul de Aurora
    ocultaría un error de integración (plan §9)."""
    disponibles = marcas_disponibles()
    if marca not in disponibles:
        print("  ✗ perfil de marca inexistente: %r" % marca)
        print("    perfiles disponibles: %s" % ", ".join(disponibles))
        print("    (crea el tuyo: python scripts/generar-marca.py <nombre> \"#hex1\" \"#hex2\")")
        return False
    return True


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


def politica_url(programa):
    """B04: una URL no permitida en el programa se RECHAZA en compilación, con error
    legible. javascript:/data:/vbscript: no son navegación generada (plan §6.2.5)."""
    malas = []
    for rx, etiqueta in (
        (r"""["']\s*(javascript|vbscript)\s*:""", "javascript:/vbscript:"),
        (r"""["']\s*data\s*:\s*(?!image/svg)""", "data: no-imagen"),
    ):
        for m in re.finditer(rx, programa, flags=re.I):
            linea = programa[:m.start()].count("\n") + 1
            malas.append((linea, etiqueta, programa[m.start():m.start() + 60].replace("\n", " ")))
    return malas


def plantilla(programa, packs, ref, marca, tema, titulo, descripcion, firma="full", inicio="",
              modo="sitio"):
    if ref is None:  # rutas locales: la página se sirve desde el propio repo
        base = "../"
        hojas = ["%stokens.css" % base] + ["%smarcas/%s.css" % (base, marca)] + \
                ["%spacks/%s" % (base, p) for p in packs]
        runtime = "%sopenui/aurora-openui.js" % base
        spec = "%sopenui/aurora.spec.json" % base
    else:
        base = "https://cdn.jsdelivr.net/gh/Ntizar/Aurora@%s/" % ref
        hojas = ["%stokens.css" % base] + ["%smarcas/%s.css" % (base, marca)] + \
                ["%spacks/%s" % (base, p) for p in packs]
        runtime = "%sopenui/aurora-openui.js" % base
        spec = "%sopenui/aurora.spec.json" % base
    enlaces = "\n".join('<link rel="stylesheet" href="%s">' % h for h in hojas)
    # B05: la firma es una POLÍTICA del proyecto, no un tatuaje de cada componente.
    # full → pie visible · subtle → una línea secundaria · none → sin firma.
    # El atributo data-nz-firma es lo que auditar-uso.py comprueba (no la marca de agua).
    if firma == "none":
        pie = ""
    elif firma == "subtle":
        pie = ('<footer class="nz-container"><p class="nz-text--small nz-text--muted">'
               + PIE_FULL + "</p></footer>")
    else:
        pie = '<footer class="nz-container"><p>' + PIE_FULL + "</p></footer>"
    return """<!DOCTYPE html>
<html lang="es" data-nz-theme="{tema}" data-nz-marca="{marca}" data-nz-firma="{firma}"{attr_inicio}{attr_modo}>
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
{pie}

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
""".format(tema=tema, marca=marca, firma=firma, titulo=titulo, descripcion=descripcion,
           enlaces=enlaces, pie=pie, attr_inicio=(' data-nz-inicio="%s"' % inicio) if inicio else "",
           attr_modo=(' data-nz-modo="%s"' % modo) if modo != "sitio" else "",
           programa=programa.strip(), runtime=runtime, spec=spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programa")
    ap.add_argument("--salida", "-o")
    ap.add_argument("--marca", default="aurora")
    ap.add_argument("--tema", default="light", choices=["light", "dark"])
    ap.add_argument("--canal", default="vivo", choices=["vivo", "congelado", "local"])
    ap.add_argument("--firma", default="full", choices=list(FIRMAS),
                    help="política de atribución: full (pie completo) · subtle (línea secundaria) · none (sin firma)")
    ap.add_argument("--inicio", default="",
                    help="homeRoute: ruta de inicio del producto; la marca de la barra enlaza a ella")
    ap.add_argument("--modo", default="sitio", choices=["sitio", "producto"],
                    help="sitio (reglas del catálogo) · producto (entrega: homeRoute, sin placeholders #)")
    ap.add_argument("--titulo")
    ap.add_argument("--descripcion", default="Página generada con Aurora a partir de un programa OpenUI Lang.")
    ap.add_argument("--packs", action="store_true", help="solo imprime los packs que necesita")
    args = ap.parse_args()

    ruta = pathlib.Path(args.programa)
    programa = ruta.read_text(encoding="utf-8")

    # B04: política de URL ANTES de pintar nada (error legible, no un CTA muerto).
    malas = politica_url(programa)
    if malas:
        print("  ✗ URL no permitida en el programa (%d):" % len(malas))
        for linea, etiqueta, muestra in malas[:5]:
            print("    línea %d · %s · %s…" % (linea, etiqueta, muestra))
        return 1

    # B02: el perfil pedido tiene que existir; sin fallback silencioso al azul de Aurora.
    if not args.packs and not validar_marca(args.marca):
        return 1

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
    html = plantilla(programa, packs, ref, args.marca, args.tema, titulo, args.descripcion,
                     firma=args.firma, inicio=args.inicio, modo=args.modo)
    salida = pathlib.Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    print("escrito %s · canal %s (%s) · marca %s · firma %s · modo %s · %d packs: %s"
          % (salida, args.canal, ref or "local", args.marca, args.firma, args.modo,
             len(packs), ", ".join(packs)))
    print("siguiente paso: python3 scripts/auditar-uso.py %s" % salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
