#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera datos/base-diseno.json — la base de datos de diseño consultable de Aurora.

No inventa nada: indexa lo que ya existe y lo enriquece con metadatos derivados.

Fuentes (todas dentro del repo):
  · components.json      → familias, clases, tokens, markup, anti-patrones, alias, combos
  · specs/*.json         → categorías y demos
  · bloques/recetas/*.html       → páginas canónicas completas
  · bloques/ejemplos/*.html      → recetas mínimas de arranque
  · bloques/combos/*.html        → esqueletos de página por tipo
  · marcas/registro.json → presets de color
  · COMPOSICION.md       → las 12 leyes duras

Salida: datos/base-diseno.json (determinista: sin fecha, ordenado).

Uso:
  python3 scripts/generar-base-datos.py           # escribe
  python3 scripts/generar-base-datos.py --check   # falla si el disco no coincide
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "datos" / "base-diseno.json"

# ---------------------------------------------------------------------------
# Curación editorial: 18 categorías. La frase responde a "¿cuándo lo abro?".
# ---------------------------------------------------------------------------
CATEGORIAS = {
    1: {
        "cuandoUsar": "Cuando necesites el esqueleto de la página: contenedores, rejillas, app shell, split, bento o regiones. Empieza aquí antes de colocar cualquier objeto.",
        "tags": ["layout", "estructura", "rejilla", "grid", "contenedor", "appshell", "bento"],
    },
    2: {
        "cuandoUsar": "Cuando el usuario tenga que orientarse o moverse: navbar, tabs, sidebar, breadcrumbs, paginación o stepper.",
        "tags": ["navegacion", "menu", "tabs", "sidebar", "breadcrumb", "paginacion", "stepper"],
    },
    3: {
        "cuandoUsar": "Cuando necesites jerarquía de texto, prosa larga, cifras o utilidades de lectura. La escala ya está recortada: no inventes tamaños.",
        "tags": ["tipografia", "texto", "prosa", "titular", "cifra", "lectura"],
    },
    4: {
        "cuandoUsar": "Cuando el usuario deba hacer algo: botones, grupos de acción, enlaces de acción y estados de carga.",
        "tags": ["accion", "boton", "cta", "enlace", "cargando"],
    },
    5: {
        "cuandoUsar": "Cuando haya que recoger datos: fields, inputs, selects, checkboxes, switches, validación y fieldset.",
        "tags": ["formulario", "input", "campo", "select", "checkbox", "switch", "validacion"],
    },
    6: {
        "cuandoUsar": "Cuando el sistema tenga que contar algo: alertas, badges, toasts, callouts, skeletons, empty states y progreso.",
        "tags": ["feedback", "alerta", "badge", "toast", "estado", "vacio", "carga", "progreso"],
    },
    7: {
        "cuandoUsar": "Cuando algo deba aparecer encima sin cambiar de página: modales, drawers, sheets, popovers y tooltips.",
        "tags": ["overlay", "modal", "drawer", "sheet", "popover", "tooltip", "dialogo"],
    },
    8: {
        "cuandoUsar": "Cuando haya que leer o comparar datos: tablas, KPIs, listas, timeline, árbol, heatmap y comparativas.",
        "tags": ["datos", "tabla", "kpi", "lista", "timeline", "arbol", "heatmap", "comparativa"],
    },
    9: {
        "cuandoUsar": "Cuando haya imagen, vídeo, audio, avatar, galería o figure. Todo con proporción y pie resueltos.",
        "tags": ["media", "imagen", "video", "audio", "avatar", "galeria", "figure"],
    },
    10: {
        "cuandoUsar": "Cuando haya producto, precio, carrito, checkout, plan o reseña. El flujo de compra ya viene pensado.",
        "tags": ["comercio", "producto", "precio", "carrito", "checkout", "plan", "resena"],
    },
    11: {
        "cuandoUsar": "Cuando haya comunidad, perfil, testimonios, share o métricas sociales.",
        "tags": ["social", "perfil", "testimonio", "share", "comunidad", "metrica"],
    },
    12: {
        "cuandoUsar": "Cuando necesites accesibilidad, utilidades de visibilidad, print o estados de sistema. Es la capa transversal.",
        "tags": ["sistema", "accesibilidad", "a11y", "utilidad", "print", "tema"],
    },
    13: {
        "cuandoUsar": "Cuando haya que comunicar una magnitud o tendencia: barras, líneas, donut, gauge, sparkline, waterfall o bullet. Elige por la pregunta, no por la estética.",
        "tags": ["grafico", "chart", "barra", "linea", "donut", "gauge", "sparkline", "waterfall", "bullet"],
    },
    14: {
        "cuandoUsar": "Cuando haya conversación, prompts, tool calls, planes de tarea o aprobación humana. Los estados del agente son parte del diseño.",
        "tags": ["ia", "chat", "prompt", "agente", "toolcall", "taskplan", "aprobacion"],
    },
    15: {
        "cuandoUsar": "Cuando construyas una herramienta de escritorio web: ventana, appnav, kanban, actbar o statusbar.",
        "tags": ["app", "escritorio", "ventana", "kanban", "actbar", "statusbar"],
    },
    16: {
        "cuandoUsar": "Capa de estilo opcional para superficies de cristal. Úsala con moderación y solo si el proyecto la pide; no es la base.",
        "tags": ["cristal", "estilo", "superficie", "opcional"],
    },
    17: {
        "cuandoUsar": "Cuando la página combine varios objetos: dashboards, settings, checkout, onboarding, pricing o estados completos. Mira aquí antes de inventar una composición.",
        "tags": ["patron", "composicion", "dashboard", "settings", "checkout", "onboarding", "pricing"],
    },
    18: {
        "cuandoUsar": "Cuando presentes una charla o historia en beats: titular, editorial, numeral, dato, nodo y QR.",
        "tags": ["escenario", "charla", "presentacion", "beat", "historia"],
    },
}

# Recetas canónicas: qué son y para qué se copian.
RECETAS_META = {
    "admin": ("Panel de administración", "Tabla densa con filtros, acciones masivas, estados y detalle. El patrón de gestión de usuarios."),
    "ajustes": ("Ajustes de cuenta", "Preferencias en dos columnas con navegación lateral, formularios y guardado por sección."),
    "charla": ("Charla en beats", "Presentación con el objeto de escenario: ritmo, jerarquía y un dato por beat."),
    "dashboard": ("Panel de indicadores", "KPIs, gráficos y tabla en un app shell. El patrón de producto analítico."),
    "informe": ("Informe ejecutivo", "Cifras, tabla y conclusiones en prosa. El patrón de entregable."),
    "login": ("Acceso", "Formulario de entrada con validación visible y estados de error."),
}
EJEMPLOS_META = {
    "chat-ia": ("Chat de IA", "Conversación con prompts, tool call y plan de tarea. El patrón de agente."),
    "dashboard": ("Dashboard mínimo", "Versión de arranque del panel: cuatro KPIs y una tabla."),
    "forms": ("Formulario de alta", "Formulario completo con fieldset, ayudas y validación."),
    "landing": ("Landing", "Hero, features, prueba social y CTA. El patrón de marketing."),
    "login": ("Login mínimo", "Versión de arranque del acceso."),
}

# Secciones de tokens que el CSS marca con comentarios; se normalizan para la UI.
SECCIONES_TOKEN = {
    "general": "Marca y base",
    "color · semánticos": "Color · semánticos",
    "color · neutros": "Color · neutros",
    "roles temáticos": "Roles temáticos",
    "espacio": "Espaciado",
    "geometría": "Geometría",
    "z-index": "Z-index",
    "movimiento": "Movimiento",
    "focus": "Foco",
}


def leer_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def limpiar_seccion(s: str) -> str:
    s = (s or "general").strip()
    s = re.sub(r"^\d+\.\s*", "", s)
    s = s.split("(")[0].strip(" ·-")
    if not s:
        return "Marca y base"
    clave = s.lower()
    return SECCIONES_TOKEN.get(clave, s[:1].upper() + s[1:])


def es_color(valor: str) -> bool:
    v = valor.strip().lower()
    return bool(
        re.match(r"^#[0-9a-f]{3,8}$", v)
        or v.startswith(("rgb(", "rgba(", "hsl(", "hsla(", "oklch(", "oklab(", "color-mix("))
    )


def titulo_de(objeto: dict) -> str:
    m = objeto.get("markup") or {}
    return (m.get("titulo") or "").strip()


def clases_base(objeto: dict) -> list[str]:
    return [c for c in objeto.get("clases", []) if "__" not in c and "--" not in c]


def construir() -> dict:
    comp = leer_json(ROOT / "components.json")
    objetos = comp.get("objetos", {})
    tokens_def = comp.get("tokens_def", [])
    tokens_dark = set(comp.get("tokens_dark", []))
    alias = comp.get("alias", {})
    packs = comp.get("packs", {})

    # --- alias inversos: "tree" busca nz-arbol -----------------------------
    alias_por_familia: dict[str, list[str]] = {}
    familias_existentes = set(objetos)
    for en, clase in alias.items():
        # la clase puede ser un modificador (nz-btn--icon): se queda con la base
        base = clase.split("--")[0].split("__")[0]
        if base in familias_existentes:
            alias_por_familia.setdefault(base, []).append(en)

    # --- specs: categorías y demos ----------------------------------------
    specs = {}
    for f in sorted((ROOT / "specs").glob("*.json")):
        s = leer_json(f)
        specs[int(s["cat"])] = s

    categorias = []
    for cat in sorted(specs):
        s = specs[cat]
        meta = CATEGORIAS.get(cat, {"cuandoUsar": "", "tags": []})
        pack = s["pack"]
        info = packs.get(pack, {})
        categorias.append({
            "id": cat,
            "nombre": s["nombre"],
            "descripcion": s.get("desc", ""),
            "pack": pack,
            "pagina": f"paginas/{s['fichero']}",
            "objetos": info.get("objetos", 0),
            "familias": info.get("familias", 0),
            "demos": info.get("demos", 0),
            "cuandoUsar": meta["cuandoUsar"],
            "tags": meta["tags"],
        })

    # --- familias ----------------------------------------------------------
    familias = []
    for nombre, o in sorted(objetos.items()):
        cat = int(o.get("categoria", 0))
        meta = CATEGORIAS.get(cat, {"cuandoUsar": "", "tags": []})
        base = nombre.split("__")[0]
        tags = set(meta["tags"])
        tags.add(base.replace("nz-", "").replace("-", " ").strip())
        tags.update(mod for mod in o.get("modificadores", []) if mod)
        tags.update(alias_por_familia.get(base, []))
        fam = {
            "id": nombre,
            "categoria": cat,
            "pack": o.get("pack", ""),
            "demo": o.get("demo", ""),
            "titulo": titulo_de(o),
            "clases": o.get("clases", []),
            "modificadores": o.get("modificadores", []),
            "partes": o.get("partes", []),
            "tokens": o.get("tokens", []),
            "nTokens": o.get("nTokens", len(o.get("tokens", []))),
            "markup": (o.get("markup") or {}).get("markup", ""),
            "noUsar": o.get("noUsar", ""),
            "cuandoUsar": meta["cuandoUsar"],
            "tags": sorted(t for t in tags if t),
            "alias": sorted(alias_por_familia.get(base, [])),
        }
        familias.append(fam)

    # --- tokens ------------------------------------------------------------
    tokens = []
    for t in tokens_def:
        nombre = t.get("nombre", "")
        if not nombre.startswith("--nz-"):
            continue
        tokens.append({
            "nombre": nombre,
            "valor": t.get("valor", ""),
            "seccion": limpiar_seccion(t.get("seccion", "")),
            "esColor": es_color(t.get("valor", "")),
            "dark": nombre in tokens_dark,
        })

    # --- recetas y ejemplos: metadatos objetivos del HTML ------------------
    def metadatos_html(p: Path) -> dict:
        txt = p.read_text(encoding="utf-8")
        titulo = re.search(r"<title>(.*?)</title>", txt, re.S)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt, re.S)
        packs_usados = sorted(set(re.findall(r"(?:packs/)(p\d+-[a-z0-9-]+\.css)", txt)))
        secciones = re.findall(r"<h2[^>]*>(.*?)</h2>", txt, re.S)
        limpia = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
        return {
            "titulo": limpia(titulo.group(1)) if titulo else p.stem,
            "h1": limpia(h1.group(1)) if h1 else "",
            "packs": packs_usados,
            "secciones": [limpia(s) for s in secciones][:12],
        }

    recetas = []
    for p in sorted((ROOT / "bloques" / "recetas").glob("*.html")):
        if p.stem == "index":
            continue
        m = metadatos_html(p)
        titulo, desc = RECETAS_META.get(p.stem, (m["titulo"], ""))
        recetas.append({
            "id": p.stem,
            "titulo": titulo,
            "fichero": f"bloques/recetas/{p.name}",
            "tipo": p.stem,
            "nivel": "canonica",
            "descripcion": desc,
            "h1": m["h1"],
            "packs": m["packs"],
            "secciones": m["secciones"],
            "tags": sorted(set([p.stem] + [x.lower() for x in m["secciones"]])),
        })

    ejemplos = []
    for p in sorted((ROOT / "bloques" / "ejemplos").glob("*.html")):
        m = metadatos_html(p)
        titulo, desc = EJEMPLOS_META.get(p.stem, (m["titulo"], ""))
        ejemplos.append({
            "id": p.stem,
            "titulo": titulo,
            "fichero": f"bloques/ejemplos/{p.name}",
            "tipo": p.stem,
            "nivel": "minima",
            "descripcion": desc,
            "h1": m["h1"],
            "packs": m["packs"],
            "secciones": m["secciones"],
            "tags": sorted(set([p.stem, "ejemplo", "arranque"])),
        })

    # --- combos ------------------------------------------------------------
    combos = []
    esqueletos = comp.get("combosEsqueleto", {})
    for nombre, c in sorted(comp.get("combos", {}).items()):
        esq = esqueletos.get(nombre, {})
        combos.append({
            "id": nombre,
            "fichero": esq.get("fichero", f"bloques/combos/{nombre}.html"),
            "packs": c.get("packs", []),
            "tipico": c.get("tipico", ""),
            "familias": esq.get("familias", []),
            "tags": sorted(set([nombre] + nombre.split("-"))),
        })

    # --- marcas ------------------------------------------------------------
    marcas = []
    registro = leer_json(ROOT / "marcas" / "registro.json")
    for m in registro:
        nombre = m.get("nombre", "")
        marcas.append({
            "id": nombre,
            "marca": m.get("marca", ""),
            "acento": m.get("acento", ""),
            "fichero": f"marcas/{nombre}.css",
            "contraste": m.get("contraste_marca_600"),
            "contrasteOk": m.get("contraste_ok", False),
            "ajustadaAA": m.get("marca_ajustada_aa", False),
        })

    # --- las 12 leyes duras ------------------------------------------------
    principios = []
    comp_txt = (ROOT / "COMPOSICION.md").read_text(encoding="utf-8")
    bloque = comp_txt.split("## 1. Las 12 leyes duras")[1].split("## 2.")[0]
    for fila in re.findall(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", bloque, re.M):
        num, ley, lint = fila
        ley = re.sub(r"\*\*(.*?)\*\*", r"\1", ley)
        principios.append({
            "id": int(num),
            "titulo": ley,
            "lint": re.sub(r"`(.*?)`", r"\1", lint),
        })

    total_clases = sum(len(o.get("clases", [])) for o in objetos.values())
    return {
        "name": "Aurora — base de datos de diseño",
        "version": comp.get("version", ""),
        "descripcion": "Índice consultable del sistema: familias, tokens, recetas, combos y marcas. Cada ficha enlaza a su demo viva y lleva el markup real.",
        "fuente": "components.json + specs/ + bloques/recetas/ + bloques/ejemplos/ + bloques/combos/ + marcas/registro.json + COMPOSICION.md",
        "explorador": "base.html",
        "resumen": {
            "familias": len(familias),
            "clases": total_clases,
            "tokens": len(tokens),
            "categorias": len(categorias),
            "recetas": len(recetas),
            "ejemplos": len(ejemplos),
            "paginas": len(recetas) + len(ejemplos),
            "combos": len(combos),
            "marcas": len(marcas),
            "principios": len(principios),
            "alias": len(alias),
        },
        "principios": principios,
        "categorias": categorias,
        "familias": familias,
        "tokens": tokens,
        "recetas": recetas,
        "ejemplos": ejemplos,
        "combos": combos,
        "marcas": marcas,
        "alias": alias,
        "lexico": comp.get("lexico", {}),
    }


def serializar(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, indent=1) + "\n"


def main() -> int:
    datos = construir()
    texto = serializar(datos)
    check = "--check" in sys.argv

    if check:
        if not DATOS.exists():
            print("FALLO: falta datos/base-diseno.json (ejecuta sin --check)")
            return 1
        actual = DATOS.read_text(encoding="utf-8")
        if actual != texto:
            print("FALLO: datos/base-diseno.json está desincronizado. Regenera con scripts/generar-base-datos.py")
            return 1
        print(f"OK: base de datos sincronizada ({datos['resumen']['familias']} familias, {datos['resumen']['tokens']} tokens)")
        return 0

    DATOS.parent.mkdir(parents=True, exist_ok=True)
    DATOS.write_text(texto, encoding="utf-8")
    r = datos["resumen"]
    print(
        f"datos/base-diseno.json · {r['familias']} familias · {r['clases']} clases · "
        f"{r['tokens']} tokens · {r['recetas']} recetas · {r['combos']} combos · {r['marcas']} marcas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
