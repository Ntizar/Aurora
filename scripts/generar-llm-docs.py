# -*- coding: utf-8 -*-
"""Genera components.json y LLM.md a partir de los packs, los specs y los tokens.

La idea (patrón «design system infalible para LLMs»): un agente NO debe leer
250 KB de CSS para usar Aurora 7. Con estos dos archivos sabe qué packs cargar,
qué clases existen de verdad, qué tokens hay disponibles y cómo encajan los
packs en una página real, sin inventarse nada.

  · components.json → spec machine-readable completo (clases + tokens + alias + combos)
  · LLM.md          → guía de decisión en prosa, ~6 KB, para meter en contexto

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
VERSION = "7.2.2"
CDN = f"https://cdn.jsdelivr.net/gh/Ntizar/Aurora7@v{VERSION}/"

# ---------------------------------------------------------------------------
# Alias: concepto en inglés → clase real. Solo entradas verificadas contra el
# censo: la IA busca «hide-mobile» y la clase es nz-hide-movil, etc.
# ---------------------------------------------------------------------------
ALIAS = {
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
}

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
    "escritorio-app": {
        "packs": ["p1-layout.css", "p2-navigation.css", "p3-typography.css",
                  "p4-actions.css", "p8-data.css", "p15-apps.css"],
        "tipico": "window + appnav + kanban/agenda + statusbar",
    },
    "e-commerce": {
        "packs": ["p1-layout.css", "p3-typography.css", "p4-actions.css",
                  "p10-commerce.css", "p8-data.css"],
        "tipico": "producto + cart + checkout-steps + pricetable",
    },
    "prototipo": {
        "packs": ["all.css"],
        "tipico": "exploración rápida: un solo enlace con los 15 packs",
    },
}


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


def main():
    packs, censo_cat, total_clases, total_bases = bc.censo()
    specs = {s["cat"]: s for s in bc.carga_specs()}
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

    datos = {
        "name": "Aurora 7",
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
            "mobileFirst": True,
            "objetivoTactil": "44px",
        },
        "resumen": {
            "objetos": total_clases,
            "familias": total_bases,
            "categorias": len(censo_cat),
            "demos": total_demos,
            "tokens": len(tokens),
            "tokensDark": len(dark),
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

    filas_alias = "\n".join(
        f"| «{ingles}» | `{clase}` |"
        for ingles, clase in sorted(alias_validos.items())
        if ingles != clase)

    llm = f"""# Aurora 7 — guía de decisión para agentes

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

## 4b. Móvil: lo que ya viene resuelto (no lo reinventes)

El sistema garantiza que nada se corta ni se sale de la pantalla. No hace falta
JS ni media queries propias:

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

## 4c. Composición: cómo se monta (contrato obligatorio)

Usar las clases correctas **no basta**. Antes de entregar, cumple el contrato de
`COMPOSICION.md` (el lint lo comprueba y falla si no):

1. **0 emojis** como icono (solo el ❤️ de la atribución).
2. **≤ 5** momentos de color saturado por página.
3. **Un protagonista por sección**: la marca o el acento, nunca los dos de igual a igual.
4. Ningún texto de interfaz **por debajo de 13px**.
5. **Un `<h1>`**, jerarquía sin saltos y **≤ 4 tamaños** distintos.
6. **Ancho por tipo de página**: una app o un panel va a **ancho completo**, no en columna
   estrecha (el error más común).
7. Ritmo vertical con tokens y **una densidad** por página.
8. Las vistas de datos tienen **tres estados**: vacío, carga y error.
9. Etiquetas de formulario **visibles**: el placeholder no es una etiqueta.
10. Iconos `.nz-icon` en SVG en línea, **nunca emojis**.

La forma correcta de cada tipo de página está en `COMPOSICION.md` §5, y hay páginas
completas listas para copiar en `recetas/`.

## 5. Buscas un nombre en inglés y no existe

Aurora 7 usa nombres en castellano en algunas familias. Aliases verificados:

| Buscas | Usa |
|---|---|
{filas_alias}

Los nombres de la tabla anterior son los que existen de verdad. Si una clase no
aparece en `components.json`, **no la inventes**.

## 6. Léxico de modificadores (igual en los 15 packs)

- **Tamaño**: `--2xs --xs --sm --lg --xl`
- **Tono**: `--brand --accent --success --warning --danger --info --neutral`
- **Énfasis**: `--solid --soft --outline --ghost`
- **Disposición**: `--vertical --horizontal --inline --compact --spacious --center --between --end`
- **Forma**: `--square --rounded --pill` · **Elevación**: `--flat --raised`
- **Estado**: `.is-active .is-disabled .is-loading .is-done .is-error .is-selected` o `[aria-current] [aria-selected]`

## 7. Marca: elige 2 colores y todo el sistema cambia

La marca **no se toca en CSS**: se elige con un atributo en el `<html>`.

```html
<html lang="es" data-nz-theme="light" data-nz-marca="indigo">
```

- Presets incluidos: `aurora` (defecto, azul + naranja), `indigo`, `esmeralda`, `violeta`,
  `carmesi`. Un `data-nz-marca` desconocido cae en `aurora` sin romper nada.
- Marca propia: `python scripts/generar-marca.py miweb "#0ea5e9" "#f43f5e"` → `marcas/miweb.css`.
  El generador crea la rampa en OKLCH, la ancla a tu color y avisa si necesita ajuste por contraste.
- Todo lo demás (`--nz-brand*`, `--nz-accent*`, foco, sombras de color y **el modo oscuro**)
  se **deriva solo** de esas dos rampas.

Solo si necesitas afinar algo suelto (fuente, radio, ancho):

```css
:root {{
  --nz-font: "Inter", system-ui, sans-serif;
  --nz-radius-md: 12px;
  --nz-container-max: 72rem;
}}
```

Los {len(tokens)} tokens están inventariados en `components.json` (sección
`tokens_def`, con nombre, valor y sección). Nada fuera de ese catálogo.

## 8. Anti-patrones (NO lo hagas)

- ❌ Pegar el CSS de los packs en el prompt (250 KB ≈ 60.000 tokens). Enlaza por CDN.
- ❌ Inventar clases (`nz-gradient-text`, `nz-btn--glass-liquid-brand`, `nz-card--glass`): no existen aquí. Es la doctrina de Aurora v6, **jubilada**: Aurora 7 es sólido, sin glass ni gradientes.
- ❌ Escribir colores a mano (`#2563eb`, `rgb(...)`): usa tokens `var(--nz-*)`.
- ❌ Gradientes, `backdrop-filter` o `!important`: prohibidos por el manifiesto y la CI los detecta.
- ❌ Clases globales sin `.nz-`: romperías la convivencia con otros frameworks.
- ❌ Desktop-first: el sistema es mobile-first (base 1 columna, `min-width` para crecer).
- ❌ Enlazar `@master` en producción: pinea la versión (`@v{VERSION}`) o jsDelivr te servirá CSS viejo desde su caché.

## 9. Verificar antes de entregar

```bash
python scripts/auditar-uso.py tu-pagina.html   # lint del HTML consumidor
python scripts/validar-css.py                  # manifiesto + cobertura del sistema
```

`auditar-uso.py` te dice: clases inventadas, packs que te faltan por enlazar,
colores a mano, gradientes, desktop-first y atribución. EJECÚTALO sobre tu HTML
antes de darlo por bueno y corrige lo que marque.

Recetas completas y funcionando en `examples/` (login, dashboard, landing,
chat-ia, forms): cópialas como punto de partida.

Docs hermanas: `AGENTS.md` (reglas duras del repo), `components.json` (API
completa machine-readable), `paginas/` (catálogo con una demo viva por objeto),
`README.md`.

Hecho con ❤️ por David Antizar
"""
    (ROOT / "LLM.md").write_text(llm, encoding="utf-8")
    print(f"components.json → {len(objetos)} familias, {total_clases} clases, "
          f"{len(tokens)} tokens (+{len(dark)} dark), {len(alias_validos)} alias, "
          f"{len(COMBOS)} combos")
    print(f"LLM.md → {len(llm)} bytes")


if __name__ == "__main__":
    main()
