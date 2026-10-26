#!/usr/bin/env python3
"""Pruebas de producto de Aurora en navegador real (plan §15 y §12.3).

Sondea las páginas de referencia servidas por HTTP local con Chrome headless y
mide el resultado RENDERIZADO, no el texto del HTML (auditoría A05/A10):

  A09/B02  dos marcas → colores computados distintos (--nz-marca-600),
           y la marca solicitada resuelve en la página generada
  B05      política de firma data-nz-firma: none → 0, subtle → 1, full → 1
  A02/B03  la marca de la ficha enlaza al inicio bajo subruta y ese destino
           responde con la landing (recorrido real: ficha → inicio)
           y el CTA de la landing apunta a la ficha
  A10      sin overflow horizontal del documento en 390 / 768 / 1440 (light)
           y en oscuro a 1440
  A05      jerarquía computada: el h1 mide más que el cuerpo y la entradilla
           no se come al título

Uso:
  python scripts/probar-producto.py [--navegador RUTA] [--presupuesto MS]

Sale con código != 0 si alguna comprobación falla. Las comprobaciones que NO
se ejecutan se listan al final como PENDIENTES (plan §12.4: una medición no
ejecutada nunca se da por aprobada).
"""
import argparse
import functools
import http.server
import json
import pathlib
import re
import subprocess
import sys
import threading
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import hornear  # noqa: E402  (NAVEGADORES, navegador(), servir(), puerto_libre())

SONDA = """<!doctype html><html lang=es><head><meta charset=utf-8>
<title>Sonda de producto · Aurora</title>
<style>
 body{font:14px system-ui;margin:0;background:#111;color:#eee}
 iframe{border:0;display:block}
 #sonda{white-space:pre-wrap;font:12px ui-monospace,monospace;color:#9f9}
</style></head><body>
<iframe id=m></iframe><pre id=sonda>esperando…</pre>
<script>
const q = new URLSearchParams(location.search);
const ifr = document.getElementById('m');
ifr.style.width = (parseInt(q.get('ancho') || '1440', 10)) + 'px';
ifr.style.height = (parseInt(q.get('alto') || '1000', 10)) + 'px';
ifr.src = q.get('pagina');
ifr.addEventListener('load', () => {
  try {
    const d = ifr.contentDocument, w = ifr.contentWindow;
    if (!d) throw new Error('iframe cross-origin');
    const tema = q.get('tema');
    if (tema) d.documentElement.setAttribute('data-nz-theme', tema);
    const h1 = d.querySelector('h1');
    const entr = d.querySelector('.nz-lead, .nz-entradilla, .nz-desc');
    const brand = d.querySelector('.nz-navbar__brand');
    const cta = d.querySelector('main a.nz-btn--primary, main.nz-btn--primary');
    const cuerpo = d.querySelector('main p:not(.nz-lead):not(.nz-entradilla):not(.nz-desc)');
    const gcs = el => el ? parseFloat(w.getComputedStyle(el).fontSize) : null;
    const res = {
      pagina: d.title,
      marca600: w.getComputedStyle(d.documentElement).getPropertyValue('--nz-marca-600').trim(),
      marcaAttr: d.documentElement.getAttribute('data-nz-marca'),
      firma: (d.body.innerText.match(/Hecho con ❤️ por David Antizar/g) || []).length,
      h1: h1 ? { px: gcs(h1), txt: h1.innerText.slice(0, 70) } : null,
      entradillaPx: gcs(entr),
      cuerpoPx: gcs(cuerpo),
      brand: brand ? { esEnlace: brand.tagName === 'A',
                       href: brand.getAttribute('href'),
                       absoluto: brand.href } : null,
      ctaDetalle: cta ? { href: cta.getAttribute('href'),
                          absoluto: cta.href } : null,
      overflow: { scroll: d.documentElement.scrollWidth,
                  client: d.documentElement.clientWidth },
      tema: d.documentElement.getAttribute('data-nz-theme'),
      estilo: d.documentElement.getAttribute('data-nz-estilo'),
      fondo: w.getComputedStyle(d.body).backgroundColor
    };
    document.getElementById('sonda').textContent = JSON.stringify(res);
    window.__lista = true;
  } catch (e) {
    document.getElementById('sonda').textContent = JSON.stringify({ error: String(e) });
  }
});
</script></body></html>"""


def chrome(nav, url, presupuesto, ancho=1500, alto=1100):
    cmd = [nav, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--window-size=%d,%d" % (ancho, alto),
           "--virtual-time-budget=%d" % presupuesto, "--dump-dom", url]
    out = subprocess.run(cmd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if not out.stdout:
        raise SystemExit("Chrome no devolvió DOM:\n" + (out.stderr or "")[:600])
    return out.stdout


def medir(nav, puerto, pagina, presupuesto, ancho=1440, alto=1000, tema=None):
    q = "pagina=%s&ancho=%d&alto=%d" % (pagina, ancho, alto)
    if tema:
        q += "&tema=" + tema
    dom = chrome(nav, "http://127.0.0.1:%d/audit/_sonda.html?%s" % (puerto, q),
                 presupuesto, ancho=ancho + 100, alto=alto + 140)
    m = re.search(r'<pre id="sonda">(.*?)</pre>', dom, re.S)
    if not m:
        raise SystemExit("La sonda no devolvió resultados")
    texto = m.group(1)
    texto = (texto.replace("&lt;", "<").replace("&gt;", ">")
                  .replace("&quot;", '"').replace("&amp;", "&"))
    return json.loads(texto)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--navegador")
    ap.add_argument("--presupuesto", type=int, default=7000)
    ns = ap.parse_args()
    nav = hornear.navegador(ns.navegador)

    # --- páginas de prueba de marca y firma (auditoría A09/B05) -------------
    audit = ROOT / "audit"
    audit.mkdir(exist_ok=True)
    (audit / "_sonda.html").write_text(SONDA, encoding="utf-8")
    temporales = [
        # (salida, args)
        ("_prod-landing-aurora.html", ["--marca", "aurora", "--firma", "full"]),
        ("_prod-detalle-none.html",   ["--marca", "ntizar", "--firma", "none"]),
        ("_prod-detalle-subtle.html", ["--marca", "ntizar", "--firma", "subtle"]),
    ]
    programa = {
        "landing": ROOT / "examples/golden/landing.openui",
        "detalle": ROOT / "examples/golden/detalle.openui",
    }
    orig = {"_prod-landing-aurora.html": programa["landing"],
            "_prod-detalle-none.html": programa["detalle"],
            "_prod-detalle-subtle.html": programa["detalle"]}
    for salida, args in temporales:
        cmd = [sys.executable, str(ROOT / "scripts/programa-a-html.py"),
               str(orig[salida]), "--salida", str(audit / salida)] + args
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(r.stdout + r.stderr)

    puerto = hornear.puerto_libre()
    httpd = hornear.servir(ROOT, puerto)
    base = "http://127.0.0.1:%d" % puerto
    ok, ko, pend = [], [], []

    def check(nombre, cond, detalle):
        (ok if cond else ko).append("%s — %s" % (nombre, detalle))
        print(("  ✓ " if cond else "  ✗ ") + nombre + ": " + detalle)

    try:
        # --- A09/B02 · estilos computados de marca --------------------------
        print("\n· Marca computada (A09/B02)")
        g = lambda p, **k: medir(nav, puerto, p, ns.presupuesto, **k)
        aur = g("/audit/_prod-landing-aurora.html")
        nti = g("/examples/golden/index.html")
        check("dos marcas → colores distintos",
              aur["marca600"] and nti["marca600"] and aur["marca600"] != nti["marca600"],
              "--nz-marca-600 aurora=%s vs ntizar=%s" % (aur["marca600"], nti["marca600"]))
        check("atributo declarado coincide",
              aur["marcaAttr"] == "aurora" and nti["marcaAttr"] == "ntizar",
              "aurora='%s' · ntizar='%s'" % (aur["marcaAttr"], nti["marcaAttr"]))

        # --- B05 · política de firma ----------------------------------------
        print("\n· Política de firma (B05/A08)")
        none = g("/audit/_prod-detalle-none.html")
        subtle = g("/audit/_prod-detalle-subtle.html")
        full = g("/examples/golden/detalle.html")
        check("none → 0 firmas", none["firma"] == 0, "encontradas=%d" % none["firma"])
        check("subtle → exactamente 1", subtle["firma"] == 1, "encontradas=%d" % subtle["firma"])
        check("full → exactamente 1", full["firma"] == 1, "encontradas=%d" % full["firma"])

        # --- A02/B03 · navegación bajo subruta ------------------------------
        print("\n· Navegación bajo subruta (A02/B03)")
        det = g("/examples/golden/detalle.html")
        b = det["brand"] or {}
        esperado_fin = "/examples/golden/index.html"
        check("la marca es enlace", b.get("esEnlace") is True,
              "etiqueta=%s" % ("A" if b.get("esEnlace") else "?"))
        check("marca → inicio del producto",
              (b.get("absoluto") or "").endswith(esperado_fin),
              "resuelve a %s" % b.get("absoluto"))
        # el destino responde y es la landing (recorrido real ficha → inicio)
        html = urllib.request.urlopen(base + esperado_fin, timeout=10).read().decode("utf-8")
        check("el destino responde con la landing",
              "Un tablero para tus encargos" in html, "HTTP 200 con h1 de la landing")
        land = g("/examples/golden/index.html")
        c = land["ctaDetalle"] or {}
        check("CTA landing → ficha",
              (c.get("absoluto") or "").endswith("/examples/golden/detalle.html"),
              "resuelve a %s" % c.get("absoluto"))
        html2 = urllib.request.urlopen(base + "/examples/golden/detalle.html", timeout=10).read().decode("utf-8")
        check("la ficha responde", "EN-2291" in html2, "HTTP 200 con la ficha EN-2291")

        # --- A10 · overflow responsive --------------------------------------
        print("\n· Overflow responsive (A10)")
        for ancho in (390, 768, 1440):
            r = g("/examples/golden/index.html", ancho=ancho, alto=900)
            ov = r["overflow"]
            check("landing a %dpx sin overflow" % ancho,
                  ov["scroll"] <= ov["client"],
                  "scrollWidth=%d clientWidth=%d" % (ov["scroll"], ov["client"]))
        r = g("/examples/golden/detalle.html", ancho=390, alto=900)
        ov = r["overflow"]
        check("ficha a 390px sin overflow", ov["scroll"] <= ov["client"],
              "scrollWidth=%d clientWidth=%d" % (ov["scroll"], ov["client"]))
        r = g("/examples/golden/detalle.html", ancho=1440, alto=900, tema="dark")
        ov = r["overflow"]
        check("ficha 1440px oscuro sin overflow", ov["scroll"] <= ov["client"],
              "scrollWidth=%d clientWidth=%d · fondo=%s" % (ov["scroll"], ov["client"], r["fondo"]))
        check("tema oscuro aplicado", r["tema"] == "dark", "data-nz-theme=%s" % r["tema"])

        # --- A05 · jerarquía tipográfica computada --------------------------
        print("\n· Jerarquía tipográfica computada (A05)")
        j = land
        h1px, entrpx, cuerpox = j["h1"]["px"], j["entradillaPx"], j["cuerpoPx"]
        check("h1 > entradilla ≥ cuerpo",
              h1px > entrpx >= cuerpox,
              "h1=%s entradilla=%s cuerpo=%s" % (h1px, entrpx, cuerpox))
        check("h1 con tamaño de página (≥24px)", h1px >= 24, "h1=%spx" % h1px)

        # --- pendientes honestos (plan §12.4) -------------------------------
        pend = [
            "zoom 200% y texto ampliado en recorridos (§12.3)",
            "foco visible y recorrido completo por teclado (§12.3, Entrega 3)",
            "cristal con prefers-reduced-transparency medido en navegador (B07: "
            "el CSS de fallback está escrito y validado sintácticamente, no medido aún)",
            "casos dirigidos de contenido vacío/largo/error (§12.3)",
        ]
    finally:
        httpd.shutdown()
        # proyecto limpio: los temporales de medición no se quedan en audit/
        for _salida, _ in temporales:
            (audit / _salida).unlink(missing_ok=True)
        (audit / "_sonda.html").unlink(missing_ok=True)

    print("\n=== RECORRIDO DE PRODUCTO ===")
    print("  comprobaciones ejecutadas: %d" % (len(ok) + len(ko)))
    print("  superadas: %d · fallidas: %d" % (len(ok), len(ko)))
    if pend:
        print("  pendientes (no ejecutados, no aprobados):")
        for p in pend:
            print("    - " + p)
    if ko:
        print("\nFALLOS:")
        for k in ko:
            print("  ✗ " + k)
        sys.exit(1)
    print("\nRESULTADO: VÁLIDO — producto medido en navegador real ✅")


if __name__ == "__main__":
    main()
