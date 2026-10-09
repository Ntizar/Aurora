<div align="center">

# Aurora

**Design system CSS de Ntizar — un solo sistema para montar cualquier web.**

2.178 objetos · 409 familias · 650 demos en vivo · 18 categorías · 0 gradientes · 0 glass

[![CI — validación del manifiesto](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml)
[![GitHub Pages](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml)
![versión](https://img.shields.io/badge/versi%C3%B3n-8.3.0-2563eb)
![objetos](https://img.shields.io/badge/objetos-2.176-2563eb)
![demos](https://img.shields.io/badge/demos-576-f97316)

**[Explorar el catálogo →](https://ntizar.github.io/Aurora/)**

</div>

---

Aurora no es una colección de snippets: es un **sistema con contrato**. Cada objeto existe si y solo si está demostrado en vivo, cada clase tiene un único dueño, y una CI lo verifica en cada push. Si el catálogo lo muestra, funciona; si algo se rompe, el push se pone rojo antes de publicarse.

## El manifiesto

| | |
|---|---|
| 🎨 | **Azul `#2563eb`** primario · **Naranja `#f97316`** acento — nunca fundidos |
| 🚫 | **0 gradientes** · **0 glass** · **0 colores a mano** · **0 `!important`*** |
| 📱 | **Mobile-first** real: base 1 columna, breakpoints con `min-width` |
| 👆 | **Táctil 44px** · safe-area iOS |
| 🌗 | **Light + dark** solo con tokens temáticos |
| 🔍 | **Si no aparece en el catálogo, no existe** — cada clase declarada tiene demo |

> \* La única excepción, declarada y justificada: `.nz-visually-hidden`, que necesita ganar a cualquier otra regla por diseño.

## Las 15 categorías

| # | Categoría | Pack | Objetos | Demos |
|---|---|---|---:|---:|
| 01 | Layout y estructura | `p1-layout.css` | 178 | 51 |
| 02 | Navegación | `p2-navigation.css` | 77 | 35 |
| 03 | Tipografía | `p3-typography.css` | 130 | 42 |
| 04 | Acciones y botones | `p4-actions.css` | 78 | 16 |
| 05 | Formularios e inputs | `p5-forms.css` | 102 | 44 |
| 06 | Feedback y estados | `p6-feedback.css` | 153 | 52 |
| 07 | Overlays y diálogo | `p7-overlays.css` | 118 | 34 |
| 08 | Datos, tablas y listas | `p8-data.css` | 145 | 40 |
| 09 | Media e iconografía | `p9-media.css` | 112 | 41 |
| 10 | Comercio y producto | `p10-commerce.css` | 156 | 48 |
| 11 | Social y marketing | `p11-social.css` | 107 | 39 |
| 12 | Accesibilidad y sistema | `p12-system.css` | 80 | 29 |
| 13 | Gráficos y visualización | `p13-charts.css` | 210 | 36 |
| 14 | IA y agentes | `p14-ai.css` | 180 | 32 |
| 15 | Apps y escritorio | `p15-apps.css` | 74 | 37 |
| | **Total** | | **1.900** | **576** |

## Uso

**En una página real** — enlaza los tokens y solo los packs que necesites:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.3.0/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.3.0/packs/p4-actions.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.3.0/packs/p5-forms.css">
```

**Todo de golpe** — para prototipar:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.3.0/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.3.0/packs/all.css">
```

El `body` lleva `class="nz"` y el tema se fija en el `<html>`:

```html
<html lang="es" data-nz-theme="light">   <!-- o "dark" -->
```

Todos los componentes comparten el prefijo `.nz-` y los tokens `--nz-*`: nada colisiona con otros frameworks ni con tu propio CSS.

## Consumo por agentes (IA)

Aurora está diseñado para que un agente genere HTML correcto a la primera, sin leer los packs:

1. **`LLM.md`** (~9 KB) — guía de decisión: qué packs enlazar según el tipo de página (combos), qué clases existen, alias inglés→clase (`tree` → `nz-arbol`) y anti-patrones.
2. **`components.json`** — API machine-readable completa: 349 familias con sus clases, modificadores y partes, **los 145 tokens** inventariados, alias y combos.
3. **`examples/`** — 5 recetas completas y funcionando (login, dashboard, landing, chat-ia, forms): se copian como punto de partida, con carga mínima de packs y markup verificado.
4. **`scripts/auditar-uso.py`** — el lint del consumidor: le pasas el HTML generado y te dice clases inventadas, packs que faltan por enlazar, gradientes, colores a mano, desktop-first y atribución. Ejecútalo **antes de dar por bueno cualquier HTML**:

```bash
python scripts/auditar-uso.py tu-pagina.html      # informe con fallos y avisos
python scripts/auditar-uso.py --selftest          # prueba de la propia herramienta
```

Nada de esto se desincroniza: la CI regenera `LLM.md`/`components.json` y compara, comprueba que las versiones de doc y tags de git coinciden y verifica que el lint funciona.

## Estructura

```
Aurora-7/
├── index.html          # portada: manifiesto, buscador de objetos, 15 categorías
├── tokens.css          # fuente única de verdad de los tokens
├── packs/
│   ├── p0-catalog.css  # shell del catálogo (.cat-*) — NO define componentes .nz-*
│   ├── p1 … p15.css    # un pack por categoría (ver tabla)
│   └── all.css         # todos los packs en un enlace (@import)
├── specs/              # FUENTE DE VERDAD de las demos (01.json … 15.json)
├── paginas/            # catálogo generado (01-…-15-*.html)
├── js/catalog.js       # buscador (tecla /), filtro, tema, «ver código» y copiar
├── datos/objetos.json  # índice de los 1.900 objetos para el buscador
├── audit/              # informe de auditoría generado (AUDITORIA.md + index.html)
├── examples/           # 5 recetas completas para agentes (login, dashboard, landing, chat-ia, forms)
├── scripts/
│   ├── build-catalog.py   # genera páginas + portada + índice desde specs/
│   ├── audit-catalog.py   # auditoría campo a campo
│   ├── validar-css.py     # manifiesto, cobertura, literales, versión y sincronía (lo que corre CI)
│   ├── audit-tema.py      # ¿todo sobrevive al modo oscuro? (lo que corre CI)
│   ├── audit-a11y.py      # etiquetas, teclado y foco de las demos (CI)
│   ├── audit-html.py      # genera el informe navegable de auditoría
│   ├── generar-llm-docs.py # genera LLM.md + components.json (tokens, alias, combos)
│   ├── auditar-uso.py     # lint del HTML consumidor: clases inventadas, packs, manifiesto
│   └── extraer-specs.py   # utilidad: reconstruye specs/ desde las páginas
├── LLM.md              # guía de decisión para agentes (~9 KB, en vez de 250 KB de CSS)
├── AGENTS.md           # reglas duras del repo (qué se toca y qué no)
└── components.json     # API machine-readable: familias, clases, tokens, alias y combos
```

## Léxico de modificadores

Los 15 packs hablan el mismo idioma — si sabes usar un objeto, sabes usarlos todos:

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
2. **Todos los valores son tokens `--nz-*`** — nunca un hex suelto ni un `16px` a mano
3. **Sin `!important`** (salvo el hueso duro de `.nz-visually-hidden`)
4. **BEM** para componentes: `.nz-card__body--featured`
5. **Una clase, un dueño**: cada objeto se declara en un único pack
6. **Si no aparece en el catálogo, no existe**: cada clase declarada tiene demo
7. **Accesible de serie**: todo control lleva etiqueta y el patrón sin JS usa
   `.nz-vh` (oculto pero focusable), nunca el atributo `hidden`

## Garantías automáticas

Cinco puertas comprueban que el sistema no se degrada. Si alguna falla, el push se
pone en rojo **antes** de publicarse:

| Puerta | Qué vigila |
|---|---|
| `validar-css.py` | 0 gradientes/glass/colores a mano, 0 `!important` sin justificar, tokens existentes, dueño único por clase, cobertura clase↔demo, HTML bien formado, cada página carga los packs que usa y ningún literal que ya tenga token |
| `audit-tema.py` | que ninguna regla pinte texto o bordes de paleta sin declarar su propio fondo: eso es lo que rompe el modo oscuro |
| `audit-a11y.py` | `alt`, etiquetas asociadas, texto accesible, `aria-*` que apunten a ids reales, `label[for]` correctos, `tabindex` y orden de tabulación |
| `audit-catalog.py` | auditoría campo a campo: lo declarado contra lo demostrado |
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

**Para agentes IA**: lee `LLM.md` primero (~5 KB con todo lo necesario para decidir), consulta `components.json` cuando necesites la API exacta de una familia, y respeta `AGENTS.md`. La CI (`.github/workflows/validar.yml`) comprueba en cada push que el manifiesto se cumple, que ninguna clase se declara dos veces, que todo lo declarado tiene demo y que el catálogo commiteado coincide con `specs/`. Si algo falla, el push se pone en rojo antes de publicarse.

---

Hecho con ❤️ por David Antizar
