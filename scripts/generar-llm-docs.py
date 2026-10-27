# -*- coding: utf-8 -*-
"""Genera components.json y LLM.md a partir de los packs, los specs y los tokens.

La idea (patrón «design system infalible para LLMs»): un agente NO debe leer
250 KB de CSS para usar Aurora. Con estos dos archivos sabe qué packs cargar,
qué clases existen de verdad, qué tokens hay disponibles y cómo encajan los
packs en una página real, sin inventarse nada.

  · components.json → spec machine-readable completo (clases + tokens + alias + combos)
  · LLM.md          → guía de decisión en prosa, ~6 KB, para meter en contexto

Novedades v9.1 (Fase B del plan Aurora 9):
  · components.json por familia: clases, partes __, modificadores del léxico,
    tokens --nz-* consumidos, markup mínimo de ejemplo (de specs/ reales) y
    anti-patrones «noUsar»
  · alias ampliados 32 → 150 al vocabulario natural de los LLMs (verificados
    contra el censo; el generador aborta si alguno apunta a algo inexistente)
  · llms.txt en la raíz apuntando a LLM.md, components.json y bloques/ejemplos/
  · punto 5 de la Fase B: cada combo genera además su MARKUP ESQUELETO en
    bloques/combos/<combo>.html (receta de arranque completa con las clases reales
    del sistema). Nada se escribe a mano: los bloques se EXTRAEN de las demos
    reales de specs/ y se validan contra el censo de los packs — si una clase
    del esqueleto no existe, o una familia no pertenece a los packs del combo,
    el generador ABORTA. El esqueleto también viaja en components.json
    (clave `combosEsqueleto`) para que un LLM lo descubra sin leer el disco.

Novedades v7.2:
  · inventario completo de tokens (--nz-*) desde tokens.css (root + dark)
  · alias inglés→clase real (la IA busca «tree», la clase es nz-arbol)
  · combos: qué packs enlazar según el tipo de página
  · CDN versionado (@v7.1.0 en adelante) en vez de @master (caché de jsDelivr)

Uso: python scripts/generar-llm-docs.py
"""
import json
import pathlib
import re
import sys
from importlib import import_module

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
bc = import_module("build-catalog")

ROOT = bc.ROOT
VERSION = "10.7.0"
# El canal vivo no se copia a mano: sale de datos/canales.json (único dueño)
_canales = json.loads((ROOT / "datos" / "canales.json").read_text(encoding="utf-8"))
CANAL_VIVO = _canales["canales"]["vivo"]["rango"]
CDN = f"https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v{VERSION}/"

# ---------------------------------------------------------------------------
# Alias: concepto en inglés → clase real. Solo entradas verificadas contra el
# censo: la IA busca «hide-mobile» y la clase es nz-hide-movil, etc.
# ---------------------------------------------------------------------------
ALIAS = {
    # Alias históricos (v7.2, verificados):
    "tree": "nz-arbol",
    "keyboard-shortcut": "nz-atajo-teclado",
    "kbd": "nz-atajo-teclado",
    "command-palette": "nz-cmd",
    "confirm-dialog": "nz-confirm",
    "dashboard-grid": "nz-dash-grid",
    "data-grid": "nz-datagrid",
    "error-state": "nz-errorstate",
    "error-hint": "nz-hint-error",
    "file-dropzone": "nz-filezona",
    "form-grid": "nz-formgrid",
    "gallery": "nz-galeria",
    "hide-mobile": "nz-hide-movil",
    "hide-desktop": "nz-hide-escritorio",
    "show-mobile": "nz-show-movil",
    "show-desktop": "nz-show-escritorio",
    "cloud-logo": "nz-logo-nube",
    "logo-cloud": "nz-logos",
    "map-placeholder": "nz-mapa-placeholder",
    "popup-menu": "nz-menu-pop",
    "note": "nz-nota",
    "pricing-plan": "nz-plan",
    "pricing-plans": "nz-plans",
    "social-links": "nz-social",
    "task-plan": "nz-taskplan",
    "theme-badge": "nz-tema-badge",
    "figure": "nz-figura",
    "message": "nz-msg",
    "mobile-nav": "nz-navbar",
    "tooltip": "nz-popover",
    "spinner": "nz-spinner",
    "empty-state": "nz-empty",
    # Vocabulario natural EN→ES de los LLMs (v9.1, verificado contra el censo):
    "accordion": "nz-collapsible",
    "alert": "nz-alert",
    "avatar": "nz-avatar",
    "backdrop": "nz-backdrop",
    "badge": "nz-badge",
    "banner": "nz-banner",
    "bar-chart": "nz-chart-bar",
    "bento-grid": "nz-bento",
    "blockquote": "nz-blockquote",
    "breadcrumb": "nz-breadcrumb",
    "button": "nz-btn",
    "callout": "nz-callout",
    "cart": "nz-cart",
    "chart": "nz-chart",
    "chat": "nz-chat",
    "checkbox": "nz-checkbox",
    "checkout": "nz-checkout-steps",
    "chip": "nz-chip",
    "code": "nz-code",
    "code-editor": "nz-codepad",
    "collapsible": "nz-collapsible",
    "comment": "nz-comment",
    "container": "nz-container",
    "context-menu": "nz-menu-pop",
    "countdown": "nz-countdown",
    "dialog": "nz-modal",
    "diff": "nz-diff",
    "divider": "nz-divider",
    "dock": "nz-dock",
    "donut-chart": "nz-chart-donut",
    "drawer": "nz-drawer",
    "dropdown": "nz-dropdown",
    "dropzone": "nz-filezona",
    "empty": "nz-empty",
    "estado-vacio": "nz-estado-vacio",
    "fab": "nz-fab",
    "faq": "nz-preguntas-frecuentes",
    "feed": "nz-feed",
    "fieldset": "nz-fieldset",
    "file-upload": "nz-filezona",
    "floating-action-button": "nz-fab",
    "footer": "nz-footer",
    "form": "nz-field",
    "gauge": "nz-chart-gauge",
    "grid": "nz-grid-12",
    "guided-empty-state": "nz-estado-vacio",
    "guided-empty-state-es": "nz-estado-vacio",
    "hashtag": "nz-hashtag",
    "header": "nz-header",
    "heatmap": "nz-heatmap",
    "hero": "nz-hero-bleed",
    "input": "nz-input",
    "kanban": "nz-kanban",
    "kpi-card": "nz-kpi",
    "label": "nz-label",
    "lightbox": "nz-lightbox",
    "line-chart": "nz-chart-line",
    "link": "nz-link",
    "list": "nz-list",
    "masonry": "nz-masonry",
    "mention": "nz-mention",
    "menu": "nz-menu",
    "meter": "nz-meter",
    "modal": "nz-modal",
    "navbar": "nz-navbar",
    "notification": "nz-notif",
    "offcanvas": "nz-offcanvas",
    "otp-input": "nz-otp",
    "pagination": "nz-pagination",
    "password": "nz-password",
    "popover": "nz-popover",
    "post": "nz-post",
    "pricing": "nz-plans",
    "pricing-table": "nz-pricetable",
    "progress": "nz-progress",
    "prompt": "nz-prompt",
    "qr": "nz-qr",
    "qr-code": "nz-qr",
    "quote": "nz-quote",
    "radio": "nz-radio",
    "range-slider": "nz-range",
    "rating": "nz-stars",
    "scrim": "nz-scrim",
    "search": "nz-search",
    "segmented-control": "nz-segmented",
    "select": "nz-select",
    "share": "nz-share",
    "sheet": "nz-sheet",
    "sidebar": "nz-sidebar",
    "skeleton": "nz-skeleton",
    "skip-link": "nz-skip-link",
    "slider": "nz-range",
    "spacer": "nz-spacer",
    "sparkline": "nz-sparkline",
    "split-pane": "nz-splitpane",
    "sr-only": "nz-visually-hidden",
    "stack": "nz-stack",
    "stars": "nz-stars",
    "stat-card": "nz-kpi",
    "statusbar": "nz-statusbar",
    "stepper": "nz-stepper",
    "switch": "nz-switch",
    "table": "nz-table",
    "table-of-contents": "nz-toc",
    "tabs": "nz-tabs",
    "textarea": "nz-textarea",
    "thinking-indicator": "nz-thinking",
    "timeline": "nz-timeline",
    "toast": "nz-toast",
    "toc": "nz-toc",
    "tool-call": "nz-toolcall",
    "toolbar": "nz-toolbar",
    "tree-view": "nz-tree",
    "truncate": "nz-truncate",
    "typing-indicator": "nz-thinking",
    "upload": "nz-filezona",
    "visually-hidden": "nz-visually-hidden",
    "window": "nz-window",
}


# ---------------------------------------------------------------------------
# Anti-patrones: cuándo NO usar cada familia. Solo donde aplica; lo que no
# está aquí no tiene trampa conocida. Verificado contra las demos reales.
# ---------------------------------------------------------------------------
ANTI_PATRONES = {
    "nz-btn": [
        "No lo uses para navegación entre páginas: usa `.nz-link` o un elemento del nav.",
        "No hagas un botón por cada tono del léxico en la misma barra: ≤ 2 momentos de color por grupo.",
    ],
    "nz-chart-bar": [
        "No para magnitudes dispares o de escala incompatible: usa `.nz-chart-tablebar`.",
    ],
    "nz-chart-line": [
        "No para comparar partes de un todo: usa `.nz-chart-donut`.",
        "No con series desordenadas en el eje X: la línea implica continuidad temporal.",
    ],
    "nz-chart-donut": [
        "No con más de 5-6 porciones: se vuelve ilegible; usa una tabla o barras.",
        "No para series temporales: usa `.nz-chart-line` o `.nz-chart-bar`.",
    ],
    "nz-kpi": [
        "No lo uses como contenedor genérico de texto: es una cifra con contexto.",
    ],
    "nz-table": [
        "Si la tabla no cabe y no apilas con `.nz-table-wrap--apilable` + `data-etiqueta`, se corta en móvil.",
    ],
    "nz-modal": [
        "No lo uses para contenido de lectura larga: es una decisión, no una página.",
        "No lo anides: un diálogo modal dentro de otro rompe el foco.",
    ],
    "nz-drawer": [
        "No para contenido principal de la página: es un panel secundario.",
    ],
    "nz-toast": [
        "No para información que el usuario deba consultar luego: es efímero; usa `.nz-alert` o `.nz-notif`.",
        "No pongas acciones críticas (confirmar borrado) dentro de un toast.",
    ],
    "nz-alert": [
        "No lo uses como decoración: cada alerta visible es un momento de color de los ≤5 por página.",
    ],
    "nz-badge": [
        "No para texto largo ni frases: es una etiqueta de 1-3 palabras.",
    ],
    "nz-avatar": [
        "No para logotipos de marca: usa `.nz-logomark` / `.nz-logo-nube`.",
    ],
    "nz-tabs": [
        "No para pasos secuenciales de un proceso: eso es `.nz-stepper`.",
    ],
    "nz-stepper": [
        "No para navegación libre entre secciones: los pasos tienen orden; eso es `.nz-tabs`.",
    ],
    "nz-popover": [
        "No para contenido crítico ni interactivo complejo: es información contextual al vuelo.",
    ],
    "nz-pagination": [
        "No para un scroll infinito o feed: la paginación es para conjuntos acotados.",
    ],
    "nz-skeleton": [
        "No para cargas < 300ms: parpadea y estorba. Solo esperas perceptibles.",
    ],
    "nz-progress": [
        "No para operaciones indeterminadas: para eso existe el spinner/`.nz-spinner`.",
    ],
    "nz-chat": [
        "No como contenedor estático: el chat implica hilo con participación de dos partes.",
    ],
    "nz-prompt": [
        "No lo uses como input de formulario normal: es la entrada de un asistente IA.",
    ],
    "nz-kanban": [
        "No para más de 5-6 columnas: se rompe en móvil; agrupa estados.",
    ],
    "nz-galeria": [
        "No para contenido crítico solo visible en el carrusel: lo que importa, fuera del carrusel.",
    ],
    "nz-hero-bleed": [
        "Uno por página. No apiles héroes.",
    ],
    "nz-dash-grid": [
        "No metas contenido de lectura larga: es una rejilla de módulos de datos.",
    ],
    "nz-collapsible": [
        "No ocultes información esencial de decisión: si el usuario la necesita siempre, visible.",
    ],
    "nz-empty": [
        "No como excusa: un estado vacío guía a la siguiente acción, no solo anuncia vacío.",
    ],
    "nz-arbol": [
        "No para jerarquías de 2 niveles planas: una lista o el nav basta.",
    ],
    "nz-timeline": [
        "No para eventos sin orden temporal: la línea implica cronología.",
    ],
    "nz-meter": [
        "No para porcentajes que no empiezan en 0 o con valor negativo: mide un llenado.",
    ],
    "nz-switch": [
        "No para acciones (guardar, aplicar): un switch es un estado persistente, no un botón.",
    ],
    "nz-navbar": [
        "No para navegación interna de una vista: es la barra global de la página.",
    ],
}

# ---------------------------------------------------------------------------
# Léxico cerrado de modificadores (AGENTS.md §4). Sirve para separar, en cada
# familia, qué modificadores son del léxico compartido y cuáles son propios.
# ---------------------------------------------------------------------------
MOD_LEXICO = {
    "2xs", "xs", "sm", "lg", "xl", "2xl",
    "brand", "accent", "success", "warning", "danger", "info", "neutral",
    "solid", "soft", "outline", "ghost",
    "vertical", "horizontal", "inline", "compact", "spacious", "center",
    "between", "end",
    "square", "rounded", "pill",
    "flat", "raised",
}


def clases_declaradas_pack(pack):
    """Clases que un pack declara como propias (mismo criterio del censo)."""
    return bc.clases_declaradas(PACKS_DIR / pack)


def reglas_css(pack):
    """Lista de (selector, cuerpo) de primer nivel y de cualquier profundidad."""
    css = (PACKS_DIR / pack).read_text(encoding="utf-8", errors="replace")
    css = bc.COMENTARIO_CSS.sub(" ", css)
    out, depth, buf, sel = [], 0, "", ""
    for ch in css:
        if ch == "{":
            if depth == 0:
                sel, buf = buf.strip(), ""
            else:
                buf += ch
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append((sel, buf))
                buf, sel = "", ""
            else:
                buf += ch
        else:
            buf += ch
    return out


CLASE_SEL = re.compile(r"\.(nz-[A-Za-z0-9_-]+)")
TOKEN_VAR = re.compile(r"(--nz-[a-z0-9-]+)")
CLASE_ATTR = re.compile(r'class="([^"]*)"')
TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)((?:\"[^\"]*\"|[^\">])*?)(/?)>", re.S)
VOID = {"img", "br", "hr", "input", "link", "meta", "source",
        "area", "base", "col", "embed", "track", "wbr"}


def clases_de_markup_attr(attrs):
    m = re.search(r'class="([^"]*)"', attrs)
    return {t for t in m.group(1).split() if t.startswith("nz-")} if m else set()


def fragmento_elemento(mu, m):
    """HTML balanceado del elemento que empieza en m."""
    if m.group(1).lower() in VOID or m.group(3):
        return m.group(0)
    tag = m.group(1)
    depth = 0
    for m2 in re.finditer(r"</?" + tag + r'(?:\"[^\"]*\"|[^\">])*?(/?)>', mu[m.start():], re.S):
        f2 = m2.group(0)
        depth += -1 if f2.startswith("</") else (0 if f2.endswith("/>") else 1)
        if depth == 0:
            return mu[m.start():m.start() + m2.end()]
    return m.group(0)


def markup_minimo(base, tope=1500):
    """Markup mínimo de ejemplo de una familia: el elemento más pequeño de las
    demos reales cuyo class lleva la familia. Preferido: el elemento raíz
    (`.nz-base` o `.nz-base--mod`), no una sub-parte `__`. Nada a mano.
    El techo es el mismo de una demo de receta (1500): así un deck completo
    (.nz-presentacion) cabe como ejemplo mínimo de su familia."""
    mejor = None
    for cat in sorted(specs_por_cat):
        for demo in specs_por_cat[cat]["demos"]:
            mu = demo["markup"]
            for m in TAG.finditer(mu):
                cls = clases_de_markup_attr(m.group(2))
                if base not in {bc.base_de(c) for c in cls}:
                    continue
                cand = fragmento_elemento(mu, m)
                if len(cand) > tope:
                    continue
                raiz = any(c2 == base or c2.startswith(base + "--") for c2 in cls)
                clave = (0 if raiz else 1, len(cand))
                if mejor is None or clave < mejor[0]:
                    mejor = (clave, cat, demo, cand)
    if mejor is None:
        return {"demo": "", "titulo": "", "markup": ""}
    clave, cat, demo, snip = mejor
    return {"demo": f"paginas/{specs_por_cat[cat]['fichero']}",
            "titulo": demo["titulo"], "markup": snip}


def tokens_de_familia(familias_del_pack, pack):
    """Tokens --nz-* que consume cada familia dentro de su pack."""
    consumo = {}
    for sel, body in reglas_css(pack):
        cs = CLASE_SEL.findall(sel)
        cs = [c for c in cs if bc.base_de(c) in familias_del_pack]
        if not cs:
            continue
        toks = set(TOKEN_VAR.findall(body))
        for f in {bc.base_de(c) for c in cs}:
            consumo.setdefault(f, set()).update(toks)
    return consumo


# ---------------------------------------------------------------------------
# Combos: qué packs enlazar según el tipo de página. Siempre tokens.css +
# p1-layout (el esqueleto) + p3-typography + p4-actions (botones): son el suelo.
# ---------------------------------------------------------------------------
COMBOS = {
    "landing": {
        "packs": ["p1-layout.css", "p3-typography.css", "p4-actions.css",
                  "p6-feedback.css", "p10-commerce.css", "p11-social.css"],
        "tipico": "hero + features + pricing + footer + atribución",
    },
    "dashboard": {
        "packs": ["p1-layout.css", "p2-navigation.css", "p3-typography.css",
                  "p4-actions.css", "p8-data.css", "p13-charts.css"],
        "tipico": "appshell + navbar + KPIs + tablas + gráficos",
    },
    "chat-ia": {
        "packs": ["p1-layout.css", "p3-typography.css", "p4-actions.css",
                  "p5-forms.css", "p14-ai.css"],
        "tipico": "chat + prompt + toolcall + taskplan + adjuntos",
    },
    "login-form": {
        "packs": ["p1-layout.css", "p3-typography.css", "p4-actions.css",
                  "p5-forms.css", "p6-feedback.css"],
        "tipico": "card centrada + field + input + botón + alerta de error",
    },
    "presentacion": {
        "packs": ["p1-layout.css", "p2-navigation.css", "p18-escenario.css"],
        "tipico": "deck de slides a pantalla completa con barra de posición y anclas",
    },
    "escritorio-app": {
        "packs": ["p1-layout.css", "p2-navigation.css", "p3-typography.css",
                  "p4-actions.css", "p6-feedback.css", "p8-data.css", "p15-apps.css"],
        "tipico": "window + appnav + kanban/agenda + statusbar",
    },
    "e-commerce": {
        "packs": ["p1-layout.css", "p3-typography.css", "p4-actions.css",
                  "p10-commerce.css", "p8-data.css"],
        "tipico": "producto + cart + checkout-steps + pricetable",
    },
    "charla-beats": {
        "packs": ["p1-layout.css", "p18-escenario.css"],
        "tipico": "lienzo 16:9 + titular/editorial/numeral + nodos del diagrama + QR de cierre",
    },
    "prototipo": {
        "packs": ["all.css"],
        "tipico": "exploración rápida: un solo enlace con todos los packs",
    },
}

# Punto 5 de la Fase B: qué familias del sistema forman el esqueleto de cada
# combo. El generador extrae el bloque de cada una de las demos reales de
# specs/, valida todas las clases contra el censo y comprueba que la familia
# declara clases en los packs del combo. Si algo no cuadra, ABORTA.
FAMILIAS_COMBO = {
    "landing": ["nz-hero-bleed", "nz-thirds", "nz-plans", "nz-badge",
                 "nz-footer"],
    "dashboard": ["nz-navbar", "nz-dash-grid", "nz-kpi", "nz-table",
                   "nz-chart", "nz-chart-bar"],
    "chat-ia": ["nz-chat", "nz-prompt", "nz-toolcall", "nz-taskplan"],
    "login-form": ["nz-article", "nz-h2", "nz-lead", "nz-field", "nz-btn",
                    "nz-alert"],
    "escritorio-app": ["nz-window", "nz-appnav", "nz-kanban", "nz-statusbar"],
    "e-commerce": ["nz-product", "nz-cart", "nz-checkout-steps",
                    "nz-pricetable"],
    "charla-beats": ["nz-recorrido", "nz-escenario", "nz-nodo", "nz-qr"],
    "presentacion": ["nz-presentacion"],
    "prototipo": ["nz-btn", "nz-field", "nz-alert", "nz-kpi"],
}


# ---------------------------------------------------------------------------
# Punto 5 de la Fase B: markup esqueleto por combo. Cada combo declara QUÉ
# familias del sistema forman su página típica; el generador EXTRAe el bloque
# de cada familia de las demos reales de specs/ (nada a mano, nada inventado),
# valida todas las clases contra el censo de los packs y compone una receta de
# arranque completa en bloques/combos/<combo>.html. Si una clase no existe o una
# familia no pertenece a los packs del combo, el generador ABORTA.
# ---------------------------------------------------------------------------

def _clases_de_markup_attr(attrs):
    """Clases nz-* de una cadena de atributos de etiqueta de apertura."""
    m = re.search(r'class="([^"]*)"', attrs)
    return {t for t in m.group(1).split() if t.startswith("nz-")} if m else set()


def _fragmento_elemento(mu, m):
    """HTML balanceado del elemento que empieza en m (comparte lógica con
    markup_minimo, pero sin tope: un bloque de combo puede ser más largo)."""
    if m.group(1).lower() in VOID or m.group(3):
        return m.group(0)
    tag = m.group(1)
    depth = 0
    for m2 in re.finditer(r"</?" + tag + r'(?:\"[^\"]*\"|[^\">])*?(/?)>',
                          mu[m.start():], re.S):
        f2 = m2.group(0)
        depth += -1 if f2.startswith("</") else (0 if f2.endswith("/>") else 1)
        if depth == 0:
            return mu[m.start():m.start() + m2.end()]
    return m.group(0)


def _recorta_clases_shell(frag):
    """Quita de los class= las clases del shell del catálogo (demo-*, cat-*).

    Algunas demos de rejilla usan .demo-box como caja de relleno dentro del
    objeto real (el propio p1 usa demo-box en sus demos de layout). El
    esqueleto debe llevar solo clases del sistema: se dean las nz-* y las cajas
    quedan como <div> — con texto de la demo dentro, que es contenido, no clase.
    """
    def limpia(m):
        nz = sorted(t for t in m.group(1).split() if t.startswith("nz-"))
        return f'class="{" ".join(nz)}"' if nz else ""
    return re.sub(r'class="([^"]*)"', limpia, frag)


def markup_de_familia(base, clases_totales, tope=6000, admite_shell=True):
    """Bloque de demo real de una familia, con criterio de preferencia:
    1) demo sin clases del shell del catálogo; 2) class exactamente la familia
    base (no solo un modificador); 3) raíz de familia (base o base--mod);
    4) más clases nz-* usadas (más completo); 5) más corto. Devuelve None si no
    hay ninguna demo que lo represente sin clases inventadas."""
    mejor = None
    for cat in sorted(specs_por_cat):
        for demo in specs_por_cat[cat]["demos"]:
            mu = demo["markup"]
            con_shell = "demo-" in mu or "cat-" in mu
            if con_shell and not admite_shell:
                continue
            for m in TAG.finditer(mu):
                cls = _clases_de_markup_attr(m.group(2))
                if base not in {bc.base_de(c) for c in cls}:
                    continue
                frag = _fragmento_elemento(mu, m)
                usadas = set(bc.clases_de_markup(frag))
                if any(c not in clases_totales for c in usadas):
                    continue
                if len(frag) > tope:
                    continue
                exacta = base in cls
                raiz = any(c == base or c.startswith(base + "--") for c in cls)
                clave = (1 if con_shell else 0, 0 if exacta else 1,
                         0 if raiz else 1, -len(usadas), len(frag))
                if mejor is None or clave < mejor[0]:
                    mejor = (clave, frag)
    if mejor is None:
        return None
    return _recorta_clases_shell(mejor[1])


def _familia_en_packs(base, packs_combo):
    """¿La familia declara clases en alguno de los packs del combo?"""
    for pack in packs_combo:
        f = PACKS_DIR / pack
        if f.exists() and any(c == base or c.startswith(base + "__")
                              or c.startswith(base + "--")
                              for c in clases_declaradas_pack(pack)):
            return True
    return False


def esqueleto_de_combo(nombre, combo, censo_cat, clases_totales):
    """Devuelve (esqueleto, familias_usadas) del combo o aborta con error claro."""
    packs_combo = combo["packs"]
    prototipo = packs_combo == ["all.css"]
    bloques = []
    familias_usadas = []
    for base in FAMILIAS_COMBO.get(nombre, []):
        if base not in clases_totales:
            sys.exit(f"COMBO ROTO: {nombre} pide la familia {base} "
                     f"y no existe en el censo de los packs")
        if not prototipo and not _familia_en_packs(base, packs_combo):
            sys.exit(f"COMBO ROTO: la familia {base} del combo {nombre} "
                     f"no declara clases en los packs del combo {packs_combo}")
        frag = markup_de_familia(base, clases_totales)
        if frag is None:
            sys.exit(f"COMBO ROTO: la familia {base} del combo {nombre} "
                     f"no tiene ninguna demo real en specs/ de la que extraer "
                     f"su bloque (o sus demos usan clases fuera del censo)")
        bloques.append((base, frag))
        familias_usadas.append(base)
    if not bloques:
        sys.exit(f"COMBO ROTO: {nombre} no declara familias esqueleto "
                 f"(FAMILIAS_COMBO)")
    return bloques, familias_usadas


def pagina_combo(nombre, combo, bloques, familias_usadas, objetos):
    """Receta de arranque completa: <head> con los packs del combo en CDN +
    el esqueleto de cada familia con comentario «Necesito X → uso Y»."""
    L = []
    A = L.append
    # Los packs se DERIVAN de las clases reales del esqueleto. La lista fija del
    # combo se quedó corta al crecer los bloques: `chat-ia` se servía sin
    # `p9-media.css` y `dashboard` sin `p5-forms.css`, así que el esqueleto se veía
    # a medias. `auditar-uso.py` lo cazaba, pero nadie lo pasaba por los combos.
    # La barra de sitio siempre va: su pack se enlaza aunque el esqueleto no lo use.
    usados = set(combo["packs"]) | {"p2-navigation.css"}
    for _, frag in bloques:
        for atributo in re.findall(r'class="([^"]+)"', frag):
            for clase in atributo.split():
                o = objetos.get(bc.base_de(clase))
                if o:
                    usados.add(o["pack"])
    orden = {p: i for i, p in enumerate(bc.PACKS_COMPONENTES)}
    packs = sorted(usados, key=lambda p: orden.get(p, 99))
    cdn_links = "\n".join(
        f'  <link rel="stylesheet" href="{CDN}packs/{p}">'
        for p in packs)
    A(f'<!-- Esqueleto del combo «{nombre}» — GENERADO por '
      f'scripts/generar-llm-docs.py, no se edita a mano.')
    A(f'     Bloques extraídos de las demos reales de specs/ y validados')
    A(f'     contra el censo de los packs: cada clase existe de verdad.')
    A(f'     {combo["tipico"]}. -->')
    A('<!DOCTYPE html>')
    A('<html lang="es" data-nz-theme="light">')
    A("<head>")
    A('<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A(f"<title>Aurora · combo {nombre}</title>")
    A(f'  <link rel="stylesheet" href="{CDN}tokens.css">')
    A(cdn_links)
    A("</head>")
    A('<body class="nz">')
    A('')
    # Barra de sitio: la marca «Aurora» vuelve a la portada y las cinco secciones
    # están a un clic desde cualquier página (antes había que editar la URL).
    A('<nav class="nz-navbar nz-navbar--bordered" aria-label="Sitio">')
    A('  <a class="nz-navbar__brand nz-navbar__link" href="../../index.html"><i></i>Aurora</a>')
    A('  <span class="nz-navbar__links">')
    # Orden canónico compartido por TODOS los índices: Catálogo · Bloques · Marcas ·
    # Iconos · OpenUI · GitHub (menú único de seis, mismo orden en cada página).
    for url, texto in (("base.html", "Catálogo"), ("bloques/recetas/index.html", "Bloques"),
                       ("marcas/index.html", "Marcas"), ("iconos/index.html", "Iconos"),
                       ("openui/index.html", "OpenUI"),
                       ("https://github.com/Ntizar/Aurora", "GitHub")):
        A('    <a class="nz-navbar__link" href="%s%s">%s</a>'
          % ("../../" if not url.startswith("http") else "", url, texto))
    A('  </span>')
    A('</nav>')
    A('')
    # El esqueleto envuelve sus bloques en <main id="contenido">: es el destino
    # real de las anclas internas que traen las demos (navbar y appnav enlazan a
    # #contenido) y el target del skip-link. Sin este id, el combo se servía con
    # anclaves rotos (auditoría de enlaces).
    A('<main id="contenido">')
    for base, frag in bloques:
        A(f'  <!-- {base} (bloque de demo real) -->')
        A("  " + frag)
        A('')
    A('</main>')
    A('<footer class="nz-footer nz-footer--compact">')
    A(f'  Esqueleto del combo «{nombre}» · Hecho con ❤️ por David Antizar')
    A('</footer>')
    A('')
    A("</body>")
    A("</html>")
    return "\n".join(L) + "\n"


def inventario_tokens():
    """Extrae los tokens --nz-* de :root (y cuenta los overrides de dark)."""
    css = (ROOT / "tokens.css").read_text(encoding="utf-8")
    # bloque :root completo (el primero)
    m_root = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    root = m_root.group(1) if m_root else css
    seccion_actual = "general"
    tokens = []
    for linea in root.splitlines():
        ms = re.match(r"\s*/\*\s*----\s*([0-9]+)\.\s*(.+?)\s*\*/", linea)
        if ms:
            seccion_actual = re.sub(r"-+\s*$", "", ms.group(2).strip())
            continue
        mt = re.match(r"\s*(--nz-[a-z0-9-]+)\s*:\s*([^;]+);", linea)
        if mt:
            tokens.append({
                "nombre": mt.group(1),
                "valor": mt.group(2).strip(),
                "seccion": seccion_actual,
            })
    m_dark = re.search(r'\[data-nz-theme="dark"\]\s*\{(.*?)\n\}', css, re.S)
    dark = re.findall(r"(--nz-[a-z0-9-]+)\s*:", m_dark.group(1)) if m_dark else []
    return tokens, dark



def resumen_iconos():
    """Resumen del repositorio de iconos numerados, para components.json y LLM.md.

    La fuente es iconos/iconos.json: aquí solo se cuenta y se ordena. Si el
    repositorio no existiera, el bloque sale en cero en vez de romper la generación.
    """
    ruta = ROOT / "iconos" / "iconos.json"
    vacio = {"total": 0, "grupos": {}, "siguiente": None, "manifiesto": "iconos/iconos.json",
             "sprite": "iconos/sprite.svg", "catalogo": "iconos/index.html",
             "colecciones": {}, "licencias": [], "convencion": ""}
    if not ruta.exists():
        return vacio
    m = json.loads(ruta.read_text(encoding="utf-8"))
    vivos = [i for i in m.get("iconos", []) if i.get("estado", "activo") == "activo"]
    grupos = {}
    for i in vivos:
        grupos[i["grupoNombre"]] = grupos.get(i["grupoNombre"], 0) + 1
    coles = {}
    for i in vivos:
        c = i.get("coleccion", "lucide")
        coles[c] = coles.get(c, 0) + 1
    licencias = sorted({i["licencia"] for i in vivos if i.get("licencia")})
    return {
        "total": len(vivos),
        "siguiente": m.get("siguiente"),
        "grupos": dict(sorted(grupos.items())),
        "colecciones": dict(sorted(coles.items())),
        "licencias": licencias,
        "manifiesto": "iconos/iconos.json",
        "sprite": "iconos/sprite.svg",
        "catalogo": "iconos/index.html",
        "convencion": (m.get("convencion", {}) or {}).get("archivo", ""),
        "uso": '<svg class="nz-icon" aria-hidden="true"><use href="iconos/sprite.svg#nz-i-NNN"/></svg>',
    }


def main():
    global specs_por_cat
    packs, censo_cat, total_clases, total_bases = bc.censo()
    specs = {s["cat"]: s for s in bc.carga_specs()}
    specs_por_cat = specs
    total_demos = sum(len(s["demos"]) for s in specs.values())

    objetos = {}
    for cat, datos in sorted(censo_cat.items()):
        spec = specs.get(cat, {})
        for clase in sorted(datos["clases"]):
            base = bc.base_de(clase)
            o = objetos.setdefault(base, {
                "pack": datos["pack"], "categoria": cat,
                "demo": f"paginas/{spec.get('fichero', '')}",
                "clases": [], "modificadores": [], "partes": [],
            })
            o["clases"].append(clase)
            resto = clase[len(base):]
            if "--" in resto:
                o["modificadores"].append(resto.split("--", 1)[1])
            if "__" in clase:
                o["partes"].append(clase.split("__", 1)[1])

    # --- v9.1: enriquecer cada familia (tokens consumidos, markup mínimo, anti-patrones) ---
    global PACKS_DIR
    PACKS_DIR = bc.PACKS
    consumo_total = {}
    for cat, datos in censo_cat.items():
        consumo_total.update(tokens_de_familia(set(datos["bases"]), datos["pack"]))
    for base, o in objetos.items():
        toks = sorted(consumo_total.get(base, set()))
        o["tokens"] = toks
        o["nTokens"] = len(toks)
        o["markup"] = markup_minimo(base)
        ap = ANTI_PATRONES.get(base)
        if ap:
            o["noUsar"] = ap
        # modificadores del léxico que la familia declara de verdad
        mod_lexico = sorted(
            m for m in o["modificadores"]
            if m in MOD_LEXICO)
        o["modificadoresLexico"] = mod_lexico

    # alias inverso: validar que la clase destino existe de verdad
    clases_totales = set()
    for cat, datos in censo_cat.items():
        clases_totales.update(datos["clases"])
    alias_validos = {}
    for ingles, clase in ALIAS.items():
        if clase in clases_totales or clase in objetos:
            alias_validos[ingles] = clase
        else:
            sys.exit(f"ALIAS ROTO: {ingles} → {clase} no existe en el censo")

    tokens, dark = inventario_tokens()
    if len(tokens) < 100:
        sys.exit(f"INVENTARIO DE TOKENS SOSPECHOSO: solo {len(tokens)} en :root")

    # --- punto 5 Fase B: esqueleto de cada combo → bloques/combos/<combo>.html ---
    # Cada bloque sale de las demos reales de specs/ y pasa dos verificaciones
    # duras: que todas sus clases existan en el censo de los packs y que la
    # familia declare clases en los packs del combo. Si no, el generador aborta.
    combos_dir = ROOT / "bloques" / "combos"
    combos_dir.mkdir(exist_ok=True)
    combos_esqueleto = {}
    for nombre_combo, combo in COMBOS.items():
        bloques, familias_usadas = esqueleto_de_combo(
            nombre_combo, combo, censo_cat, clases_totales)
        (combos_dir / f"{nombre_combo}.html").write_text(
            pagina_combo(nombre_combo, combo, bloques, familias_usadas, objetos),
            encoding="utf-8")
        combos_esqueleto[nombre_combo] = {
            "fichero": f"bloques/combos/{nombre_combo}.html",
            "familias": familias_usadas,
        }

    datos = {
        "name": "Aurora",
        "version": VERSION,
        "type": "css-only design system",
        "namespace": ".nz-",
        "tokens": "tokens.css",
        "cdn": CDN,
        "manifiesto": {
            "gradientes": 0,
            "glass": 0,
            "coloresAMano": 0,
            "importantPermitidoEn": [".nz-visually-hidden", ".nz-print-hide"],
            "tema": 'data-nz-theme="light" | "dark" en el elemento <html>',
            "cuerpo": 'class="nz"',
            "responsiveFirst": True,
            "objetivoTactil": "44px",
        },
        "resumen": {
            "objetos": total_clases,
            "familias": total_bases,
            "categorias": len(censo_cat),
            "demos": total_demos,
            "tokens": len(tokens),
            "tokensDark": len(dark),
            "alias": len(alias_validos),
            "familiasConMarkup": sum(1 for o in objetos.values() if o["markup"]["markup"]),
            "familiasConAntiPatron": sum(1 for o in objetos.values() if "noUsar" in o),
            "tokensConsumidosPorFamilias": len({t for o in objetos.values() for t in o["tokens"]}),
        },
        "packs": {
            datos_pack["pack"]: {
                "categoria": cat,
                "nombre": specs[cat]["nombre"] if cat in specs else "",
                "descripcion": specs[cat]["desc"] if cat in specs else "",
                "objetos": len(datos_pack["clases"]),
                "familias": len(datos_pack["bases"]),
                "demos": len(specs[cat]["demos"]) if cat in specs else 0,
                "pagina": f"paginas/{specs[cat]['fichero']}" if cat in specs else "",
            }
            for cat, datos_pack in sorted(censo_cat.items())
        },
        "iconos": resumen_iconos(),
        "lexico": {
            "tamano": ["--2xs", "--xs", "--sm", "--lg", "--xl"],
            "tono": ["--brand", "--accent", "--success", "--warning", "--danger", "--info", "--neutral"],
            "enfasis": ["--solid", "--soft", "--outline", "--ghost"],
            "disposicion": ["--vertical", "--horizontal", "--inline", "--compact",
                            "--spacious", "--center", "--between", "--end"],
            "forma": ["--square", "--rounded", "--pill"],
            "elevacion": ["--flat", "--raised"],
            "estado": [".is-active", ".is-disabled", ".is-loading", ".is-done",
                       ".is-error", ".is-empty", ".is-selected",
                       "[aria-current]", "[aria-selected]", "[aria-expanded]"],
        },
        "alias": alias_validos,
        "combos": COMBOS,
        "combosEsqueleto": combos_esqueleto,
        "tokens_def": tokens,
        "tokens_dark": dark,
        "objetos": objetos,
    }
    (ROOT / "components.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- LLM.md ----------
    filas = "\n".join(
        f"| {v['categoria']:02d} · {v['nombre']} | `{k}` | "
        f"{', '.join(f'`{b}`' for b in sorted(censo_cat[v['categoria']]['bases'])[:4])}"
        f"{'…' if len(censo_cat[v['categoria']]['bases']) > 4 else ''} |"
        for k, v in sorted(datos["packs"].items(), key=lambda kv: kv[1]["categoria"]))

    filas_combos = "\n".join(
        f"| {nombre} | `tokens.css` + `{', '.join(c['packs'])}` | {c['tipico']} |"
        for nombre, c in COMBOS.items())

    filas_esqueleto = "\n".join(
        f"- `{esq['fichero']}` — esqueleto **{nombre}**: {', '.join(f'`{f}`' for f in esq['familias'])}"
        for nombre, esq in sorted(combos_esqueleto.items()))

    filas_alias = "\n".join(
        f"| «{ingles}» | `{clase}` |"
        for ingles, clase in sorted(alias_validos.items())
        if ingles != clase)

    n_iconos = resumen_iconos()["total"]
    llm = f"""# Aurora — guía de decisión para agentes

Design system CSS puro, sin dependencias ni build. {total_clases} objetos en {len(censo_cat)} categorías.
**No pegues el CSS en el prompt**: enlaza por CDN y usa las clases de esta guía.

## 1. Mínimo obligatorio

```html
<html lang="es" data-nz-theme="light">
<head>
  <link rel="stylesheet" href="{CDN}tokens.css">
  <link rel="stylesheet" href="{CDN}packs/all.css">
</head>
<body class="nz">
```

Ojo: el `<html lang="es" data-nz-theme="light">` y el `<body class="nz">` son el
elemento raíz del documento, no un fragmento — el snippet de arriba muestra dónde
van cada uno. Dark mode: cambia a `data-nz-theme="dark"` en el `<html>`.

## 2. ¿Qué packs enlazo según lo que construyo?

| Tipo de página | CDN | Qué lleva dentro |
|---|---|---|
{filas_combos}

Carga **solo los packs que uses** en producción (cada uno pesa 12-40 KB) o
`packs/all.css` para prototipos. `tokens.css` siempre primero.

**Esqueletos listos para arrancar** (markup de cada tipo de página con las
clases reales del sistema, extraído y validado de las demos — cópialos):

{filas_esqueleto}

La lista completa de familias y su fichero está en `components.json`
(clave `combosEsqueleto`).

## 3. Mapa de categorías (API completa en `components.json`)

| Categoría | Pack | Objetos clave |
|---|---|---|
{filas}

## 4. Necesito X → uso Y

| Necesito | Clases (el pack de cada una está en `components.json`) |
|---|---|
| Botón (p4) | `.nz-btn` + `.nz-btn--primary/--accent/--ghost/--soft/--outline/--danger` + `--sm/--lg/--icon` |
| Superficie / tarjeta (p1) | `.nz-article`, `.nz-bento`, `.nz-thirds`, `.nz-hero-bleed` · **`.nz-card` NO existe** |
| Formulario (p5) | `.nz-field` > `.nz-field__label` + `.nz-input` + `.nz-field__help`, `.nz-formgrid` |
| Elegir una opción (p5) | `.nz-checkbox`, `.nz-radio`, `.nz-switch`, `.nz-segmented` |
| Aviso (p6) | `.nz-alert--info/--success/--warning/--danger`, `.nz-callout` |
| Etiqueta de estado (p6+p3) | `.nz-badge--brand/--success/--danger/--warning`, `.nz-chip`, `.nz-lbl` |
| Tabla ancha (p8) | `.nz-table-wrap` > `.nz-table` (+ `--striped`, `__num`, `__status`): se desplaza a lo ancho |
| Tabla que debe caber entera (p8) | `.nz-table-wrap--apilable` > `.nz-table--apilable` con `data-etiqueta` en cada `td`: en móvil cada fila es una tarjeta, desde 640 px vuelve a ser tabla |
| Cifra destacada (p8) | `.nz-kpi` (`__label/__value/__delta`) |
| Gráfico (p13) | `.nz-chart` + `.nz-chart-bar`, `.nz-chart-line`, `.nz-chart-donut`, `.nz-chart-gauge`, `.nz-heatmap` |
| Diálogo (p7) | `.nz-modal` (checkbox + label, sin JS), `.nz-drawer`, `.nz-sheet` |
| Pantalla completa (p1) | `.nz-appshell`, `.nz-with-sidebar`, `.nz-split`, `.nz-dash-grid` |
| Navegación (p2) | `.nz-navbar`, `.nz-tabs`, `.nz-breadcrumb`, `.nz-stepper`, `.nz-pagination` |
| Chat / IA (p14) | `.nz-chat`, `.nz-msg`, `.nz-prompt`, `.nz-toolcall`, `.nz-taskplan`, `.nz-approval` |
| Escritorio / app (p15) | `.nz-window`, `.nz-appnav`, `.nz-kanban`, `.nz-actbar`, `.nz-statusbar` |
| Icono (p9) | `.nz-icon` con un SVG **del repositorio**: `iconos/sprite.svg#nz-i-NNN` o el fichero `iconos/NNN-nombre.svg` |

**Iconos: nunca un emoji ni un símbolo de texto.** El repositorio `iconos/` trae
{n_iconos} iconos numerados (`nz-i-001`…), cada uno con número estable, nombre castellano y
licencia en `iconos/iconos.json`. Se usan así:

```html
<svg class="nz-icon" aria-hidden="true"><use href="iconos/sprite.svg#nz-i-042"/></svg>
```

El número no cambia nunca: si el nombre se renombra, el 042 sigue siendo el 042. Para
añadir uno: `python3 scripts/iconos.py anadir lucide:nombre`. Catálogo navegable:
`iconos/index.html`.

## 4b. Móvil y escritorio: lo que ya viene resuelto (no lo reinventes)

El sistema garantiza que nada se corta ni se sale de la pantalla, y que en un
monitor grande **no sobra media pantalla**. No hace falta JS ni media queries
propias:

- **Pestañas** (`.nz-tabs`): se envuelven en varias líneas, todas se ven y se
  pulsan. Si una barra debe quedarse en una sola línea, se pide `.nz-tabs--scroll`.
- **Navbar** (`.nz-navbar`): la barra y sus acciones se envuelven; ninguna acción
  queda cortada ni escondida.
- **Tabla apilable** (`.nz-table--apilable`): en móvil cada fila es una tarjeta con
  el nombre de la columna delante. La etiqueta viaja en el HTML:
  `<td data-etiqueta="Entrega">oct 2026</td>`. Desde 640 px vuelve a ser tabla.
  Va con `.nz-table-wrap--apilable` para que el marco lo lleve cada tarjeta.
- **Nada desborda** (p1): los hijos de `.nz-dash-grid`, `.nz-split`, `.nz-thirds`,
  `.nz-bento`, `.nz-grid-12`, `.nz-holy` y `.nz-article` nacen con `min-width: 0`,
  así que una tabla ancha encoge a su contenedor en vez de estirar la página.
- **Lienzo que crece** (escritorio): `.nz-container` mide 72rem, y sube solo a
  84rem desde 1200px y a 96rem desde 1440px. No hace falta tocar nada.
- **Herramienta a pantalla completa**: una app, un panel o un tablero van con
  `.nz-container--app` (sin tope). El texto de lectura sigue con `.nz-container`.
- **La letra no crece con el monitor**: crece el lienzo. Los titulares tienen tope
  (--nz-text-3xl 34px, --nz-text-4xl 50px) a propósito.

## 4d. Tipografía: pesos y tamaños con juicio

Nada de negritas porque sí: cuando todo está en negrita, nada destaca.

- **El mínimo de interfaz es 13px** (`--nz-text-xs`). Los 12px (`--nz-text-2xs`)
  son para **datos**: ejes, contadores, notas al pie. Nunca una etiqueta.
- **Pesos por token**, no a mano: `--nz-peso-normal` (400) cuerpo ·
  `--nz-peso-medio` (500) apoyo y filas activas · `--nz-peso-fuerte` (600) rótulos
  de interfaz, insignias y botones · `--nz-peso-titulo` (700) **solo** titulares y
  cifras grandes. Utilidades: `.nz-text--peso-medio`, `.nz-text--peso-fuerte`.
- **El 800 está retirado** y nada por debajo de 16px lleva 700.
- **La fuente viaja con el CSS**: Inter variable se sirve desde `tokens.css`
  (`fuentes/*.woff2`). No enlaces Google Fonts: el sistema ya la trae y así la
  letra es la misma en todas las máquinas, sin red.

## 4c. Composición: cómo se monta (contrato obligatorio)

Usar las clases correctas **no basta**. Antes de entregar, cumple el contrato de
`COMPOSICION.md` (el lint lo comprueba y falla si no):

1. **0 emojis** como icono (solo el ❤️ de la atribución).
2. **≤ 5** momentos de color saturado por página.
3. **Un protagonista por sección**: la marca o el acento, nunca los dos de igual a
   igual. **Y el acento tiene que aparecer**: cada página lleva al menos un momento
   de acento (el dato que importa, la 2ª serie, la acción secundaria), y la marca no
   acapara más de dos tercios de los momentos de color.
4. Ningún texto de interfaz **por debajo de 13px** (12px solo para datos).
5. **Un `<h1>`**, jerarquía sin saltos y **≤ 4 tamaños** distintos.
6. **Ancho por tipo de página**: una app o un panel va a **ancho completo**, no en columna
   estrecha (el error más común).
7. Ritmo vertical con tokens y **una densidad** por página.
8. Las vistas de datos tienen **tres estados**: vacío, carga y error.
9. Etiquetas de formulario **visibles**: el placeholder no es una etiqueta.
10. Iconos `.nz-icon` en SVG en línea, **nunca emojis**.

La forma correcta de cada tipo de página está en `COMPOSICION.md` §5, y hay páginas
completas listas para copiar en `bloques/recetas/`.

## 5. Buscas un nombre en inglés y no existe

Aurora usa nombres en castellano en algunas familias. Aliases verificados:

| Buscas | Usa |
|---|---|
{filas_alias}

Los nombres de la tabla anterior son los que existen de verdad. Si una clase no
aparece en `components.json`, **no la inventes**.

## 6. Léxico de modificadores (igual en los 18 packs)

- **Tamaño**: `--2xs --xs --sm --lg --xl`
- **Tono**: `--brand --accent --success --warning --danger --info --neutral`
- **Énfasis**: `--solid --soft --outline --ghost`
- **Disposición**: `--vertical --horizontal --inline --compact --spacious --center --between --end`
- **Forma**: `--square --rounded --pill` · **Elevación**: `--flat --raised`
- **Estado**: `.is-active .is-disabled .is-loading .is-done .is-error .is-selected` o `[aria-current] [aria-selected]`

## 7. Marca y acento: dos colores con papeles distintos

La marca **no se toca en CSS**: se elige con un atributo en el `<html>`.

```html
<html lang="es" data-nz-theme="light" data-nz-marca="ntizar">
```

- Presets incluidos: `aurora` (defecto, azul + naranja), `indigo`, `esmeralda`, `violeta`,
  `carmesi`, `ntizar` (azul eléctrico #0057ff + naranja #ff6a00). Un `data-nz-marca` desconocido cae en `aurora` sin romper nada.
- **Los dos colores no son intercambiables**:
  - **Marca** = estructura. Navegación activa, enlaces, foco, botón primario, 1ª serie.
  - **Acento** = **el dato que importa y la acción secundaria**: el delta de un KPI,
    la 2ª serie de un gráfico, el botón de acento, el filete de un titular
    (`.nz-lead--accent`, `.nz-num--accent`, `.nz-kpi--accent`, `.nz-lbl--accent`,
    `.nz-highlight--accent`, `.nz-list--accent`).
  - **Cada página lleva acento**: si la página es toda azul, falta el acento. Y la
    marca no acapara más de dos tercios de los momentos de color.
- Marca propia: `python scripts/generar-marca.py miweb "#0ea5e9" "#f43f5e"` → `marcas/miweb.css`.
  El generador crea la rampa en OKLCH, la ancla a tu color y avisa si necesita ajuste por contraste.
- Todo lo demás (`--nz-brand*`, `--nz-accent*`, foco, sombras de color y **el modo oscuro**)
  se **deriva solo** de esas dos rampas.
- **Color de acento legible en cualquier fondo** (v9.3): el acento NUNCA se pinta de texto
  directamente. Como texto sobre fondo: `var(--nz-accent-text)` (acento-700 en claro,
  acento-400 en oscuro). Como tinta sobre un relleno de acento: `var(--nz-accent-ink)`
  (tinta casi negra en claro; el propio fondo oscuro en dark). El relleno plano
  `--nz-accent` solo va en fondos, gráficos y bordes — nunca sostiene texto blanco
  (medido: blanco s/ acento-500 cae a 2,80:1).
- **Doble declaración OKLch (v9.3)**: cada token de color de `tokens.css` va en hex y
  debajo su gemela `oklch(...)`. Los navegadores modernos usan la OKLch (mejor gamut y
  derivas de tema); los antiguos ignoran la segunda y quedan con el hex. Nunca edites
  solo una de las dos: la convierte `scripts/generar-marca.py` o `scripts/auditar-contraste.py`
  la marca como descuadrada.

Solo si necesitas afinar algo suelto (radio, ancho): la **fuente ya viene cargada**
desde `tokens.css`, así que no hay que enlazar Google Fonts ni tocar `--nz-font`.

```css
:root {{
  --nz-radius-md: 12px;
  --nz-container-max: 72rem;
}}
```

Los {len(tokens)} tokens están inventariados en `components.json` (sección
`tokens_def`, con nombre, valor y sección). Nada fuera de ese catálogo.

## 8. Anti-patrones (NO lo hagas)

- ❌ Pegar el CSS de los packs en el prompt (250 KB ≈ 60.000 tokens). Enlaza por CDN.
- ❌ Inventar clases (`nz-gradient-text`, `nz-btn--glass-liquid-brand`, `nz-card--glass`): no existen aquí. Es la doctrina de Aurora v6, **jubilada**: Aurora es sólido por defecto. El ÚNICO glass oficial es la capa `p16-cristal.css` (`.nz-cristal`, `data-nz-estilo="cristal"`) — se activa, no se reimplementa; nunca en tablas, formularios ni cristal anidado.
- ❌ Escribir colores a mano (`#2563eb`, `rgb(...)`): usa tokens `var(--nz-*)`.
- ❌ Texto blanco sobre relleno de acento o texto acento plano (`color: var(--nz-accent)`):
  en claro cae a 2,80:1 y falla WCAG. Texto de acento → `var(--nz-accent-text)`;
  tinta sobre relleno de acento → `var(--nz-accent-ink)`. La auditoría
  `scripts/auditar-contraste.py` lo caza.
- ❌ Gradientes, `backdrop-filter` o `!important` fuera de sus excepciones oficiales (la capa `.nz-cristal` y los helpers de ocultación): el manifiesto los permite SOLO ahí y la CI los detecta en cualquier otro sitio.
- ❌ Clases globales sin `.nz-`: romperías la convivencia con otros frameworks.
- ❌ Desktop-first: el sistema es responsive first (base móvil en 1 columna, crece con
  `min-width` hasta el escritorio, y los objetos responden a su contenedor).
- ❌ Dejar media pantalla vacía en un monitor grande: un panel o una herramienta usan
  `.nz-container--app`; el lienzo ya crece solo hasta 96rem desde 1440px.
- ❌ `font-weight` a mano (700/800 sueltos) o negritas porque sí: usa `--nz-peso-*`.
  El 800 no existe en el sistema y nada por debajo de 16px lleva 700.
- ❌ Texto de interfaz a 12px: los 12px son para datos, no para etiquetas.
- ❌ Enlazar Google Fonts (o cualquier CDN de fuentes): `tokens.css` ya sirve la fuente.
- ❌ Enlazar `@master` en producción: pinea la versión (`@v{VERSION}`) o jsDelivr te servirá CSS viejo desde su caché.

## 8b. Canales: qué versión enlazar

Dos canales, un sistema. La regla de oro: **nunca `@master`**.

| Canal | URL | Cuándo |
|---|---|---|
| vivo | `@{CANAL_VIVO}` | webs propias: recibe cada release de su serie sin tocarlas |
| congelado | `@{VERSION}` | entregas a cliente: reproducible dentro de dos años |

Si el proyecto trae `aurora.lock`, respétalo: dice qué canal y qué tag está comiendo.
Un cambio aditivo llega solo; renombrar o quitar algo exige major y migración
(`CONTRATO.md`, `scripts/migrar-programas.py`).

## 9. Verificar antes de entregar

```bash
python scripts/auditar-uso.py tu-pagina.html   # lint del HTML consumidor
python scripts/validar-css.py                  # manifiesto + cobertura del sistema
python scripts/auditar-contraste.py            # contraste WCAG de pares + paridad oklch
```

`auditar-uso.py` te dice: clases inventadas, packs que te faltan por enlazar,
colores a mano, gradientes, desktop-first y atribución. EJECÚTALO sobre tu HTML
antes de darlo por bueno y corrige lo que marque.

Recetas completas y funcionando en `bloques/ejemplos/` (login, dashboard, landing,
chat-ia, forms): cópialas como punto de partida.

**Base de datos de diseño:** `base.html` es el explorador (búsqueda por lo que
quieres construir, ficha con markup y preview) y `datos/base-diseno.json` es el
índice machine-readable: {total_bases} familias con su markup, {len(tokens)} tokens,
recetas, combos, marcas y las 12 leyes. Consúltalo antes de leer un pack.

## 10. Interfaces generativas (OpenUI Lang)

Si el HTML lo va a escribir un **modelo en tiempo de ejecución**, no le pases este
documento ni le pidas HTML: dale el lenguaje y la biblioteca.

| Pieza | Qué es |
|---|---|
| `openui/PROMPT.md` | System prompt listo: sintaxis, las 36 firmas y las reglas de diseño |
| `openui/aurora.spec.json` | Biblioteca machine-readable (firmas + JSON Schema) |
| `openui/aurora-openui.js` | Runtime vanilla: OpenUI Lang → markup `.nz-*` (sin React, sin build) |
| `openui/index.html` | Probador en vivo: editas el programa y ves el render |
| `scripts/auditar-openui.py` | Puerta: censo, deriva, runtime y ejemplos |

El modelo emite ~52 % menos tokens que con JSON. Un programa son 3 líneas:

```
root = Pagina([titulo, k])
titulo = Titular("Operaciones de la flota")
k = Kpi("Puntualidad", "94,2 %", "+2,1 pp", "sube", "acento")
```

Regla: si un patrón se repite en dos proyectos, **se sube al repo y se añade a
`openui/componentes.json`** — el siguiente proyecto lo hereda sin escribir CSS.

Docs hermanas: `AGENTS.md` (reglas duras del repo), `components.json` (API
completa machine-readable), `paginas/` (catálogo con una demo viva por objeto),
`README.md`.

Hecho con ❤️ por David Antizar
"""
    (ROOT / "LLM.md").write_text(llm, encoding="utf-8")

    # ---------- llms.txt (estándar para crawlers de LLMs) ----------
    llms = f"""# Aurora — design system CSS puro (v{VERSION})

> Sistema de diseño CSS-only, sin build y sin dependencias. Namespace `.nz-`,
> tokens `--nz-*`, BEM, responsive first. {total_clases} clases en {total_bases} familias,
> {len(censo_cat)} packs. Sin gradientes ni `!important`; glass solo en la capa
> `.nz-cristal` (uso controlado, con fallback opaco).

Documentos para agentes (léelos en este orden):

- [LLM.md]({CDN}LLM.md): guía de decisión (~7 KB). Qué packs enlazar por CDN,
  qué clases usar por necesidad, léxico de modificadores, marca/acento y
  anti-patrones globales. Empieza aquí.
- [components.json]({CDN}components.json): API machine-readable completa. Por
  familia: clases, partes `__`, modificadores (los del léxico en
  `modificadoresLexico`), tokens `--nz-*` que consume, markup mínimo de
  ejemplo extraído de las demos reales y `noUsar` (anti-patrones). Alias
  EN→ES en `alias`.
- [bloques/ejemplos/]({CDN}): 5 páginas completas listas para copiar (login,
  dashboard, landing, chat-ia, forms).
- [llms-full.txt]({CDN}llms-full.txt): referencia completa por componente — las
  {total_clases} clases con markup real, tokens, alias y anti-patrón de cada una.
  Cuando necesites la API exacta de UNA pieza sin abrir components.json.
- [base.html]({CDN}base.html) y [datos/base-diseno.json]({CDN}datos/base-diseno.json):
  base de datos de diseño consultable. {total_bases} familias con markup, tokens,
  recetas, combos y marcas en un índice; búscalo antes de leer un pack.
- [bloques/combos/]({CDN}): esqueleto markup de cada tipo de página (landing,
  dashboard, chat-ia, login-form, e-commerce, escritorio-app, charla-beats,
  prototipo) con clases reales validadas; mapa en `components.json`
  (`combos` y `combosEsqueleto`).
- [paginas/]({CDN}): catálogo vivo con una demo real por objeto.
- [COMPOSICION.md]({CDN}COMPOSICION.md): contrato de composición que el lint
  comprueba (protagonista, acento, jerarquía, densidad, estados).
- [AGENTS.md]({CDN}AGENTS.md): reglas duras del repo.

Reglas mínimas que no se negocian:

1. No pegues los packs en el prompt (~340 KB). Enlaza por CDN pineado:
   `{CDN}tokens.css` + `{CDN}packs/all.css` (o los packs que uses).
2. `<html lang="es" data-nz-theme="light">` + `<body class="nz">`.
3. Toda clase pública empieza por `.nz-`. Si no está en `components.json`,
   no existe: no la inventes.
4. Color siempre por token `var(--nz-*)`. Cero colores a mano, cero
   gradientes, cero `backdrop-filter` (excepción: la capa `.nz-cristal`).
5. Responsive first: base móvil 1 columna, se crece con `min-width`; los objetos
   responden a su contenedor. Táctil 44px.
6. Marca con `data-nz-marca="aurora|indigo|esmeralda|violeta|carmesi|ntizar"`;
   la marca es estructura, el acento es el dato que importa.

Hecho con ❤️ por David Antizar
"""
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")

    # ---------- llms-full.txt: la API entera, componente a componente ----------
    # Una sola fuente (components.json) y generado siempre en la cadena de
    # regeneración: tocarlo a mano es un anti-patrón (§10 de SKILL.md).
    filas = [
        f"# Aurora — referencia completa por componente (v{VERSION})",
        "",
        "> Extiende llms.txt con la API exacta de las " + str(len(objetos)) + " familias:",
        "> clases, markup real, tokens, alias y anti-patrón. Generado desde",
        "> components.json por scripts/generar-llm-docs.py — no lo edites a mano.",
        "",
    ]
    for nombre in sorted(objetos):
        o = objetos[nombre]
        m = (o.get("markup") or {}).get("markup", "")
        no_usar = o.get("noUsar", "")
        if isinstance(no_usar, list):
            no_usar = " ".join(str(x) for x in no_usar)
        filas.append(f"## {nombre} · packs/{o.get('pack', '?')}")
        if o.get("clases"):
            filas.append("clases: " + ", ".join(o["clases"]))
        if o.get("alias"):
            alias = o["alias"]
            if isinstance(alias, dict):
                alias = [f"{k} → {v}" for k, v in alias.items()]
            filas.append("alias: " + ", ".join(alias))
        if o.get("tokens"):
            filas.append("tokens: " + ", ".join(o["tokens"]))
        if m:
            filas.append("markup: " + m.replace("\n", " "))
        if no_usar:
            filas.append("noUsar: " + str(no_usar))
        filas.append("")
    full = "\n".join(filas)
    (ROOT / "llms-full.txt").write_text(full, encoding="utf-8")

    n_markup = sum(1 for o in objetos.values() if o["markup"]["markup"])
    n_anti = sum(1 for o in objetos.values() if "noUsar" in o)
    print(f"components.json → {len(objetos)} familias, {total_clases} clases, "
          f"{len(tokens)} tokens (+{len(dark)} dark), {len(alias_validos)} alias, "
          f"{len(COMBOS)} combos ({len(combos_esqueleto)} con esqueleto)")
    print(f"  familias con markup mínimo: {n_markup}/{len(objetos)} · "
          f"con anti-patrones: {n_anti} · "
          f"tokens consumidos por familias: "
          f"{len({t for o in objetos.values() for t in o['tokens']})}")
    print(f"LLM.md → {len(llm)} bytes")
    print(f"llms.txt → {len(llms)} bytes")


if __name__ == "__main__":
    main()
