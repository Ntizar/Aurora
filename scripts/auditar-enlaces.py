# -*- coding: utf-8 -*-
"""Audita los enlaces locales, los anclajes y el camino de vuelta a la portada.

Nació de un fallo real y visible: `bloques/recetas/index.html` (dos niveles de
profundidad) enlazaba `../tokens.css`, que resuelve a `bloques/tokens.css` — un
fichero que no existe. La página se servía **sin una sola hoja de estilo** y nadie
se enteraba, porque el HTML es válido y los enlaces no se prueban en ninguna
puerta. Además no tenía forma de volver a la portada: había que editar la URL.

Comprueba lo que el resto de la CI no mira (ampliación B04 del plan de mejora:
sigue habiendo UN solo auditor, sin sistema paralelo):

1. **Todo enlace o recurso local existe.** Se parsea el DOM (HTMLParser), no solo
   regex sobre el crudo; `href` y `src` relativos se resuelven contra el directorio
   del fichero y contra la base de despliegue (`--base /Aurora/`) si es absoluto.
2. **Toda página sabe volver.** Cualquier HTML que no esté en la raíz debe tener
   al menos un enlace que resuelva a la portada. En MODO PRODUCTO
   (`<html data-nz-modo="producto">`) el requisito cambia: volver al `data-nz-inicio`
   declarado (homeRoute) y que la marca sea enlace a ese inicio — otra aplicación
   vuelve a SU casa, no al catálogo de Aurora (plan §6.1).
3. **Anclajes resueltos**: `#nombre` debe existir como `id` en la página; en
   `archivo.html#nombre`, en el destino. IDs duplicados = fallo (plan §6.2.3).
4. **Protocolos**: `javascript:`/`vbscript:`/`data:` (no-imagen) en un `href` son
   fallo en cualquier modo: no son navegación generada (plan §6.2.5).
5. **Placeholders**: `href="#"` exacto = fallo en modo producto (una entrega de
   producto no tiene destinos vacíos); en demos del catálogo se cuenta como aviso —
   la paginación y las migas de demo viven de eso (plan §6.2.2).
6. **Externos aparte** (`--externos`): HEAD con timeout y caché en
   `audit/enlaces-externos.json`, distinguiendo 404 de bloqueo/auth/rate-limit.
   No va en la CI: la puerta no depende de la red de terceros (plan §6.2.6).

Uso:
  python3 scripts/auditar-enlaces.py            # puerta de CI
  python3 scripts/auditar-enlaces.py --lista    # con el detalle de cada fichero
  python3 scripts/auditar-enlaces.py --base /Aurora/   # resolución bajo subruta
  python3 scripts/auditar-enlaces.py --externos # además, destinos externos
"""
import argparse
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXTERNOS = ("http://", "https://", "mailto:", "tel:", "//")
EXCLUIR = {"node_modules", ".git", "audit", "briefs"}  # briefs/: plantillas, no páginas servidas
CACHE_EXTERNOS = ROOT / "audit" / "enlaces-externos.json"


# --- parseo DOM: el plan pide HTML/DOM, no regex sobre el crudo -----------------
class Recolector(HTMLParser):
    """Extrae enlaces, ids, modo y homeRoute de la página desde el DOM real.

    El contenido de <pre>/<code>/<textarea> es muestra de código, no marcado:
    se ignora (los snippets escapados no enlazan nada).
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.enlaces = []          # [(tag, url)] de href/src
        self.ids = []              # ids en orden de aparición
        self.modo = "sitio"        # data-nz-modo="producto" activa la política estricta
        self.inicio = ""           # data-nz-inicio (homeRoute del producto)
        self.marca_href = None     # href del primer .nz-navbar__brand
        self._muestra = 0          # dentro de <pre>/<code>: muestra, no marcado

    def handle_starttag(self, tag, attrs):
        if tag in ("pre", "code", "textarea"):
            self._muestra += 1
        if self._muestra:
            return
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        for k in ("href", "src"):
            if a.get(k) is not None:
                self.enlaces.append((tag, a[k]))
        if tag == "html":
            if a.get("data-nz-modo") == "producto":
                self.modo = "producto"
            self.inicio = a.get("data-nz-inicio") or ""
        if "nz-navbar__brand" in (a.get("class") or "").split():
            if a.get("href") is not None and self.marca_href is None:
                self.marca_href = a["href"]

    def handle_endtag(self, tag):
        if tag in ("pre", "code", "textarea") and self._muestra:
            self._muestra -= 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def parsear(texto):
    p = Recolector()
    try:
        p.feed(texto)
        p.close()
    except Exception:
        pass  # HTML malformado: ya lo mira validar-css; aquí no se pierde el resto
    return p


def sin_codigo(texto):
    """Fuera los bloques de código: dentro van ejemplos escapados, no enlaces."""
    return re.sub(r"<(pre|code)\b.*?</\1>", "", texto, flags=re.S | re.I)


def paginas():
    for f in sorted(ROOT.rglob("*.html")):
        partes = set(f.relative_to(ROOT).parts[:-1])
        if partes & EXCLUIR:
            continue
        if f.name.startswith("_"):  # artefactos de horneado
            continue
        yield f


def clasificar(url, base_despliegue):
    """→ ('local', ruta, ancla) | ('ancla', nombre) | ('placeholder',) | ('peligro', url)
          | ('externo', url) | ('otro', url)."""
    u = (url or "").strip()
    if not u:
        return ("placeholder",)
    if u.startswith(("javascript:", "vbscript:")) or re.match(r"^data:(?!image/)", u, re.I):
        return ("peligro", u)
    if u.startswith("#"):
        return ("ancla", u[1:])
    if u.startswith(("http://", "https://", "//")):
        return ("externo", u)
    if u.startswith(("mailto:", "tel:", "data:")):
        return ("otro", u)
    if u.startswith("/"):
        # ruta absoluta bajo base de despliegue: /Aurora/foo → foo (relativa al repo)
        prefijo = base_despliegue.rstrip("/")
        if prefijo and u.startswith(prefijo + "/"):
            u = u[len(prefijo) + 1:]
        else:
            u = u.lstrip("/")
    base, _, ancla = u.partition("#")
    return ("local", base.split("?")[0], ancla.split("?")[0])


def marca_arriba(texto, f, portada):
    """¿Hay un enlace llamado «Aurora» que lleve a la portada antes del primer titular?

    Es la regla del sitio: la marca vive arriba a la izquierda y siempre vuelve a
    casa. Se comprueba en el marcado (antes del primer `<h1`), no a ojo.
    """
    cabecera = re.sub(r"<!--.*?-->", "", texto, flags=re.S).split("<h1", 1)[0]
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', cabecera, re.S):
        href = m.group(1).strip()
        if not href or href.startswith(EXTERNOS) or href.startswith("#"):
            continue
        base = href.split("#")[0].split("?")[0]
        if not base:
            continue
        if (f.parent / base).resolve() == portada:
            etiqueta = re.sub(r"<[^>]+>", "", m.group(2))
            if "Aurora" in etiqueta:
                return True
    return False


def validar_externos(destinos):
    """HEAD a los externos con timeout y caché. Distingue 404 de bloqueo (plan §6.2.6)."""
    import urllib.error
    import urllib.request

    cache = {}
    if CACHE_EXTERNOS.exists():
        try:
            cache = json.loads(CACHE_EXTERNOS.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    rotos, bloqueados = [], []
    for u in sorted(destinos):
        entrada = cache.get(u) or {}
        estado = entrada.get("estado")
        if not estado or estado == "?":
            req = urllib.request.Request(u, method="HEAD",
                                          headers={"User-Agent": "Aurora-Enlaces/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    estado = str(r.status)
            except urllib.error.HTTPError as e:
                estado = str(e.code)
            except Exception:
                estado = "?"  # red/DNS/TLS: no es un 404, es un bloqueo
            cache[u] = {"estado": estado}
        # 404/410/451 = roto · 401/403/405/429/«?» = bloqueo o auth, no rotura
        if estado in ("404", "410", "451"):
            rotos.append((u, estado))
        elif estado in ("401", "403", "405", "429", "?"):
            bloqueados.append((u, estado))
    CACHE_EXTERNOS.parent.mkdir(exist_ok=True)
    CACHE_EXTERNOS.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return rotos, bloqueados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", action="store_true", help="imprime el detalle fichero a fichero")
    ap.add_argument("--base", default="", help="prefijo de despliegue para rutas absolutas (p. ej. /Aurora/)")
    ap.add_argument("--externos", action="store_true",
                    help="además valida destinos externos (HEAD con timeout y caché; fuera de la CI)")
    args = ap.parse_args()

    portada = (ROOT / "index.html").resolve()
    rotos, sin_vuelta, sin_marca = [], [], []
    anclajes_rotos, ids_dup, peligrosos = [], [], []
    placeholders = []          # (rel, n, es_producto)
    externos_todo = set()
    comprobados = 0
    cache_ids = {}             # ruta resuelta → frozenset(ids) de esa página

    def ids_de(destino):
        if destino not in cache_ids:
            try:
                cache_ids[destino] = frozenset(
                    parsear(destino.read_text(encoding="utf-8", errors="replace")).ids)
            except Exception:
                cache_ids[destino] = frozenset()
        return cache_ids[destino]

    lista_paginas = list(paginas())
    for f in lista_paginas:
        rel = f.relative_to(ROOT).as_posix()
        texto = f.read_text(encoding="utf-8", errors="replace")
        dom = parsear(sin_codigo(texto))
        es_producto = dom.modo == "producto"
        destinos = []
        n_placeholder = 0
        vistos, dup = set(), set()
        for i in dom.ids:
            (dup if i in vistos else vistos).add(i)

        for tag, url in dom.enlaces:
            kind = clasificar(url, args.base)
            if kind[0] == "peligro":
                peligrosos.append((rel, kind[1]))
            elif kind[0] == "externo":
                externos_todo.add(kind[1])
            elif kind[0] == "otro":
                pass
            elif kind[0] == "placeholder":
                n_placeholder += 1
            elif kind[0] == "ancla":
                if not kind[1]:
                    n_placeholder += 1  # href="#" suelto
                elif kind[1] not in set(dom.ids):
                    anclajes_rotos.append((rel, "#" + kind[1]))
            else:
                ruta_base, ancla = kind[1], kind[2]
                if ruta_base:
                    destino = (f.parent / ruta_base).resolve()
                    destinos.append(destino)
                    comprobados += 1
                    if not destino.exists():
                        rotos.append((rel, url))
                        continue
                    if ancla and destino.suffix == ".html" and destino != f.resolve():
                        if ancla not in ids_de(destino):
                            anclajes_rotos.append((rel, "%s#%s" % (ruta_base, ancla)))
                elif ancla and ancla not in set(dom.ids):
                    anclajes_rotos.append((rel, "#" + ancla))

        if n_placeholder:
            placeholders.append((rel, n_placeholder, es_producto))

        # IDs duplicados en la propia página (plan §6.2.3)
        if dup:
            ids_dup.append((rel, sorted(dup)))

        # Camino de vuelta: la página cuelga de una carpeta y no ofrece la portada.
        if f.resolve() != portada:
            if es_producto:
                # MODO PRODUCTO: vuelve a SU inicio (data-nz-inicio), no al catálogo.
                if not dom.inicio:
                    sin_vuelta.append("%s · sin data-nz-inicio (homeRoute)" % rel)
                else:
                    inicio_ruta = dom.inicio.split("#")[0].split("?")[0]
                    inicio = (f.parent / inicio_ruta).resolve()
                    if not inicio.exists():
                        sin_vuelta.append("%s · data-nz-inicio=%s no existe" % (rel, dom.inicio))
                    elif dom.marca_href is None:
                        sin_marca.append("%s · la marca no es enlace (modo producto)" % rel)
                    else:
                        mdest = (f.parent / dom.marca_href.split("#")[0].split("?")[0]).resolve()
                        if mdest != inicio:
                            sin_marca.append("%s · la marca (%s) no apunta al inicio (%s)"
                                             % (rel, dom.marca_href, dom.inicio))
            else:
                if portada not in destinos:
                    sin_vuelta.append(rel)
                # Botón de marca: en toda página de subcarpeta, un enlace llamado «Aurora»
                # que lleve a la portada y que esté ARRIBA (antes del primer titular).
                if not marca_arriba(texto, f, portada):
                    sin_marca.append(rel)

        # Etiquetas partidas: un <link> sin cerrar se traga el siguiente y su CSS
        # no llega. Es un fallo invisible (el HTML "pasa") que costó una tarde.
        for i, linea in enumerate(texto.split("\n"), 1):
            s = linea.strip()
            if s.startswith("<link") and not s.endswith(">"):
                rotos.append(("%s:%d" % (rel, i), "etiqueta <link> sin cerrar"))

    ph_fallos = [(rel, n) for rel, n, prod in placeholders if prod]
    ph_avisos = sum(n for rel, n, prod in placeholders if not prod)

    rotos_ext, bloqueados_ext = ([], [])
    if args.externos:
        rotos_ext, bloqueados_ext = validar_externos(externos_todo)

    print("Aurora · enlaces, anclajes y navegación")
    print("  páginas revisadas    %d" % len(lista_paginas))
    print("  enlaces locales      %d" % comprobados)
    print("  enlaces rotos        %d" % len(rotos))
    print("  anclajes rotos       %d" % len(anclajes_rotos))
    print("  IDs duplicados       %d" % len(ids_dup))
    print("  protocolos inseguros %d" % len(peligrosos))
    print("  placeholders «#»     %d fallo(s) producto · %d en demos (aviso)"
          % (sum(n for _, n in ph_fallos), ph_avisos))
    print("  sin vuelta a inicio  %d" % len(sin_vuelta))
    print("  sin botón «Aurora»   %d" % len(sin_marca))
    if args.externos:
        print("  externos             %d rotos · %d bloqueados/rate-limit (caché: audit/enlaces-externos.json)"
              % (len(rotos_ext), len(bloqueados_ext)))

    if args.lista or rotos or sin_vuelta or sin_marca or anclajes_rotos or ids_dup \
            or peligrosos or ph_fallos:
        for rel, u in rotos[:40]:
            print("  ✗ %-42s → %s" % (rel, u))
        for rel, a in anclajes_rotos[:40]:
            print("  ✗ ancla rota %-36s → %s" % (rel, a))
        for rel, ds in ids_dup[:20]:
            print("  ✗ ids duplicados %-34s → %s" % (rel, ", ".join(ds)))
        for rel, u in peligrosos[:20]:
            print("  ✗ protocolo inseguro %-31s → %s" % (rel, u))
        for rel, n in ph_fallos[:20]:
            print("  ✗ placeholder # en modo producto %-17s (%d)" % (rel, n))
        for rel in sin_vuelta[:40]:
            print("  ! %-42s sin enlace a la portada" % rel)
        for rel in sin_marca[:40]:
            print("  ! %-42s sin botón «Aurora» arriba a la izquierda" % rel)
        if args.externos:
            for u, e in rotos_ext[:20]:
                print("  ✗ externo %s → %s" % (u, e))
            for u, e in bloqueados_ext[:20]:
                print("  ! externo bloqueado (no rotura) %s → %s" % (u, e))

    fallos = (len(rotos) + len(sin_vuelta) + len(sin_marca) + len(anclajes_rotos)
              + len(ids_dup) + len(peligrosos) + sum(n for _, n in ph_fallos)
              + len(rotos_ext))
    if fallos:
        print("\nRESULTADO: CON FALLOS — %d problema(s): rotos=%d anclajes=%d dup-ids=%d "
              "inseguros=%d placeholders=%d vuelta=%d marca=%d externos=%d"
              % (fallos, len(rotos), len(anclajes_rotos), len(ids_dup), len(peligrosos),
                 sum(n for _, n in ph_fallos), len(sin_vuelta), len(sin_marca), len(rotos_ext)))
        return 1
    extra = ""
    if args.externos:
        extra = " · %d externo(s) bloqueado(s) (no es rotura)" % len(bloqueados_ext)
    print("\nRESULTADO: VÁLIDO — enlaces, anclaves, vuelta y botón «Aurora» en todas las páginas ✅" + extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
