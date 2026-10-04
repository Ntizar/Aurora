# -*- coding: utf-8 -*-
"""Audita el USO de Aurora 7 en páginas consumidoras (el lint del agente).

El validador del sistema (`validar-css.py`) comprueba los packs desde dentro.
Este comprueba las páginas que CONSUMEN Aurora 7 desde fuera: el HTML que un
agente (o una persona) genera enlazando el CDN. Es el paso que falta en el
bucle: la IA verifica su propio output antes de entregarlo.

Qué detecta:
  · clases nz-* inventadas (no existen en components.json)  → FALLO
  · clases del shell del catálogo (cat-*, demo-*)           → FALLO
  · packs del sistema que faltan por enlazar                → FALLO
  · CDN sin pinear (@master)                                → AVISO
  · gradientes, backdrop-filter, !important                 → FALLO (manifiesto)
  · colores a mano (#hex, rgb, hsl)                         → AVISO
  · desktop-first (@media max-width)                        → AVISO
  · falta body.nz / data-nz-theme / lang=es / atribución    → AVISO
Composición (COMPOSICION.md):
  · emojis fuera de la atribución                           → FALLO
  · más de un <h1>                                          → FALLO
  · presupuesto de color (>5 momentos saturados)            → AVISO
  · marca y acento compitiendo a la vez                     → AVISO
  · font-size propio por debajo de 13px                     → AVISO
  · más de 4 tamaños tipográficos                           → AVISO
  · app/panel sin contenedor ancho                          → AVISO

Uso:
  python scripts/auditar-uso.py pagina.html [otra.html …]
  curl -s https://mi-sitio.es | python scripts/auditar-uso.py -
  python scripts/auditar-uso.py --selftest      # test de la propia herramienta

Salida: informe por página y código de salida 1 si hay fallos.
"""
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CDN_RE = re.compile(
    r'href="(https://cdn\.jsdelivr\.net/gh/Ntizar/Aurora7@([^/"]+)/([^"]+))"')
CLASE_RE = re.compile(r'class="([^"]*)"')
# enlaces locales (recetas/ y páginas del propio repo): ../tokens.css, ../packs/x.css
LOCAL_RE = re.compile(r'href="(?:\.\./)?(tokens\.css|packs/[a-z0-9-]+\.css)"')
STYLE_RE = re.compile(r'style="([^"]*)"')
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\(")

# Clases legítimas que no viven en el censo de componentes
EXENTAS = {"nz", "nz-visually-hidden", "nz-vh", "nz-print-hide"}

# --- Composición (COMPOSICION.md): reglas que el lint hace cumplir -------------
# Emoji = pictograma. Los símbolos tipográficos (✓ ✕ → ⬆ …) NO cuentan: son
# tipografía legítima. Si llevan el selector de variación U+FE0F, sí se cazan
# (➡️ con FE0F cae; ➡ solo, no).
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\u2B00-\u2BFF\uFE0F]")
TIPOGRAFICOS = set("\u2713\u2715\u2717\u2794\u279c\u2192\u2190\u2191\u2193"
                   "\u2b05\u2b06\u2b07\u2b95")
ATRIBUCION = "Hecho con ❤️ por David Antizar"
# elementos que gastan un "momento" de color saturado
COLOR_RE = re.compile(
    r"nz-(?:btn|cta|badge|chip|lbl|kpi|alert)(?:--(?:primary|accent|brand|success|warning|danger|info))")
FONT_PX_RE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px")
TEXTO_VAR_RE = re.compile(r"var\((--nz-text-(?:2xs|xs|sm|base|md|lg|xl|2xl|3xl|4xl))\)")


def auditar_composicion(html):
    """Las 12 leyes de COMPOSICION.md que se pueden comprobar mecánicamente."""
    fallos, avisos = [], []
    # los comentarios HTML no son interfaz: no cuentan (evita falsos positivos
    # por documentar dentro de la propia página)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)

    # 1 y 10 · emojis fuera de la atribución
    cuerpo = html.replace(ATRIBUCION, "")
    emojis = [c for c in EMOJI_RE.findall(cuerpo) if c not in TIPOGRAFICOS]
    if emojis:
        unicos = "".join(sorted(set(emojis)))[:14]
        fallos.append(f"emoji-en-ui: {len(emojis)} emoji(s) fuera de la atribución ({unicos}) — usa .nz-icon en SVG")

    # 2 · presupuesto de color
    momentos = COLOR_RE.findall(html)
    if len(momentos) > 5:
        avisos.append(f"presupuesto-color: {len(momentos)} elementos con color saturado (máx 5)")

    # 3 · dos protagonistas
    marca = len(re.findall(r"nz-\w+--(?:primary|brand)", html))
    acento = len(re.findall(r"nz-\w+--accent", html))
    if marca >= 2 and acento >= 2:
        avisos.append(f"dos-protagonistas: {marca} de marca y {acento} de acento compiten en la misma página")

    # 4 · mínimo tipográfico (solo en CSS propio; el sistema ya garantiza el suyo)
    chicos = sorted({v for v in FONT_PX_RE.findall(html) if float(v) < 13})
    if chicos:
        avisos.append(f"minimo-tipografico: font-size por debajo de 13px ({', '.join(chicos)}px)")

    # 5 · jerarquía
    h1 = len(re.findall(r"<h1[\s>]", html))
    if h1 > 1:
        fallos.append(f"jerarquia: {h1} <h1> en la misma página (debe haber exactamente uno)")

    # 6 · escala tipográfica: máximo 4 tamaños
    usados = sorted(set(TEXTO_VAR_RE.findall(html)))
    if len(usados) > 4:
        avisos.append(f"escala-tipografica: {len(usados)} tamaños distintos (máx 4): {', '.join(usados)}")

    # 7 · ancho por tipo de página
    es_app = bool(re.search(r"nz-appshell|nz-navbar|nz-dash-grid", html))
    hay_ancho = bool(re.search(r"nz-container(?![\w-])|nz-container--(?:fluid|wide)|nz-main--wide|nz-dash-grid", html))
    if es_app and not hay_ancho:
        avisos.append("ancho-composicion: parece una app/panel y no declara contenedor ancho "
                      "(nz-container / nz-container--fluid / nz-dash-grid)")

    return fallos, avisos


def cargar_censo():
    ruta = ROOT / "components.json"
    if not ruta.exists():
        sys.exit("No existe components.json. Ejecuta antes: python scripts/generar-llm-docs.py")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    clase_a_familia = {}
    for familia, objeto in datos["objetos"].items():
        for clase in objeto["clases"]:
            clase_a_familia[clase] = familia
    packs = set(datos["packs"].keys())
    return clase_a_familia, packs, datos["version"]


def auditar(html, clase_a_familia, packs_conocidos):
    """Devuelve (fallos, avisos, info) de una página."""
    fallos, avisos = [], []

    # --- 1. CSS enlazado (CDN o local, para las páginas del repo) ------------
    enlaces = CDN_RE.findall(html)
    locales = LOCAL_RE.findall(html)
    ficheros = {e[2] for e in enlaces} | set(locales)
    versiones = {e[1] for e in enlaces}
    if not enlaces and not locales:
        avisos.append("No enlaza el CSS de Aurora (¿es una página Aurora?)")
    if "master" in versiones:
        avisos.append("CDN sin pinear (@master): jsDelivr puede servir CSS viejo desde su caché. Pineas con @vX.Y.Z")
    if (enlaces or locales) and "tokens.css" not in ficheros and "all.css" in " ".join(ficheros):
        avisos.append("tokens.css no está enlazado: los packs lo necesitan para resolver los tokens")
    for fichero in ficheros:
        if fichero.startswith("packs/") and fichero != "packs/all.css":
            if fichero[len("packs/"):] not in packs_conocidos:
                fallos.append(f"Pack enlazado que no existe en el sistema: {fichero}")

    # --- 2. Clases -----------------------------------------------------------
    vistas = []
    for valor in CLASE_RE.findall(html):
        vistas.extend(valor.split())
    nz = {c for c in vistas if c.startswith("nz-")}
    invented = sorted(c for c in nz if c not in clase_a_familia and c not in EXENTAS)
    for c in invented:
        fallos.append(f"Clase inventada (no está en components.json): .{c}")
    for c in sorted({c for c in vistas if c.startswith(("cat-", "demo-"))}):
        fallos.append(f"Clase del shell del catálogo (no es del sistema): .{c}")

    # --- 3. Packs necesarios vs enlazados ------------------------------------
    if enlaces or locales:
        # pack de cada familia usada
        familias = {clase_a_familia[c] for c in nz if c in clase_a_familia}
        necesarios = {FAMILIA_PACK.get(f, "") for f in familias}
        necesarios.discard("")
        enlazados = {f[len("packs/"):] for f in ficheros if f.startswith("packs/")}
        if "all.css" in enlazados:
            necesarios = set()  # all.css lo cubre todo
        for p in sorted(necesarios - enlazados):
            fallos.append(f"Falta por enlazar el pack {p} (lo usan clases de la página)")
        for p in sorted(enlazados - necesarios - {"all.css"}):
            avisos.append(f"Pack enlazado sin uso aparente: {p} (peso muerto, valora quitarlo)")

    # --- 4. Manifiesto en <style> y style="" ---------------------------------
    bloques = " ".join(STYLE_BLOCK_RE.findall(html))
    inline = " ".join(STYLE_RE.findall(html))
    for nombre, texto in (("<style>", bloques), ('style=""', inline)):
        if "gradient" in texto.lower():
            fallos.append(f"Gradiente en {nombre}: prohibido por el manifiesto")
        if "backdrop-filter" in texto.lower():
            fallos.append(f"backdrop-filter en {nombre}: prohibido por el manifiesto")
        if "!important" in texto:
            fallos.append(f"!important en {nombre}: prohibido por el manifiesto")
        for rx, etiqueta in ((HEX_RE, "hex"), (RGB_RE, "rgb/hsl")):
            toques = rx.findall(texto)
            if toques:
                avisos.append(
                    f"{len(toques)} color(es) {etiqueta} a mano en {nombre}: usa var(--nz-*) ({', '.join(toques[:3])}…)")
    if "@media" in bloques and re.search(r"@media[^{]*max-width", bloques):
        avisos.append("@media (max-width) detectado: Aurora 7 es mobile-first (base 1 columna + min-width)")

    # --- 5. Estructura mínima -------------------------------------------------
    if not re.search(r'<html[^>]*lang="es"', html):
        avisos.append('<html> sin lang="es"')
    if not re.search(r'<html[^>]*data-nz-theme="(light|dark)"', html):
        avisos.append('<html> sin data-nz-theme="light|dark"')
    if not re.search(r"<body[^>]*class=\"[^\"]*\bnz\b", html):
        avisos.append('<body> sin class="nz"')
    if "Hecho con ❤️ por David Antizar" not in html:
        avisos.append('Falta la atribución exacta: "Hecho con ❤️ por David Antizar"')

    # --- 6. Composición (COMPOSICION.md) -------------------------------------
    f2, a2 = auditar_composicion(html)
    fallos.extend(f2)
    avisos.extend(a2)

    return fallos, avisos


# mapa familia → pack, relleno al cargar el censo
FAMILIA_PACK = {}


def main():
    global FAMILIA_PACK
    args = sys.argv[1:]

    if args and args[0] == "--selftest":
        return selftest()

    clase_a_familia, packs_conocidos, version = cargar_censo()
    FAMILIA_PACK = {}
    censo = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    for familia, objeto in censo["objetos"].items():
        FAMILIA_PACK[familia] = objeto["pack"]

    rutas = []
    for a in args:
        if a == "-":
            rutas.append(("-: stdin", sys.stdin.read()))
        elif "/" in a and a.startswith("http"):
            import urllib.request
            rutas.append((a, urllib.request.urlopen(a, timeout=30).read().decode("utf-8")))
        else:
            rutas.extend((str(p), p.read_text(encoding="utf-8"))
                         for p in [pathlib.Path(a)] if p.exists())
    if not rutas:
        rutas = [(str(p), p.read_text(encoding="utf-8"))
                 for p in map(pathlib.Path, sorted(glob.glob(str(ROOT / "examples" / "*.html"))))]
        print(f"(sin argumentos: auditando examples/ de fábrica)")

    total_fallos = 0
    for nombre, html in rutas:
        fallos, avisos = auditar(html, clase_a_familia, packs_conocidos)
        total_fallos += len(fallos)
        print(f"\n== {nombre}")
        for f in fallos:
            print(f"  ✗ FALLO  {f}")
        for a in avisos:
            print(f"  ! aviso  {a}")
        if not fallos and not avisos:
            print("  ✓ limpia: clases, packs, manifiesto y estructura OK")
        print(f"  → {len(fallos)} fallos · {len(avisos)} avisos")

    print(f"\nTOTAL: {total_fallos} fallos")
    return 1 if total_fallos else 0


def selftest():
    """El lint se prueba a sí mismo: una página mala debe salir con fallos."""
    clase_a_familia, packs_conocidos, version = cargar_censo()
    global FAMILIA_PACK
    FAMILIA_PACK = {f: o["pack"] for f, o in
                    json.loads((ROOT / "components.json").read_text(encoding="utf-8"))["objetos"].items()}

    # Ojo: esta página mala enlaza tokens.css pero NO p1-layout.css, para que
    # el lint cace también el pack que falta por enlazar.
    mala = f"""<!DOCTYPE html><html lang="es"><head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora7@master/tokens.css">
<style>.x {{ background: linear-gradient(90deg, red, blue); color: #ff0000; font-size: 11px }}</style>
</head><body><h1>Uno</h1><h1>Dos</h1><main class="nz-container nz-card nz-boton">\U0001F511 Hola</main></body></html>"""

    # Y una página BUENA: debe salir con 0 fallos (si no, hay falso positivo).
    buena = """<!DOCTYPE html><html lang="es" data-nz-theme="light"><head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora7@v7.2.2/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora7@v7.2.2/packs/p1-layout.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora7@v7.2.2/packs/p3-typography.css">
</head><body class="nz"><main class="nz-container"><h1 class="nz-h1">Panel</h1>
<p class="nz-lead">Datos de ejemplo.</p></main>
<footer>Hecho con \u2764\ufe0f por David Antizar</footer></body></html>"""

    fallos, avisos = auditar(mala, clase_a_familia, packs_conocidos)
    texto = " | ".join(fallos + avisos)
    f_buena, a_buena = auditar(buena, clase_a_familia, packs_conocidos)
    esperados = [
        ("clase inventada .nz-card", "nz-card" in texto),
        ("clase inventada .nz-boton", "nz-boton" in texto),
        ("gradiente detectado", "Gradiente" in texto),
        ("color hex a mano", "hex" in texto),
        ("CDN @master avisado", "@master" in texto),
        ("falta pack de nz-container", "Falta por enlazar el pack p1-layout.css" in texto),
        ("body sin nz", 'class="nz"' in texto),
        ("falta atribución", "atribución" in texto),
        ("emoji en UI (ley 1)", "emoji-en-ui" in texto),
        ("dos <h1> (ley 5)", "jerarquia" in texto),
        ("font-size < 13px (ley 4)", "minimo-tipografico" in texto),
        ("página buena sin fallos", not f_buena),
    ]
    ok = True
    for nombre, cond in esperados:
        print(f"  {'✓' if cond else '✗ FALLO DEL TEST'} {nombre}")
        ok = ok and cond
    print(f"\nSELFTEST: {'OK — el lint caza los ' + str(len(esperados)) + ' defectos' if ok else 'FALLIDO'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
