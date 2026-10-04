# -*- coding: utf-8 -*-
"""Auditoria movil REAL de Aurora: navegador headless, no lint.

Para cada pagina del catalogo y cada viewport movil (320/360/390):
  1. Overflow horizontal de la pagina: scrollingElement.scrollWidth vs clientWidth.
  2. Elementos que se salen del viewport, EXCLUYENDO lo legal:
     - descendientes de un contenedor con overflow-x auto/scroll (scroll legal),
     - elementos invisibles (display none, visibility hidden).
     Se marca aparte lo que un ancestor recorta con overflow-x hidden (dato perdido).
  3. Tactil 44px: todo lo clicable en movil mide >= 44x44 (regla 6). Los enlaces
     de texto dentro de prosa se listan aparte (criterio distinto).

Uso:
    uv run --with playwright python scripts/auditar-movil.py
Salida:
    audit/movil.json  (datos crudos)
    audit/MOVIL.md    (informe navegable)
"""
import json
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGINAS = sorted((ROOT / "paginas").glob("*.html"))
VIEWPORTS = [320, 360, 390]

JS_AUDIT = r"""
() => {
  const se = document.scrollingElement;
  const vw = window.innerWidth;
  const dentroScrollLegal = (el) => {
    let a = el.parentElement;
    while (a && a !== document.body) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') return true;
      a = a.parentElement;
    }
    return false;
  };
  const clipadoPor = (el) => {
    let a = el.parentElement;
    while (a && a !== document.body) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'hidden' || cs.overflowX === 'clip') return true;
      a = a.parentElement;
    }
    return false;
  };
  const invisible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return true;
    const rc = el.getBoundingClientRect();
    return rc.width === 0 && rc.height === 0;
  };
  const primeraClase = (el) => (String(el.classList[0] || el.tagName.toLowerCase()));
  const fuera = [], clipados = [];
  for (const el of document.querySelectorAll('body *')) {
    if (el === se || el === document.body) continue;
    if (invisible(el)) continue;
    const rc = el.getBoundingClientRect();
    if (rc.right > vw + 0.5 || rc.left < -0.5) {
      if (dentroScrollLegal(el)) continue;
      const dato = { clase: primeraClase(el), exceso: Math.round(Math.max(rc.right - vw, -rc.left)) };
      if (clipadoPor(el)) clipados.push(dato); else fuera.push(dato);
    }
  }
  // Tactil: todo lo clicable en movil
  const clickables = document.querySelectorAll('a,button,[role="button"],input,select,textarea,summary,[onclick]');
  const peq = [], enlacesTexto = [];
  let nClick = 0;
  for (const el of clickables) {
    if (invisible(el)) continue;
    const rc = el.getBoundingClientRect();
    // objetivos sr-only de 1x1: no son interaccion visible
    if (rc.width <= 8 && rc.height <= 8) continue;
    // el patron del sistema: boton diminuto con ::after que extiende el area de impacto
    const after = getComputedStyle(el, '::after');
    if (after.content !== 'none' && after.position === 'absolute') continue;
    nClick++;
    if (rc.height >= 43.5 && rc.width >= 43.5) continue;
    const enProsa = !!el.closest('p, li, .nz-prose, .nz-msg__bubble, td');
    const dato = {
      clase: primeraClase(el),
      w: Math.round(rc.width), h: Math.round(rc.height),
      texto: (el.textContent || el.value || '').trim().slice(0, 24),
    };
    if (enProsa || el.matches('a.nz-badge, a.nz-link')) enlacesTexto.push(dato); else peq.push(dato);
  }
  return {
    scrollW: se.scrollWidth, clientW: se.clientWidth, vw,
    fuera: fuera.slice(0, 60), nFuera: fuera.length,
    clipados: clipados.slice(0, 30), nClipados: clipados.length,
    tactil: { nClick, nPeq: peq.length, peq: peq.slice(0, 40), nTexto: enlacesTexto.length },
  };
}
"""


def agrupar(items, clave):
    g = {}
    for it in items:
        k = it[clave]
        g[k] = g.get(k, 0) + 1
    return sorted(g.items(), key=lambda x: -x[1])


def main():
    resultados = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        for ancho in VIEWPORTS:
            ctx = navegador.new_context(
                viewport={"width": ancho, "height": 800},
                device_scale_factor=2, is_mobile=True, has_touch=True,
            )
            pagina = ctx.new_page()
            for pag in PAGINAS:
                pagina.goto(f"file:///{pag.as_posix()}")
                pagina.wait_for_load_state("load")
                # congelar animaciones/transiciones: medir estado final, no un fotograma al azar
                pagina.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; }")
                datos = pagina.evaluate(JS_AUDIT)
                # las demos ocultas por el buscador no existen al medir; el DOM es el mismo
                resultados.setdefault(pag.name, {})[ancho] = datos
            ctx.close()
        navegador.close()

    (ROOT / "audit" / "movil.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")

    # Informe
    lineas = ["# Auditoría móvil — Aurora", "",
              f"Fecha: {date.today().isoformat()} · Navegador real headless · Viewports: {', '.join(map(str, VIEWPORTS))}", ""]
    fallos = 0
    for pag, por_vp in resultados.items():
        problemas = []
        for vp, d in por_vp.items():
            if d["scrollW"] > d["clientW"]:
                problemas.append(f"**{vp}px**: página desborda ({d['scrollW']}>{d['clientW']}) — {agrupar(d['fuera'], 'clase')}")
            if d["nClipados"]:
                problemas.append(f"**{vp}px**: {d['nClipados']} elemento(s) recortados por overflow hidden — {agrupar(d['clipados'], 'clase')}")
            t = d["tactil"]
            if t["nPeq"]:
                problemas.append(f"**{vp}px**: {t['nPeq']}/{t['nClick']} clicables <44px — {agrupar(t['peq'], 'clase')}")
        if problemas:
            fallos += len(problemas)
            lineas += [f"## {pag}", ""] + [f"- {x}" for x in problemas] + [""]
        else:
            lineas += [f"## {pag}", "- ✅ limpia en los 3 viewports", ""]
    lineas += ["", f"**Problemas totales: {fallos}**"]
    (ROOT / "audit" / "MOVIL.md").write_text("\n".join(lineas), encoding="utf-8")

    # Resumen consola
    for pag, por_vp in resultados.items():
        malos = sum(1 for d in por_vp.values() if d["scrollW"] > d["clientW"] or d["nClipados"] or d["tactil"]["nPeq"])
        print(f"{'✗' if malos else '✓'} {pag}: " + ", ".join(
            f"{vp}:{d['scrollW']}x{d['clientW']} fuera={d['nFuera']} clip={d['nClipados']} peq44={d['tactil']['nPeq']}"
            for vp, d in por_vp.items()))
    print(f"\nProblemas: {fallos} → audit/MOVIL.md")


if __name__ == "__main__":
    main()
