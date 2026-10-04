# -*- coding: utf-8 -*-
"""Generador del catálogo Aurora.

Fuente única de verdad: specs/NN.json (declarativos) + los packs CSS.
Genera:
  · paginas/NN-*.html  — una página por categoría (todas, incluida la 01)
  · index.html         — portada con buscador global y cifras reales
  · datos/objetos.json — índice de todos los objetos del sistema

Las cifras NO se escriben a mano en ningún sitio: se cuentan del CSS y de los
specs. Si un pack crece, la portada, los encabezados y los pies se actualizan
solos. Así no puede haber tres números distintos para la misma categoría.

Uso: python scripts/build-catalog.py
"""
import html
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGINAS = ROOT / "paginas"
PACKS = ROOT / "packs"
SPECS = ROOT / "specs"
DATOS = ROOT / "datos"

SITIO = "https://ntizar.github.io/Aurora/"
PACK_SHELL = "p0-catalog.css"

# Packs de componentes en orden. Añadir un pack = añadir una línea aquí.
PACKS_COMPONENTES = [f"p{i}-{n}.css" for i, n in [
    (1, "layout"), (2, "navigation"), (3, "typography"), (4, "actions"),
    (5, "forms"), (6, "feedback"), (7, "overlays"), (8, "data"), (9, "media"),
    (10, "commerce"), (11, "social"), (12, "system"),
    (13, "charts"), (14, "ai"), (15, "apps"),
]]


# ------------------------------------------------------------------
# Contar clases declaradas (objetos) leyendo el CSS de verdad
# ------------------------------------------------------------------
COMENTARIO_CSS = re.compile(r"/\*.*?\*/", re.S)


def selectores(css):
    """Lista de preludios de regla del CSS, a cualquier profundidad.

    Recorre el archivo acumulando texto y lo vuelca al llegar a '{'; al llegar a
    '}' vacía el búfer. Así se recogen tanto los selectores de primer nivel como
    los que viven dentro de @media / @supports (que es donde están una docena de
    objetos de este sistema: si se pierden, el censo miente).

    Los COMENTARIOS se eliminan antes de recorrer: un comentario que mencione una
    regla (p. ej. explicar que «.nz-x { display:flex } pisa a esta utilidad»)
    generaba un selector fantasma y el censo/dueño de esa clase mentía. Pasó de
    verdad el 2026-09-20: un comentario en p1-layout.css hizo que
    .nz-navbar__links apareciera como declarada por dos packs.
    """
    css = COMENTARIO_CSS.sub(" ", css)
    fuera = []
    buf = []
    for ch in css:
        if ch == "{":
            s = "".join(buf).strip()
            if s:
                fuera.append(s)
            buf = []
        elif ch == "}":
            buf = []
        else:
            buf.append(ch)
    return fuera


def selector_externo(css):
    """Compatibilidad: todos los selectores en un solo texto."""
    return "|".join(selectores(css))


CLASE = re.compile(r"\.(nz-[A-Za-z0-9_-]+)")
ATRIBUTO_CLASE = re.compile(r'class="([^"]*)"')


def clases_de_markup(markup):
    """Clases .nz-* realmente aplicadas en un trozo de HTML.

    Ojo: CLASE busca `.nz-x` (sintaxis CSS). En HTML las clases van dentro de
    class="nz-x", sin punto, así que hace falta este segundo lector. Confundir
    los dos hace que el catálogo cuente cero clases usadas.
    """
    vistas = set()
    for valor in ATRIBUTO_CLASE.findall(markup):
        vistas.update(t for t in valor.split() if t.startswith("nz-"))
    vistas.update(CLASE.findall(markup))  # por si el markup cita clases en prosa
    return vistas


def clases_declaradas(path):
    """Clases .nz-* que el pack declara como propias (no contextos del catálogo)."""
    txt = path.read_text(encoding="utf-8", errors="replace")
    propias = set()
    for sel in selectores(txt):
        if "cat-" in sel or "demo-" in sel:
            continue
        for parte in sel.split(","):
            cs = CLASE.findall(parte)
            if not cs:
                continue
            # Declara la clase quien la usa en solitario o junto a clases de su
            # misma familia (.nz-btn.nz-btn--sm). Si el selector mezcla familias
            # (.nz-product .nz-btn) es un AJUSTE contextual de otro pack, no una
            # declaración: así no aparecen duplicados falsos.
            if len({base_de(c) for c in cs}) == 1:
                propias.update(cs)
    return propias


def base_de(clase):
    m = re.match(r"(nz-[A-Za-z0-9]+(?:-[a-z0-9]+)*?)(?:__|--|$)", clase)
    return m.group(1) if m else clase


def _version():
    """La versión vive en components.json (generado). Sin números duplicados."""
    p = ROOT / "components.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8")).get("version", "8.0.0")
        except Exception:
            pass
    return "8.0.0"


VERSION = _version()


def inyecta_packs(html_txt, packs, prefijo):
    """Sustituye el marcador <!--PACKS--> por los packs que la página USA de verdad.

    Se calcula del propio HTML ya construido, así que no hay forma de que una
    página se quede sin el pack que necesita: si una clase aparece, su pack se
    enlaza. Se pasa de cargar los 16 packs (≈310 KB) a cargar solo los usados.
    """
    usadas = clases_de_markup(html_txt)
    necesarios = [p for p in PACKS_COMPONENTES
                  if (PACKS / p).exists() and (packs.get(p, {"clases": set()})["clases"] & usadas)]
    links = "\n".join(f'<link rel="stylesheet" href="{prefijo}{p}">' for p in necesarios)
    return html_txt.replace("<!--PACKS-->", links), necesarios


def censo():
    """Cuenta clases, objetos base y demos. Nada inventado."""
    packs, por_cat = {}, {}
    for i, pack in enumerate(PACKS_COMPONENTES, 1):
        f = PACKS / pack
        if not f.exists():
            continue
        cs = clases_declaradas(f)
        packs[pack] = {"clases": cs, "bases": sorted({base_de(c) for c in cs})}
        por_cat[i] = {"pack": pack, "clases": cs,
                      "bases": sorted({base_de(c) for c in cs})}
    total_clases = sum(len(v["clases"]) for v in packs.values())
    total_bases = len({b for v in packs.values() for b in v["bases"]})
    return packs, por_cat, total_clases, total_bases


def carga_specs():
    specs = []
    for f in sorted(SPECS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        specs.append(d)
    specs.sort(key=lambda d: d["cat"])
    return specs


# ------------------------------------------------------------------
# Página de categoría
# ------------------------------------------------------------------
def pagina(spec, censo_cat, totales, nav, packs):
    n = spec["cat"]
    demos = spec["demos"]
    fichero = spec["fichero"]
    clases_pack = censo_cat.get(n, {}).get("clases", set())
    bases = censo_cat.get(n, {}).get("bases", [])

    # Familias presentes en las demos → chips de filtro
    familias = sorted({base_de(c) for d in demos for c in clases_de_markup(d["markup"])})
    chips = "".join(
        f'\n      <button type="button" class="cat-filters__chip" data-filtro="{html.escape(f)}" '
        f'aria-pressed="false">{html.escape(f.replace("nz-", "."))}</button>'
        for f in familias[:18])

    L = []
    A = L.append
    A("<!DOCTYPE html>")
    A('<html lang="es" data-nz-theme="light">')
    A("<head>")
    A('<meta charset="UTF-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">')
    A(f"<title>Aurora · {n:02d} {html.escape(spec['nombre'])} · {len(clases_pack)} objetos</title>")
    A(f'<meta name="description" content="{html.escape(spec["desc"])}">')
    A('<link rel="stylesheet" href="../tokens.css">')
    A('<link rel="stylesheet" href="../packs/' + PACK_SHELL + '">')
    A("<!--PACKS-->")
    A("</head>")
    A('<body class="nz">')
    A('<a class="nz-skip-link" href="#contenido">Saltar al contenido</a>')
    A('<header class="cat-topbar">')
    A('<a class="cat-brandmark" href="../index.html"><i></i><i></i> Aurora</a>')
    A(f'<span class="cat-count">{n:02d} · {len(clases_pack)} objetos · {len(demos)} demos</span>')
    A('<span class="cat-topbar__tools">')
    A('<a class="cat-icobtn" href="../index.html" title="Portada" aria-label="Volver a la portada">⌂</a>')
    A('<button class="cat-icobtn" id="btnTheme" aria-label="Cambiar tema" title="Light / Dark">◐</button>')
    A("</span>")
    A("</header>")
    A('<nav class="cat-nav-pages" aria-label="Categorías del catálogo">')
    for s in nav:
        cur = ' aria-current="page"' if s["cat"] == n else ""
        A(f'  <a href="{s["fichero"]}"{cur}>{s["cat"]:02d} {html.escape(s["nombre"])}</a>')
    A("</nav>")
    A('<main class="nz-container cat-main" id="contenido">')
    A('  <div class="cat-pagehead">')
    A(f'    <p class="cat-pagehead__over">Categoría {n:02d} de {len(nav)} · {len(clases_pack)} objetos · {len(demos)} demos</p>')
    A(f'    <h1>{html.escape(spec["nombre"])}</h1>')
    A(f'    <p>{html.escape(spec["desc"])}</p>')
    A('    <div class="cat-pagehead__stats">')
    A(f'      <span class="nz-badge nz-badge--brand"><i></i>{len(clases_pack)} objetos</span>')
    A(f'      <span class="nz-badge nz-badge--neutral">{len(bases)} familias</span>')
    A(f'      <span class="nz-badge nz-badge--accent">{len(demos)} demos en vivo</span>')
    A(f'      <span class="nz-badge nz-badge--neutral">{len(familias)} clases distintas usadas</span>')
    A('      <a class="nz-badge nz-badge--brand" href="../packs/{0}">{0}</a>'.format(spec["pack"]))
    A("    </div>")
    A("  </div>")
    A('  <div class="cat-tools">')
    A('    <div class="cat-search">')
    A('      <span class="cat-search__icon" aria-hidden="true">⌕</span>')
    A('      <input class="cat-search__input" id="catBuscar" type="search" '
      'placeholder="Buscar en esta categoría… (pulsa /)" aria-label="Buscar objeto en esta categoría">')
    A(f'      <span class="cat-search__count" id="catContador">{len(demos)} objetos</span>')
    A("    </div>")
    A(f'    <div class="cat-filters" role="group" aria-label="Filtrar por familia de objeto">'
      f'<button type="button" class="cat-filters__chip" data-filtro="todo" aria-pressed="true">Todo</button>{chips}</div>')
    A("  </div>")
    for i, d in enumerate(demos, 1):
        fams = " ".join(sorted({base_de(c) for c in clases_de_markup(d["markup"])}))
        A(f'  <section class="cat-demo cat-in" data-cat="{html.escape(fams)}">')
        A(f'    <div class="cat-demo__title"><span class="cat-demo__num">{i}</span>'
          f'<span class="cat-demo__name">{html.escape(d["titulo"])}</span>'
          f'<span class="cat-demo__tag">{html.escape(d["tag"])}</span></div>')
        A('    <div class="cat-stage">')
        A("      " + d["markup"].replace("\n", "\n      "))
        A("    </div>")
        A("  </section>")
    A('  <div class="cat-empty" id="catVacio" hidden><b>Nada por aquí</b>Prueba con otro término o quita el filtro.</div>')
    A("</main>")
    prev_n = n - 1 if n > 1 else len(nav)
    next_n = n + 1 if n < len(nav) else 1
    pf = next(s["fichero"] for s in nav if s["cat"] == prev_n)
    pn = next(s["nombre"] for s in nav if s["cat"] == prev_n)
    nf = next(s["fichero"] for s in nav if s["cat"] == next_n)
    nn = next(s["nombre"] for s in nav if s["cat"] == next_n)
    A('<div class="cat-nav-pages" style="justify-content:center;border-top:1px solid var(--nz-border-soft)">')
    A(f'  <a href="{pf}">← {prev_n:02d} {html.escape(pn)}</a>')
    A(f'  <a href="{nf}">{next_n:02d} {html.escape(nn)} →</a>')
    A("</div>")
    A('<footer class="cat-footer">')
    A(f'  Aurora · Design System Ntizar · Categoría {n:02d} de {len(nav)} · '
      f'{totales["clases"]} objetos · {totales["demos"]} demos · '
      f'Hecho con ❤️ por David Antizar')
    A("</footer>")
    A('<script src="../js/catalog.js"></script>')
    A("</body>")
    A("</html>")
    html_txt, packs_pagina = inyecta_packs("\n".join(L) + "\n", packs, "../packs/")
    return fichero, html_txt, packs_pagina


# ------------------------------------------------------------------
# Portada
# ------------------------------------------------------------------
PORTADA_JS = """
  /* Constelación: deriva azul + chispas naranjas + explosión al pulsar.
     Canvas = fondo; todo el texto vive en DOM encima. reduced-motion → fotograma estático. */
  (function () {
    var cv = document.getElementById('sky'); if (!cv) return;
    var cx = cv.getContext('2d');
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var W, H, pts = [], parts = [], running = false;
    function palette() {
      return document.documentElement.getAttribute('data-nz-theme') === 'dark'
        ? { dot: '125,165,255', line: '79,142,247', spark: '251,146,60' }
        : { dot: '37,99,235', line: '37,99,235', spark: '249,115,22' };
    }
    function size() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = innerWidth; H = innerHeight;
      cv.width = W * dpr; cv.height = H * dpr;
      cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function seed() {
      pts = [];
      var n = W < 640 ? 42 : 90;
      for (var i = 0; i < n; i++) pts.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
        r: 1.2 + Math.random() * 1.3, a: .18 + Math.random() * .4,
        spark: Math.random() < .08
      });
    }
    function step() {
      cx.clearRect(0, 0, W, H);
      var p = palette(), LINK = 110, i, j, d;
      for (i = 0; i < pts.length; i++) {
        d = pts[i]; d.x += d.vx; d.y += d.vy;
        if (d.x < -10) d.x = W + 10; if (d.x > W + 10) d.x = -10;
        if (d.y < -10) d.y = H + 10; if (d.y > H + 10) d.y = -10;
      }
      cx.lineWidth = 1;
      for (i = 0; i < pts.length; i++) for (j = i + 1; j < pts.length; j++) {
        var dist = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y);
        if (dist < LINK) {
          cx.strokeStyle = 'rgba(' + p.line + ',' + ((1 - dist / LINK) * .16).toFixed(3) + ')';
          cx.beginPath(); cx.moveTo(pts[i].x, pts[i].y); cx.lineTo(pts[j].x, pts[j].y); cx.stroke();
        }
      }
      for (i = 0; i < pts.length; i++) {
        d = pts[i];
        cx.fillStyle = d.spark ? 'rgba(' + p.spark + ',' + (d.a + .2).toFixed(2) + ')' : 'rgba(' + p.dot + ',' + d.a.toFixed(2) + ')';
        cx.beginPath(); cx.arc(d.x, d.y, d.spark ? d.r + .6 : d.r, 0, 6.283); cx.fill();
      }
      for (i = parts.length - 1; i >= 0; i--) {
        var b = parts[i], alive = false;
        for (var k = 0; k < b.length; k++) {
          var q = b[k];
          if (q.life <= 0) continue;
          alive = true;
          q.x += q.vx; q.y += q.vy; q.vy += .12; q.vx *= .985; q.life--;
          cx.fillStyle = 'rgba(' + q.c + ',' + Math.max(q.life / 60, 0).toFixed(2) + ')';
          cx.beginPath(); cx.arc(q.x, q.y, 1.6 + (q.life / 60) * 1.4, 0, 6.283); cx.fill();
        }
        if (!alive) parts.splice(i, 1);
      }
    }
    function loop() { step(); if (running) requestAnimationFrame(loop); }
    size(); seed();
    if (reduce) { step(); return; }
    running = true; requestAnimationFrame(loop);
    document.addEventListener('visibilitychange', function () { running = !document.hidden; if (running) requestAnimationFrame(loop); });
    window.addEventListener('resize', function () { size(); seed(); });
    window.addEventListener('pointerdown', function (e) {
      var p = palette(), ps = [];
      for (var i = 0; i < 18; i++) {
        var ang = Math.random() * 6.283, sp = 1.5 + Math.random() * 3.2;
        ps.push({ x: e.clientX, y: e.clientY, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp - 1, life: 40 + (Math.random() * 25 | 0), c: Math.random() < .3 ? p.spark : p.dot });
      }
      parts.push(ps);
    });
  })();

  /* Buscador global de objetos: carga el índice y ofrece resultados con enlace. */
  (function () {
    var inp = document.getElementById('objBuscar');
    var out = document.getElementById('objResultados');
    if (!inp || !out) return;
    var indice = null, cargando = false;
    function normaliza(t) { return (t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''); }
    function pinta(q) {
      if (!indice) return;
      var nq = normaliza(q);
      var res = indice.filter(function (o) { return !nq || normaliza(o.c).indexOf(nq) !== -1 || normaliza(o.n).indexOf(nq) !== -1; }).slice(0, 60);
      if (!q) { out.innerHTML = ''; out.hidden = true; return; }
      out.hidden = false;
      if (!res.length) { out.innerHTML = '<p class="cat-hint">Ningún objeto coincide con «' + q + '».</p>'; return; }
      var html = res.map(function (o) {
        return '<a class="objr" href="paginas/' + o.f + '#obj"><code>.' + o.c + '</code><span>' + o.n + '</span></a>';
      }).join('');
      out.innerHTML = '<p class="cat-hint">' + res.length + ' de ' + indice.length + ' objetos</p>' + html;
    }
    inp.addEventListener('input', function () {
      var q = inp.value.trim();
      if (!indice && !cargando) {
        cargando = true;
        fetch('datos/objetos.json').then(function (r) { return r.json(); }).then(function (d) {
          indice = d; cargando = false; pinta(inp.value.trim());
        }).catch(function () {
          cargando = false;
          out.hidden = false;
          out.innerHTML = '<p class="cat-hint">Abre el catálogo por HTTP (GitHub Pages) para buscar en los objetos.</p>';
        });
      }
      pinta(q);
    });
  })();

  /* Selector de marca en vivo: cambia --nz-marca-* y todo el sistema se rehace. */
  (function () {
    var raiz = document.documentElement;
    var barra = document.getElementById('marcasBarra');
    var rampa = document.getElementById('marcasRampa');
    if (!barra || !rampa) return;
    function pinta() {
      var cs = getComputedStyle(raiz), html = '';
      [50, 100, 200, 300, 400, 500, 600, 700, 800, 900].forEach(function (i) {
        var c = cs.getPropertyValue('--nz-marca-' + i).trim();
        html += '<span style="background:' + c + ';color:' + (i >= 500 ? '#fff' : '#111827') + '">' + i + '</span>';
      });
      rampa.innerHTML = html;
    }
    function marca(n) {
      raiz.setAttribute('data-nz-marca', n);
      [].forEach.call(barra.querySelectorAll('.cat-marca'), function (o) {
        o.setAttribute('aria-pressed', String(o.getAttribute('data-marca') === n));
      });
      try { localStorage.setItem('nz-marca', n); } catch (e) { /* irrelevante */ }
      pinta();
    }
    barra.addEventListener('click', function (e) {
      var b = e.target.closest('.cat-marca');
      if (b) marca(b.getAttribute('data-marca'));
    });
    try { var g = localStorage.getItem('nz-marca'); if (g) marca(g); } catch (e) { /* irrelevante */ }
    var bt = document.getElementById('btnTheme');
    if (bt) bt.addEventListener('click', function () { setTimeout(pinta, 40); });
    pinta();
  })();
"""


CSS_PORTADA = """
  .objBuscar { position: relative; margin-top: var(--nz-space-6); max-width: 34rem; }
  .objResultados { margin-top: var(--nz-space-3); display: grid; gap: var(--nz-space-1); max-height: 24rem; overflow-y: auto; }
  .objr { display: flex; align-items: center; gap: var(--nz-space-3); min-height: 44px; padding: 0 var(--nz-space-3); border-radius: var(--nz-radius-md); background: var(--nz-surface); box-shadow: var(--nz-shadow-xs); text-decoration: none; color: var(--nz-text); }
  .objr:hover { background: var(--nz-brand-soft); }
  .objr code { font-family: var(--nz-font-mono); font-size: var(--nz-text-xs); color: var(--nz-brand); }
  .objr span { margin-left: auto; font-size: var(--nz-text-xs); color: var(--nz-text-mute); }

  /* --- Portada: showcase del sistema (shell, solo clases .cat-*) --- */
  .cat-h2 { font-size: var(--nz-text-xl); letter-spacing: var(--nz-tracking-tight); margin-bottom: var(--nz-space-3); }
  .cat-p { color: var(--nz-text-soft); max-width: 62ch; margin-bottom: var(--nz-space-4); }
  .cat-marcas { display: flex; flex-wrap: wrap; gap: var(--nz-space-2); margin-bottom: var(--nz-space-4); }
  .cat-marca { min-height: var(--nz-tactil); padding: 0 var(--nz-space-4); display: inline-flex; align-items: center; gap: var(--nz-space-2);
    border: var(--nz-border-w) solid var(--nz-border); border-radius: var(--nz-radius-full); background: var(--nz-surface);
    color: var(--nz-text); font: inherit; font-weight: 600; cursor: pointer; }
  .cat-marca i { width: 14px; height: 14px; border-radius: var(--nz-radius-full); display: inline-block; }
  .cat-marca[aria-pressed="true"] { border-color: var(--nz-brand); box-shadow: var(--nz-focus-ring); }
  .cat-rampa { display: grid; grid-template-columns: repeat(10, 1fr); border-radius: var(--nz-radius-md); overflow: hidden; margin-bottom: var(--nz-space-3); }
  .cat-rampa span { height: 44px; display: grid; place-items: center; font-size: var(--nz-text-2xs); font-family: var(--nz-font-mono); }
  .cat-ideas { display: grid; gap: var(--nz-space-3); grid-template-columns: 1fr; }
  @media (min-width: 640px) { .cat-ideas { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 960px) { .cat-ideas { grid-template-columns: repeat(4, 1fr); } }
  .cat-idea { display: grid; gap: var(--nz-space-1); padding: var(--nz-space-4); border: var(--nz-border-w) solid var(--nz-border);
    border-radius: var(--nz-radius-lg); background: var(--nz-surface); box-shadow: var(--nz-shadow-xs); text-decoration: none; color: var(--nz-text); }
  .cat-idea:hover { border-color: var(--nz-brand); }
  .cat-idea b { font-size: var(--nz-text-base); }
  .cat-idea span { font-size: var(--nz-text-sm); color: var(--nz-text-soft); }
  .cat-muestra { display: grid; gap: var(--nz-space-4); grid-template-columns: 1fr; }
  @media (min-width: 960px) { .cat-muestra { grid-template-columns: repeat(3, 1fr); align-items: start; } }
  .cat-muestra__col { display: grid; gap: var(--nz-space-2); align-content: start; }
  .cat-muestra__t { font-size: var(--nz-text-2xs); font-weight: 800; letter-spacing: var(--nz-tracking-caps); text-transform: uppercase; color: var(--nz-text-faint); }
"""


def portada(specs, censo_cat, totales, packs):
    filas = []
    for s in specs:
        n = s["cat"]
        cc = censo_cat.get(n, {"clases": set(), "bases": []})
        wide = " cat-cat--wide" if n in (1, 5, 13) else ""
        filas.append(
            f'        <a class="cat-cat{wide} cat-in" href="paginas/{s["fichero"]}">\n'
            f'          <span class="cat-cat__n">{n:02d}</span>\n'
            f'          <span class="cat-cat__name">{html.escape(s["nombre"])}</span>\n'
            f'          <span class="cat-cat__meta">{len(cc["clases"])} objetos · {len(s["demos"])} demos</span>\n'
            f'          <span class="cat-cat__arrow">→</span>\n'
            f'        </a>')
    t = totales
    html_txt = f"""<!DOCTYPE html>
<html lang="es" data-nz-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Aurora · Design System Ntizar · {t['clases']} objetos de frontend</title>
<meta name="description" content="Design system CSS de Ntizar: {t['clases']} objetos en {t['categorias']} categorías. Sólido, mobile-first, táctil 44px, light y dark. Sin gradientes, sin glass.">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="packs/{PACK_SHELL}">
<!--PACKS-->
<link rel="stylesheet" href="marcas/aurora.css">
<link rel="stylesheet" href="marcas/indigo.css">
<link rel="stylesheet" href="marcas/esmeralda.css">
<link rel="stylesheet" href="marcas/violeta.css">
<link rel="stylesheet" href="marcas/carmesi.css">
<style>{CSS_PORTADA}</style>
</head>
<body class="nz">

<canvas id="sky" class="cat-sky" aria-hidden="true"></canvas>

<div class="cat-above">

  <a class="nz-skip-link" href="#contenido">Saltar al contenido</a>

  <header class="cat-topbar">
    <span class="cat-brandmark"><i></i><i></i> Aurora</span>
    <span class="cat-count">v{VERSION} · motor de temas</span>
    <span class="cat-topbar__tools">
      <a class="cat-icobtn" href="audit/index.html" title="Auditoría del sistema" aria-label="Auditoría del sistema">✓</a>
      <button class="cat-icobtn" id="btnTheme" aria-label="Cambiar tema" title="Light / Dark">◐</button>
    </span>
  </header>

  <section class="cat-hero cat-in">
    <p class="cat-eyebrow">Design System Ntizar</p>
    <h1>Aurora</h1>
    <p class="cat-hero__sub">{t['clases']} objetos de frontend para montar cualquier web. Elige dos colores y el sistema entero se rehace. Sólido y con sombras de verdad: sin gradientes, sin glass, sin IA-slop. Mobile-first de verdad.</p>
    <div class="cat-ctas">
      <a class="nz-btn nz-btn--primary" href="recetas/index.html">Ver las recetas</a>
      <a class="nz-btn nz-btn--soft" href="paginas/01-layout.html">Explorar el catálogo</a>
      <a class="nz-btn nz-btn--ghost" href="COMPOSICION.md">Contrato de composición</a>
      <span class="cat-hint">psst… pulsa en cualquier parte para las chispas</span>
    </div>
    <div class="objBuscar">
      <div class="cat-search">
        <span class="cat-search__icon" aria-hidden="true">⌕</span>
        <input class="cat-search__input" id="objBuscar" type="search" placeholder="Buscar un objeto: btn, modal, chart… (pulsa /)" aria-label="Buscar objeto en todo el sistema">
      </div>
      <div class="objResultados" id="objResultados" hidden></div>
    </div>
    <div class="cat-stats">
      <div class="cat-stat"><b><span data-cuenta="{t['clases']}">0</span></b><span>objetos</span></div>
      <div class="cat-stat"><b>{t['categorias']}</b><span>categorías</span></div>
      <div class="cat-stat"><b>{t['demos']}</b><span>demos en vivo</span></div>
      <div class="cat-stat"><b><span data-cuenta="{t['bases']}">0</span></b><span>familias</span></div>
      <div class="cat-stat"><b>2</b><span>temas</span></div>
      <div class="cat-stat"><b>0</b><span>gradientes</span></div>
      <div class="cat-stat"><b>0</b><span>glass</span></div>
    </div>
  </section>

  <main id="contenido" style="max-width:var(--nz-container-max);margin-inline:auto;padding:0 var(--nz-gutter)">

    <section class="cat-in" style="--d:.06s;margin-block:var(--nz-space-12)">
      <h2 style="font-size:var(--nz-text-xl);letter-spacing:var(--nz-tracking-tight);margin-bottom:var(--nz-space-4)">Manifiesto</h2>
      <div class="cat-pillrow">
        <span class="cat-pill"><i></i> Mobile first</span>
        <span class="cat-pill"><i></i> Azul #2563eb</span>
        <span class="cat-pill"><i></i> Naranja #f97316</span>
        <span class="cat-pill"><i></i> Sombras multicapa</span>
        <span class="cat-pill"><i></i> expo-out ≤ 300 ms</span>
        <span class="cat-pill"><i></i> Táctil 44 px</span>
        <span class="cat-pill"><i></i> Safe-area iOS</span>
        <span class="cat-pill"><i></i> Light + dark</span>
        <span class="cat-pill"><i></i> Cero JS obligatorio</span>
        <span class="cat-pill cat-pill--no"><i></i> Sin gradientes</span>
        <span class="cat-pill cat-pill--no"><i></i> Sin glass</span>
        <span class="cat-pill cat-pill--no"><i></i> Sin IA-slop</span>
      </div>
    </section>

    <section class="cat-in" style="--d:.05s;margin-block:var(--nz-space-12)">
      <h2 class="cat-h2">Tu marca, en una línea</h2>
      <p class="cat-p">Elige el color del proyecto y el sistema entero se rehace: botones, foco, sombras, fondos suaves y modo oscuro. Pruébalo aquí mismo.</p>
      <div class="cat-marcas" id="marcasBarra">
        <button class="cat-marca" data-marca="aurora" aria-pressed="true"><i style="background:#2563eb"></i>Aurora</button>
        <button class="cat-marca" data-marca="indigo" aria-pressed="false"><i style="background:#4f46e5"></i>Índigo</button>
        <button class="cat-marca" data-marca="esmeralda" aria-pressed="false"><i style="background:#00875e"></i>Esmeralda</button>
        <button class="cat-marca" data-marca="violeta" aria-pressed="false"><i style="background:#7c3aed"></i>Violeta</button>
        <button class="cat-marca" data-marca="carmesi" aria-pressed="false"><i style="background:#dc2626"></i>Carmesí</button>
      </div>
      <div class="cat-rampa" id="marcasRampa" aria-hidden="true"></div>
      <p class="cat-hint">Se activa con <code>data-nz-marca</code> en el <code>&lt;html&gt;</code>. Comparador completo en <a class="nz-link" href="marcas/index.html">marcas</a> · tu marca desde dos hex: <code>python scripts/generar-marca.py miweb "#0ea5e9" "#f43f5e"</code></p>
    </section>

    <section class="cat-in" style="--d:.07s;margin-block:var(--nz-space-12)">
      <h2 class="cat-h2">El sistema, en cuatro ideas</h2>
      <div class="cat-ideas">
        <a class="cat-idea" href="marcas/index.html"><b>Motor de temas</b><span>Dos colores y cambia todo. Cinco marcas listas y generador OKLCH con contraste AA.</span></a>
        <a class="cat-idea" href="COMPOSICION.md"><b>Contrato de composición</b><span>Doce leyes: cero emojis, presupuesto de color, ancho por tipo de página.</span></a>
        <a class="cat-idea" href="recetas/index.html"><b>Recetas canónicas</b><span>Admin, dashboard, ajustes, acceso e informe. Cópialas y adapta.</span></a>
        <a class="cat-idea" href="audit/index.html"><b>Arnés de verificación</b><span>El lint caza emojis, jerarquía, presupuesto de color y tipografía mínima.</span></a>
      </div>
    </section>

    <section class="cat-in" style="--d:.08s;margin-block:var(--nz-space-12)">
      <h2 class="cat-h2">Muestra viva</h2>
      <div class="cat-muestra">
        <div class="nz-kpi nz-kpi--brand">
          <span class="nz-kpi__label">Usuarios activos</span>
          <span class="nz-kpi__value">1 284</span>
          <span class="nz-kpi__delta nz-kpi__delta--up">+6,2 % este mes</span>
        </div>
        <div class="cat-muestra__col">
          <span class="cat-muestra__t">Acciones</span>
          <div class="nz-cluster">
            <button class="nz-btn nz-btn--primary" type="button">Guardar</button>
            <button class="nz-btn nz-btn--soft" type="button">Suave</button>
            <button class="nz-btn nz-btn--outline" type="button">Borde</button>
          </div>
          <span class="cat-muestra__t">Estados</span>
          <div class="nz-cluster">
            <span class="nz-badge nz-badge--brand">Nuevo</span>
            <span class="nz-badge nz-badge--success">Correcto</span>
            <span class="nz-badge nz-badge--warning">Pendiente</span>
          </div>
          <span class="cat-muestra__t">Formulario</span>
          <div class="nz-field">
            <label class="nz-field__label" for="muestraCorreo">Correo</label>
            <input class="nz-input" id="muestraCorreo" type="email" placeholder="tu@correo.com">
            <span class="nz-field__help">La etiqueta siempre visible; el recuadro de ejemplo no sustituye al nombre.</span>
          </div>
        </div>
        <div class="cat-muestra__col">
          <span class="cat-muestra__t">Aviso</span>
          <div class="nz-alert nz-alert--info" role="status">
            <div class="nz-alert__body"><p class="nz-alert__msg">Los colores de este aviso también salen de la marca que elijas arriba.</p></div>
          </div>
          <span class="cat-muestra__t">Iconos (no emojis)</span>
          <div class="nz-cluster">
            <svg class="nz-icon nz-icon--lg nz-icon--brand" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
            <svg class="nz-icon nz-icon--lg" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
            <svg class="nz-icon nz-icon--lg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/></svg>
            <svg class="nz-icon nz-icon--lg" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>
          </div>
          <span class="cat-muestra__t">Un objeto del catálogo</span>
          <div class="nz-progress"><div class="nz-progress__bar" style="width:76%"></div></div>
        </div>
      </div>
    </section>

    <section class="cat-in" style="--d:.09s;margin-block:var(--nz-space-12)">
      <h2 class="cat-h2">Recetas canónicas</h2>
      <p class="cat-p">Cada tipo de página tiene una forma correcta, y está escrita: cero emojis, presupuesto de color y ancho adecuado.</p>
      <div class="cat-ideas">
        <a class="cat-idea" href="recetas/admin.html"><b>Admin</b><span>Barra lateral, KPIs y tabla ancha con estados.</span></a>
        <a class="cat-idea" href="recetas/dashboard.html"><b>Dashboard</b><span>Indicadores, gráficos CSS y los tres estados.</span></a>
        <a class="cat-idea" href="recetas/ajustes.html"><b>Ajustes</b><span>Secciones y formularios con etiquetas visibles.</span></a>
        <a class="cat-idea" href="recetas/login.html"><b>Acceso</b><span>Tarjeta centrada, un CTA y el error donde se mira.</span></a>
        <a class="cat-idea" href="recetas/informe.html"><b>Informe</b><span>Prosa a una columna y tablas anchas.</span></a>
      </div>
    </section>

    <section class="cat-in" style="--d:.1s;margin-block:var(--nz-space-12)">
      <h2 style="font-size:var(--nz-text-xl);letter-spacing:var(--nz-tracking-tight)">{t['categorias']} categorías · {t['clases']} objetos</h2>
      <div class="cat-grid" style="margin-top:var(--nz-space-4)">
{chr(10).join(filas)}
      </div>
    </section>

    <section class="cat-in" style="--d:.14s;margin-block:var(--nz-space-12)">
      <h2 style="font-size:var(--nz-text-xl);letter-spacing:var(--nz-tracking-tight);margin-bottom:var(--nz-space-4)">Señales de vida</h2>
      <div class="cat-livegrid">
        <div class="cat-live-card">
          <h3>Botón que cicla</h3>
          <div class="cat-live-slot"><button class="nz-btn nz-btn--primary" id="liveSave">Guardar cambios</button></div>
        </div>
        <div class="cat-live-card">
          <h3>Interruptor</h3>
          <div class="cat-live-slot"><label class="nz-switch"><input type="checkbox" checked><span class="nz-switch__track"><span class="nz-switch__thumb"></span></span><span class="nz-switch__label">Activo</span></label></div>
        </div>
        <div class="cat-live-card">
          <h3>Progreso</h3>
          <div class="cat-live-slot"><div class="nz-progress" style="width:100%"><div class="nz-progress__bar" id="liveProg" style="width:76%"></div></div></div>
        </div>
        <div class="cat-live-card">
          <h3>Cuenta atrás</h3>
          <div class="cat-live-slot"><span class="nz-num nz-num--stat" data-cuenta="{t['clases']}">0</span></div>
        </div>
      </div>
    </section>

  </main>

  <footer class="cat-footer">
    Aurora · Hecho con ❤️ por David Antizar · {t['clases']} objetos, {t['demos']} demos, 1 sistema
  </footer>

</div>

<script src="js/catalog.js"></script>
<script>{PORTADA_JS}</script>
</body>
</html>
"""
    html_txt, packs_portada = inyecta_packs(html_txt, packs, "packs/")
    print("portada: carga", ", ".join(packs_portada))
    return html_txt


# ------------------------------------------------------------------
def main():
    specs = carga_specs()
    packs, censo_cat, total_clases, total_bases = censo()
    total_demos = sum(len(s["demos"]) for s in specs)
    totales = {"clases": total_clases, "bases": total_bases,
               "demos": total_demos, "categorias": len(specs)}

    nav = [{"cat": s["cat"], "nombre": s["nombre"], "fichero": s["fichero"]} for s in specs]

    PAGINAS.mkdir(exist_ok=True)
    for s in specs:
        fichero, contenido, packs_pagina = pagina(s, censo_cat, totales, nav, packs)
        (PAGINAS / fichero).write_text(contenido, encoding="utf-8")
        cc = censo_cat.get(s["cat"], {"clases": set()})
        print(f"paginas/{fichero:<22} {len(cc['clases']):>3} objetos · {len(s['demos']):>3} demos"
              f" · {len(packs_pagina)} packs")

    # bundle para consumidores
    imp = "\n".join(f'@import url("{p}");' for p in PACKS_COMPONENTES if (PACKS / p).exists())
    (PACKS / "all.css").write_text(
        "/* Aurora — todos los packs en un solo enlace.\n"
        "   Para producción se recomienda enlazar solo los packs que uses.\n"
        "   Orden: components primero, shell del catálogo al final (no necesario fuera del catálogo). */\n"
        '/* No incluye p0-catalog.css: ese es el shell del catálogo, no del sistema. */\n'
        + imp + "\n", encoding="utf-8")

    (ROOT / "index.html").write_text(portada(specs, censo_cat, totales, packs), encoding="utf-8")

    # índice de objetos para el buscador global
    DATOS.mkdir(exist_ok=True)
    indice = []
    for s in specs:
        for c in sorted(censo_cat.get(s["cat"], {"clases": set()})["clases"]):
            indice.append({"c": c, "n": s["nombre"], "f": s["fichero"]})
    (DATOS / "objetos.json").write_text(
        json.dumps(indice, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    print(f"\nTOTAL: {total_clases} objetos · {total_bases} familias · {total_demos} demos · "
          f"{len(specs)} categorías")
    print(f"index.html regenerado · datos/objetos.json ({len(indice)} objetos) · packs/all.css")


if __name__ == "__main__":
    main()
