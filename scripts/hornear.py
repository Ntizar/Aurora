# -*- coding: utf-8 -*-
"""Hornea un programa OpenUI: programa → HTML estático, sin escribir markup a mano.

Por qué existe: una página generada se pintaba en el navegador (runtime) o se
copiaba a mano al HTML para que fuera estática. Copiarla a mano significa mantener
dos veces lo mismo (el `.openui` y el HTML), y ahí se van los tokens y aparecen
las divergencias: la portada prometía «el programa se muestra abajo» y no había
nada abajo, porque el HTML se había escrito a mano.

Esto cierra el círculo: el programa es la única fuente. Se compila, se pinta en un
Chrome headless con la red servida por HTTP local (el runtime carga la spec por
`fetch`, que en `file://` falla por CORS) y se extrae el `<main>` ya pintado.

  briefs/portada.openui ──programa-a-html.py──► página con runtime
                        ──chrome --dump-dom────► DOM final
                        ──este script──────────► HTML estático (0 JS)

Uso:
  python3 scripts/hornear.py briefs/portada.openui --salida briefs/portada.tmpl.html
  python3 scripts/hornear.py prog.openui --salida out.html --plantilla-base
  python3 scripts/hornear.py prog.openui --salida out.html --navegador "C:/.../chrome.exe"

`--plantilla-base` deja `{{OBJETOS}}` y `{{PROGRAMA}}` sin sustituir para que
`build-catalog.py` los clave con los datos reales del censo (así la portada nunca
inventa un número). Sin esa bandera, el HTML sale cerrado y listo para servir.
"""
import argparse
import functools
import html
import http.server
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAVEGADORES = [
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
RE_MAIN = re.compile(r'<main id="contenido">(.*?)</main>', re.S)
FALLOS = ("No se pudo cargar la capa OpenUI", "se pinta en el navegador")


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def navegador(ruta=None):
    if ruta:
        return ruta
    for c in NAVEGADORES:
        if pathlib.Path(c).exists():
            return c
    raise SystemExit("No encuentro Chrome ni Edge. Pásalo con --navegador.")


class Silencioso(http.server.SimpleHTTPRequestHandler):
    """Sirve el repo sin llenar la consola: el horneado no necesita log."""

    def log_message(self, *args):
        pass


def servir(directorio, puerto):
    """Servidor HTTP local en un hilo: el runtime hace fetch() y en file:// no puede."""
    handler = functools.partial(Silencioso, directory=str(directorio))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", puerto), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def compilar(programa, tmp, marca, tema, titulo, descripcion):
    cmd = [sys.executable, str(ROOT / "scripts" / "programa-a-html.py"), str(programa),
           "--salida", str(tmp), "--marca", marca, "--tema", tema, "--canal", "local",
           "--titulo", titulo, "--descripcion", descripcion]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(out.stdout + out.stderr)
    return out.stdout.strip()


def hornear(pagina_url, nav, presupuesto):
    cmd = [nav, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=%d" % presupuesto, "--dump-dom", pagina_url]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not out.stdout:
        raise SystemExit("Chrome no devolvió DOM:\n" + (out.stderr or "")[:800])
    return out.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("programa")
    ap.add_argument("--salida", "-o", required=True)
    ap.add_argument("--marca", default="ntizar")
    ap.add_argument("--tema", default="light", choices=["light", "dark"])
    ap.add_argument("--titulo")
    ap.add_argument("--descripcion", default="Página generada con Aurora a partir de un programa OpenUI Lang.")
    ap.add_argument("--base", default="", help="prefijo de los enlaces CSS ('' si la salida va en la raíz del repo)")
    ap.add_argument("--presupuesto", type=int, default=10000, help="ms de reloj virtual para Chrome")
    ap.add_argument("--navegador")
    ap.add_argument("--plantilla-base", action="store_true",
                    help="deja {{OBJETOS}} y {{PROGRAMA}} para que build-catalog los clave")
    args = ap.parse_args()

    programa = pathlib.Path(args.programa)
    if not programa.is_absolute():
        programa = (pathlib.Path.cwd() / programa).resolve()
    texto = programa.read_text(encoding="utf-8")
    titulo = args.titulo or programa.stem.replace("-", " ").capitalize()

    # El horneado se hace siempre desde UNA subcarpeta del repo (audit/): el
    # compilador emite rutas "../" para el canal local, así que un solo nivel es
    # justo lo que hace que tokens.css y packs/*.css resuelvan. Dos niveles
    # (audit/.hornear/) apuntan a audit/ y el CSS no llega: el runtime no pinta.
    (ROOT / "audit").mkdir(exist_ok=True)
    tmp = ROOT / "audit" / "_horneado.html"
    print("1/3 compilando  %s" % compilar(programa, tmp, args.marca, args.tema, titulo, args.descripcion))

    puerto = puerto_libre()
    httpd = servir(ROOT, puerto)
    try:
        url = "http://127.0.0.1:%d/%s" % (puerto, tmp.relative_to(ROOT).as_posix())
        print("2/3 horneando    %s" % url)
        dom = hornear(url, navegador(args.navegador), args.presupuesto)
    finally:
        httpd.shutdown()

    m = RE_MAIN.search(dom)
    cuerpo = m.group(1).strip() if m else ""
    for fallo in FALLOS:
        if fallo in cuerpo:
            raise SystemExit("El runtime no pintó: %r\n%s" % (fallo, cuerpo[:400]))
    if len(cuerpo) < 500:
        raise SystemExit("El <main> horneado sale vacío o casi (%d chars). Revisa el programa." % len(cuerpo))

    tema = args.tema
    marca = args.marca
    if args.plantilla_base:
        apendice = ('\n<pre class="nz-code nz-code--block" tabindex="0" role="region"'
                    ' aria-label="Programa OpenUI de esta página">{{PROGRAMA}}</pre>\n')
    else:
        import json
        censo = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
        apendice = ('\n<pre class="nz-code nz-code--block" tabindex="0" role="region"'
                    ' aria-label="Programa OpenUI de esta página">' + html.escape(texto) + "</pre>\n")

    # El apéndice con el programa entra DENTRO de la última sección: si cae
    # suelto tras el </section>, el <pre> queda fuera del bloque que lo presenta.
    if apendice.strip():
        corte = cuerpo.rfind("</section>")
        cuerpo = (cuerpo[:corte] + apendice.strip() + cuerpo[corte:]) if corte != -1 else cuerpo + apendice

    packs = subprocess.run([sys.executable, str(ROOT / "scripts" / "programa-a-html.py"),
                            str(programa), "--packs"], capture_output=True, text=True).stdout.split()
    base = args.base
    hojas = "\n".join('<link rel="stylesheet" href="%s%s">' % (base, h) for h in
                      ["tokens.css"] + ["packs/%s" % p for p in packs])

    doc = """<!DOCTYPE html>
<html lang="es" data-nz-theme="%(tema)s" data-nz-marca="%(marca)s">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>%(titulo)s</title>
<meta name="description" content="%(descripcion)s">
%(hojas)s
</head>
<body class="nz">
<a class="nz-skip-link" href="#contenido">Saltar al contenido</a>
<main id="contenido">%(cuerpo)s
</main>
<footer class="nz-footer">
  <p>Hecho con ❤️ por David Antizar</p>
</footer>
</body>
</html>
""" % dict(tema=tema, marca=marca, titulo=titulo, descripcion=args.descripcion,
           hojas=hojas, cuerpo=cuerpo, apendice=apendice)

    # Cifras y programa sin clavar cuando se hornea la plantilla base.

    salida = pathlib.Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(doc, encoding="utf-8")
    tmp.unlink(missing_ok=True)
    print("3/3 escrito      %s · %d packs · %d KB · %d bytes de main"
          % (salida, len(packs), len(doc.encode("utf-8")) // 1024, len(cuerpo)))
    print("siguiente: python scripts/auditar-uso.py %s" % salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
