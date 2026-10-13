<div align="center">

# Aurora

**Design system CSS de Ntizar — un solo sistema para montar cualquier web.**

2.184 objetos · 409 familias · 653 demos en vivo · 18 categorías · 0 gradientes · 0 glass

[![CI — validación del manifiesto](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml)
[![GitHub Pages](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml)
![versión](https://img.shields.io/badge/versi%C3%B3n-8.4.2-2563eb)
![objetos](https://img.shields.io/badge/objetos-2.184-2563eb)
![demos](https://img.shields.io/badge/demos-653-f97316)

**[Explorar el catálogo →](https://ntizar.github.io/Aurora/)**

</div>

---

Aurora no es una colección de snippets: es un **sistema con contrato**. Cada objeto existe si y solo si está demostrado en vivo, cada clase tiene un único dueño, y una CI lo verifica en cada push. Si el catálogo lo muestra, funciona; si algo se rompe, el push se pone en rojo antes de publicarse.

## El manifiesto

| | |
|---|---|
| 🎨 | **Azul `#2563eb`** marca (estructura) · **Naranja `#f97316`** acento (**el dato que importa**) — nunca fundidos, y el acento siempre presente |
| 🚫 | **0 gradientes** · **0 glass** · **0 colores a mano** · **0 `!important`*** |
| 📱 | **Mobile-first** real: base 1 columna, breakpoints con `min-width` |
| 🖥️ | **Escritorio que crece**: lienzo 72 → 84 → 96rem (≥1200 / ≥1440) y `.nz-container--app` para herramientas. La letra no crece con el monitor; crece el lienzo |
| 🔤 | **Fuente servida por el sistema**: Inter variable viaja en `tokens.css`. La misma letra en Windows, Android, Linux y en una captura headless |
| ⚖️ | **Pesos por token** (`--nz-peso-*`): 400 cuerpo · 500 apoyo · 600 interfaz · 700 titulares. **El 800 está retirado**; nada por debajo de 16px va en 700 |
| 👆 | **Táctil 44px** · safe-area iOS |
| 🌗 | **Light + dark** solo con tokens temáticos |
| 🔍 | **Si no aparece en el catálogo, no existe** — cada clase declarada tiene demo |

> \* La única excepción, declarada y justificada: `.nz-visually-hidden`, que necesita ganar a cualquier otra regla por diseño.

## Las 18 categorías

| # | Categoría | Pack | Objetos | Demos |
|---|---|---|---:|---:|
| 01 | Layout y estructura | `p1-layout.css` | 178 | 52 |
| 02 | Navegación | `p2-navigation.css` | 78 | 36 |
| 03 | Tipografía | `p3-typography.css` | 135 | 44 |
| 04 | Acciones y botones | `p4-actions.css` | 78 | 16 |
| 05 | Formularios e inputs | `p5-forms.css` | 102 | 44 |
| 06 | Feedback y estados | `p6-feedback.css` | 153 | 52 |
| 07 | Overlays y diálogo | `p7-overlays.css` | 118 | 34 |
| 08 | Datos, tablas y listas | `p8-data.css` | 145 | 40 |
| 09 | Media e iconografía | `p9-media.css` | 119 | 42 |
| 10 | Comercio y producto | `p10-commerce.css` | 156 | 48 |
| 11 | Social y marketing | `p11-social.css` | 107 | 39 |
| 12 | Accesibilidad y sistema | `p12-system.css` | 80 | 29 |
| 13 | Gráficos y visualización | `p13-charts.css` | 216 | 38 |
| 14 | IA y agentes | `p14-ai.css` | 180 | 32 |
| 15 | Apps y escritorio | `p15-apps.css` | 74 | 37 |
| 16 | Cristal (capa de estilo) | `p16-cristal.css` | 8 | 5 |
| 17 | Patrones compuestos | `p17-patrones.css` | 224 | 47 |
| 18 | Escenario (charlas en beats) | `p18-escenario.css` | 33 | 18 |
| | **Total** | | **2.184** | **653** |

## Uso

**En una página real** — enlaza los tokens y solo los packs que necesites:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.4.2/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.4.2/packs/p4-actions.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.4.2/packs/p5-forms.css">
```

**Todo de golpe** — para prototipar:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.4.2/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.4.2/packs/all.css">
```

El `body` lleva `class="nz"` y el tema se fija en el `<html>`:

```html
<html lang="es" data-nz-theme="light">   <!-- o "dark" -->
```

**No hay que enlazar fuentes**: `tokens.css` sirve Inter variable desde el propio repo (los `.woff2` viven en `fuentes/`). Y el lienzo ya crece solo en escritorio: si es una herramienta, añade `.nz-container--app`.

Todos los componentes comparten el prefijo `.nz-` y los tokens `--nz-*`: nada colisiona con otros frameworks ni con tu propio CSS.

## Consumo por agentes (IA)

Aurora está diseñado para que un agente genere HTML correcto a la primera, sin leer los packs:

1. **`LLM.md`** (~12 KB) — guía de decisión: qué packs enlazar según el tipo de página (combos), qué clases existen, alias inglés→clase (`tree` → `nz-arbol`), reglas de tipografía y acento, y anti-patrones.
2. **`components.json`** — API machine-readable completa: **409 familias** con sus clases, modificadores y partes, los **189 tokens** inventariados, alias y combos.
3. **`COMPOSICION.md`** — el contrato de cómo se monta una página (14 leyes). Las clases correctas no bastan.
4. **`recetas/` y `examples/`** — páginas completas y funcionando (login, dashboard, admin, ajustes, informe, landing, chat-ia, forms): se copian como punto de partida.
5. **`scripts/auditar-uso.py`** — el lint del consumidor: le pasas el HTML generado y te dice clases inventadas, packs que faltan por enlazar, gradientes, colores a mano, negritas a mano, ausencia de acento, desktop-first y atribución. Ejecútalo **antes de dar por bueno cualquier HTML**:

```bash
python scripts/auditar-uso.py tu-pagina.html      # informe con fallos y avisos
python scripts/auditar-uso.py --selftest          # prueba de la propia herramienta
```

Nada de esto se desincroniza: la CI regenera `LLM.md`/`components.json` y compara, comprueba que las versiones de doc y tags de git coinciden y verifica que el lint funciona.

## Estructura

```
Aurora/
├── index.html          # portada: manifiesto, buscador de objetos, 18 categorías
├── tokens.css          # fuente única de verdad de los tokens (+ @font-face de Inter)
├── fuentes/            # Inter variable self-hosted (woff2 · latin y latin-ext)
├── packs/
│   ├── p0-catalog.css  # shell del catálogo (.cat-*) — NO define componentes .nz-*
│   ├── p1 … p18.css    # un pack por categoría (ver tabla)
│   └── all.css         # todos los packs en un enlace (@import)
├── marcas/             # presets de color (aurora, indigo, esmeralda, violeta, carmesí)
├── specs/              # FUENTE DE VERDAD de las demos (01.json … 18.json)
├── paginas/            # catálogo generado (01-…-18-*.html)
├── js/catalog.js       # buscador (tecla /), filtro, tema, «ver código» y copiar
├── datos/objetos.json  # índice de los 2.184 objetos para el buscador
├── audit/              # informe de auditoría generado (AUDITORIA.md + index.html)
├── recetas/ · examples/ # páginas completas para copiar
├── scripts/
│   ├── build-catalog.py    # genera páginas + portada + índice desde specs/
│   ├── audit-catalog.py    # auditoría campo a campo
│   ├── validar-css.py      # manifiesto, cobertura, literales, versión y sincronía (lo que corre CI)
│   ├── audit-tema.py       # ¿todo sobrevive al modo oscuro? (lo que corre CI)
│   ├── audit-a11y.py       # etiquetas, teclado y foco de las demos (CI)
│   ├── audit-html.py       # genera el informe navegable de auditoría
│   ├── auditar-movil.py    # mide desbordes y objetivos táctiles en móvil
│   ├── generar-llm-docs.py # genera LLM.md + components.json (tokens, alias, combos)
│   ├── auditar-uso.py      # lint del HTML consumidor (manifiesto + composición)
│   ├── traer-fuente.py     # descarga/actualiza los woff2 de Inter
│   └── extraer-specs.py    # utilidad: reconstruye specs/ desde las páginas
├── LLM.md              # guía de decisión para agentes (~12 KB, en vez de 250 KB de CSS)
├── COMPOSICION.md      # contrato de composición (14 leyes que el lint comprueba)
├── AGENTS.md           # reglas duras del repo (qué se toca y qué no)
└── components.json     # API machine-readable: familias, clases, tokens, alias y combos
```

## Léxico de modificadores

Los 18 packs hablan el mismo idioma — si sabes usar un objeto, sabes usarlos todos:

| Eje | Modificadores |
|---|---|
| Tamaño | `--2xs` `--xs` `--sm` `--lg` `--xl` |
| Tono | `--brand` `--accent` `--success` `--warning` `--danger` `--info` `--neutral` |
| Énfasis | `--solid` `--soft` `--outline` `--ghost` |
| Disposición | `--vertical` `--horizontal` `--inline` `--compact` `--spacious` `--center` `--between` `--end` |
| Forma | `--square` `--rounded` `--pill` |
| Elevación | `--flat` `--raised` |
| Estado | `.is-active` `.is-disabled` `.is-loading` `.is-done` `.is-error` `.is-empty` `.is-selected` o `[aria-current]` `[aria-selected]` `[aria-expanded]` |

## Reglas del sistema

1. **Todo lo público vive bajo `.nz-`**
2. **Todos los valores son tokens `--nz-*`** — nunca un hex suelto, un `16px` a mano ni un `font-weight: 700` suelto
3. **Sin `!important`** (salvo el hueso duro de `.nz-visually-hidden`)
4. **BEM** para componentes: `.nz-card__body--featured`
5. **Una clase, un dueño**: cada objeto se declara en un único pack
6. **Si no aparece en el catálogo, no existe**: cada clase declarada tiene demo
7. **Accesible de serie**: todo control lleva etiqueta y el patrón sin JS usa
   `.nz-vh` (oculto pero focusable), nunca el atributo `hidden`
8. **Tipografía con juicio**: 13px es el mínimo de interfaz (12px solo para datos),
   el peso es un token y el 800 no existe
9. **Escritorio de verdad**: el lienzo crece hasta 96rem y una herramienta usa
   `.nz-container--app`; medido a 1920px: una herramienta ocupa ≥95% del ancho (y hasta el
   100% con `--app`), y una página de contenido ya no baja del 80% (en v8.3 era el 60%)

## Garantías automáticas

Seis puertas comprueban que el sistema no se degrada. Si alguna falla, el push se
pone en rojo **antes** de publicarse:

| Puerta | Qué vigila |
|---|---|
| `validar-css.py` | 0 gradientes/glass/colores a mano, 0 `!important` sin justificar, tokens existentes, dueño único por clase, cobertura clase↔demo, HTML bien formado, cada página carga los packs que usa, ningún literal que ya tenga token y **nada por debajo de 16px en negrita** (`peso-por-tamano`) |
| `audit-tema.py` | que ninguna regla pinte texto o bordes de paleta sin declarar su propio fondo: eso es lo que rompe el modo oscuro |
| `audit-a11y.py` | `alt`, etiquetas asociadas, texto accesible, `aria-*` que apunten a ids reales, `label[for]` correctos, `tabindex` y orden de tabulación |
| `audit-catalog.py` | auditoría campo a campo: lo declarado contra lo demostrado |
| `auditar-uso.py --selftest` | que el lint del consumidor siga cazando los 13 defectos que debe cazar (clases inventadas, gradientes, negritas a mano, emojis…) |
| `node --check` + regeneración | que el catálogo commiteado coincida con `specs/` |

## Trabajar en el sistema

```bash
python scripts/build-catalog.py    # regenera páginas, portada e índice de objetos
python scripts/audit-catalog.py    # auditoría campo a campo → audit/
python scripts/audit-html.py       # informe navegable → audit/index.html
python scripts/validar-css.py      # manifiesto + cobertura (esto es lo que corre CI)
```

Las demos viven en `specs/NN.json`, no en el HTML. Para añadir un objeto nuevo:

1. Declara sus clases en el pack que le toque (`packs/pN-*.css`).
2. Añade su demo en `specs/NN.json` (titulo, tag, markup).
3. `python scripts/build-catalog.py` y listo.

**Para agentes IA**: lee `LLM.md` primero (~12 KB con todo lo necesario para decidir), consulta `components.json` cuando necesites la API exacta de una familia, y respeta `AGENTS.md` y `COMPOSICION.md`. La CI (`.github/workflows/validar.yml`) comprueba en cada push que el manifiesto se cumple, que ninguna clase se declara dos veces, que todo lo declarado tiene demo y que el catálogo commiteado coincide con `specs/`. Si algo falla, el push se pone en rojo antes de publicarse.

---

Hecho con ❤️ por David Antizar
