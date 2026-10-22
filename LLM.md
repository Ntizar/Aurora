# Aurora — guía de decisión para agentes

Design system CSS puro, sin dependencias ni build. 2195 objetos en 18 categorías.
**No pegues el CSS en el prompt**: enlaza por CDN y usa las clases de esta guía.

## 1. Mínimo obligatorio

```html
<html lang="es" data-nz-theme="light">
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/tokens.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/all.css">
</head>
<body class="nz">
```

Ojo: el `<html lang="es" data-nz-theme="light">` y el `<body class="nz">` son el
elemento raíz del documento, no un fragmento — el snippet de arriba muestra dónde
van cada uno. Dark mode: cambia a `data-nz-theme="dark"` en el `<html>`.

## 2. ¿Qué packs enlazo según lo que construyo?

| Tipo de página | CDN | Qué lleva dentro |
|---|---|---|
| landing | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p6-feedback.css, p10-commerce.css, p11-social.css` | hero + features + pricing + footer + atribución |
| dashboard | `tokens.css` + `p1-layout.css, p2-navigation.css, p3-typography.css, p4-actions.css, p8-data.css, p13-charts.css` | appshell + navbar + KPIs + tablas + gráficos |
| chat-ia | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p5-forms.css, p14-ai.css` | chat + prompt + toolcall + taskplan + adjuntos |
| login-form | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p5-forms.css, p6-feedback.css` | card centrada + field + input + botón + alerta de error |
| escritorio-app | `tokens.css` + `p1-layout.css, p2-navigation.css, p3-typography.css, p4-actions.css, p6-feedback.css, p8-data.css, p15-apps.css` | window + appnav + kanban/agenda + statusbar |
| e-commerce | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p10-commerce.css, p8-data.css` | producto + cart + checkout-steps + pricetable |
| charla-beats | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p18-escenario.css` | lienzo 16:9 + titular/editorial/numeral + nodos del diagrama + QR de cierre |
| prototipo | `tokens.css` + `all.css` | exploración rápida: un solo enlace con todos los packs |

Carga **solo los packs que uses** en producción (cada uno pesa 12-40 KB) o
`packs/all.css` para prototipos. `tokens.css` siempre primero.

**Esqueletos listos para arrancar** (markup de cada tipo de página con las
clases reales del sistema, extraído y validado de las demos — cópialos):

- `bloques/combos/charla-beats.html` — esqueleto **charla-beats**: `nz-recorrido`, `nz-escenario`, `nz-nodo`, `nz-qr`
- `bloques/combos/chat-ia.html` — esqueleto **chat-ia**: `nz-chat`, `nz-prompt`, `nz-toolcall`, `nz-taskplan`
- `bloques/combos/dashboard.html` — esqueleto **dashboard**: `nz-navbar`, `nz-dash-grid`, `nz-kpi`, `nz-table`, `nz-chart`, `nz-chart-bar`
- `bloques/combos/e-commerce.html` — esqueleto **e-commerce**: `nz-product`, `nz-cart`, `nz-checkout-steps`, `nz-pricetable`
- `bloques/combos/escritorio-app.html` — esqueleto **escritorio-app**: `nz-window`, `nz-appnav`, `nz-kanban`, `nz-statusbar`
- `bloques/combos/landing.html` — esqueleto **landing**: `nz-hero-bleed`, `nz-thirds`, `nz-plans`, `nz-badge`, `nz-footer`
- `bloques/combos/login-form.html` — esqueleto **login-form**: `nz-article`, `nz-h2`, `nz-lead`, `nz-field`, `nz-btn`, `nz-alert`
- `bloques/combos/prototipo.html` — esqueleto **prototipo**: `nz-btn`, `nz-field`, `nz-alert`, `nz-kpi`

La lista completa de familias y su fichero está en `components.json`
(clave `combosEsqueleto`).

## 3. Mapa de categorías (API completa en `components.json`)

| Categoría | Pack | Objetos clave |
|---|---|---|
| 01 · Layout y estructura | `p1-layout.css` | `nz-appshell`, `nz-article`, `nz-aside`, `nz-aspect`… |
| 02 · Navegación | `p2-navigation.css` | `nz-breadcrumb`, `nz-dropdown`, `nz-menu`, `nz-navbar`… |
| 03 · Tipografía | `p3-typography.css` | `nz--leading-normal`, `nz--leading-snug`, `nz--leading-tight`, `nz--tracking-caps`… |
| 04 · Acciones y botones | `p4-actions.css` | `nz-btn`, `nz-btn-group`, `nz-cta`, `nz-fab`… |
| 05 · Formularios e inputs | `p5-forms.css` | `nz-checkbox`, `nz-field`, `nz-fieldset`, `nz-filezona`… |
| 06 · Feedback y estados | `p6-feedback.css` | `nz-alert`, `nz-badge`, `nz-banner`, `nz-callout`… |
| 07 · Overlays y diálogo | `p7-overlays.css` | `nz-backdrop`, `nz-cmd`, `nz-confirm`, `nz-drawer`… |
| 08 · Datos, tablas y listas | `p8-data.css` | `nz-arbol`, `nz-compare`, `nz-datagrid`, `nz-dl`… |
| 09 · Media e iconografía | `p9-media.css` | `nz-audio`, `nz-avatar`, `nz-avatar-group`, `nz-bgimg`… |
| 10 · Comercio y producto | `p10-commerce.css` | `nz-cart`, `nz-cart-item`, `nz-checkout-steps`, `nz-compare-bar`… |
| 11 · Social y marketing | `p11-social.css` | `nz-activity`, `nz-comment`, `nz-cta-banner`, `nz-feed`… |
| 12 · Accesibilidad y sistema | `p12-system.css` | `nz-a11y-badge`, `nz-atajo-teclado`, `nz-contrast`, `nz-focus-accent`… |
| 13 · Gráficos y visualización | `p13-charts.css` | `nz-bullet`, `nz-chart`, `nz-chart-bar`, `nz-chart-compare`… |
| 14 · IA y agentes | `p14-ai.css` | `nz-agent-card`, `nz-approval`, `nz-attach`, `nz-chat`… |
| 15 · Apps y escritorio | `p15-apps.css` | `nz-actbar`, `nz-agenda`, `nz-appempty`, `nz-appnav`… |
| 16 · Cristal (capa de estilo) | `p16-cristal.css` | `nz-cristal`, `nz-cristal-barra` |
| 17 · Patrones compuestos | `p17-patrones.css` | `nz-agenda-disponibilidad`, `nz-asistente-pasos`, `nz-aviso-accion`, `nz-aviso-sistema`… |
| 18 · Escenario (charlas en beats) | `p18-escenario.css` | `nz-enlace`, `nz-esc-dato`, `nz-esc-editorial`, `nz-esc-etiqueta`… |

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
338 iconos numerados (`nz-i-001`…), cada uno con número estable, nombre castellano y
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
| «accordion» | `nz-collapsible` |
| «alert» | `nz-alert` |
| «avatar» | `nz-avatar` |
| «backdrop» | `nz-backdrop` |
| «badge» | `nz-badge` |
| «banner» | `nz-banner` |
| «bar-chart» | `nz-chart-bar` |
| «bento-grid» | `nz-bento` |
| «blockquote» | `nz-blockquote` |
| «breadcrumb» | `nz-breadcrumb` |
| «button» | `nz-btn` |
| «callout» | `nz-callout` |
| «cart» | `nz-cart` |
| «chart» | `nz-chart` |
| «chat» | `nz-chat` |
| «checkbox» | `nz-checkbox` |
| «checkout» | `nz-checkout-steps` |
| «chip» | `nz-chip` |
| «cloud-logo» | `nz-logo-nube` |
| «code» | `nz-code` |
| «code-editor» | `nz-codepad` |
| «collapsible» | `nz-collapsible` |
| «command-palette» | `nz-cmd` |
| «comment» | `nz-comment` |
| «confirm-dialog» | `nz-confirm` |
| «container» | `nz-container` |
| «context-menu» | `nz-menu-pop` |
| «countdown» | `nz-countdown` |
| «dashboard-grid» | `nz-dash-grid` |
| «data-grid» | `nz-datagrid` |
| «dialog» | `nz-modal` |
| «diff» | `nz-diff` |
| «divider» | `nz-divider` |
| «dock» | `nz-dock` |
| «donut-chart» | `nz-chart-donut` |
| «drawer» | `nz-drawer` |
| «dropdown» | `nz-dropdown` |
| «dropzone» | `nz-filezona` |
| «empty» | `nz-empty` |
| «empty-state» | `nz-empty` |
| «error-hint» | `nz-hint-error` |
| «error-state» | `nz-errorstate` |
| «estado-vacio» | `nz-estado-vacio` |
| «fab» | `nz-fab` |
| «faq» | `nz-preguntas-frecuentes` |
| «feed» | `nz-feed` |
| «fieldset» | `nz-fieldset` |
| «figure» | `nz-figura` |
| «file-dropzone» | `nz-filezona` |
| «file-upload» | `nz-filezona` |
| «floating-action-button» | `nz-fab` |
| «footer» | `nz-footer` |
| «form» | `nz-field` |
| «form-grid» | `nz-formgrid` |
| «gallery» | `nz-galeria` |
| «gauge» | `nz-chart-gauge` |
| «grid» | `nz-grid-12` |
| «guided-empty-state» | `nz-estado-vacio` |
| «guided-empty-state-es» | `nz-estado-vacio` |
| «hashtag» | `nz-hashtag` |
| «header» | `nz-header` |
| «heatmap» | `nz-heatmap` |
| «hero» | `nz-hero-bleed` |
| «hide-desktop» | `nz-hide-escritorio` |
| «hide-mobile» | `nz-hide-movil` |
| «input» | `nz-input` |
| «kanban» | `nz-kanban` |
| «kbd» | `nz-atajo-teclado` |
| «keyboard-shortcut» | `nz-atajo-teclado` |
| «kpi-card» | `nz-kpi` |
| «label» | `nz-label` |
| «lightbox» | `nz-lightbox` |
| «line-chart» | `nz-chart-line` |
| «link» | `nz-link` |
| «list» | `nz-list` |
| «logo-cloud» | `nz-logos` |
| «map-placeholder» | `nz-mapa-placeholder` |
| «masonry» | `nz-masonry` |
| «mention» | `nz-mention` |
| «menu» | `nz-menu` |
| «message» | `nz-msg` |
| «meter» | `nz-meter` |
| «mobile-nav» | `nz-navbar` |
| «modal» | `nz-modal` |
| «navbar» | `nz-navbar` |
| «note» | `nz-nota` |
| «notification» | `nz-notif` |
| «offcanvas» | `nz-offcanvas` |
| «otp-input» | `nz-otp` |
| «pagination» | `nz-pagination` |
| «password» | `nz-password` |
| «popover» | `nz-popover` |
| «popup-menu» | `nz-menu-pop` |
| «post» | `nz-post` |
| «pricing» | `nz-plans` |
| «pricing-plan» | `nz-plan` |
| «pricing-plans» | `nz-plans` |
| «pricing-table» | `nz-pricetable` |
| «progress» | `nz-progress` |
| «prompt» | `nz-prompt` |
| «qr» | `nz-qr` |
| «qr-code» | `nz-qr` |
| «quote» | `nz-quote` |
| «radio» | `nz-radio` |
| «range-slider» | `nz-range` |
| «rating» | `nz-stars` |
| «scrim» | `nz-scrim` |
| «search» | `nz-search` |
| «segmented-control» | `nz-segmented` |
| «select» | `nz-select` |
| «share» | `nz-share` |
| «sheet» | `nz-sheet` |
| «show-desktop» | `nz-show-escritorio` |
| «show-mobile» | `nz-show-movil` |
| «sidebar» | `nz-sidebar` |
| «skeleton» | `nz-skeleton` |
| «skip-link» | `nz-skip-link` |
| «slider» | `nz-range` |
| «social-links» | `nz-social` |
| «spacer» | `nz-spacer` |
| «sparkline» | `nz-sparkline` |
| «spinner» | `nz-spinner` |
| «split-pane» | `nz-splitpane` |
| «sr-only» | `nz-visually-hidden` |
| «stack» | `nz-stack` |
| «stars» | `nz-stars` |
| «stat-card» | `nz-kpi` |
| «statusbar» | `nz-statusbar` |
| «stepper» | `nz-stepper` |
| «switch» | `nz-switch` |
| «table» | `nz-table` |
| «table-of-contents» | `nz-toc` |
| «tabs» | `nz-tabs` |
| «task-plan» | `nz-taskplan` |
| «textarea» | `nz-textarea` |
| «theme-badge» | `nz-tema-badge` |
| «thinking-indicator» | `nz-thinking` |
| «timeline» | `nz-timeline` |
| «toast» | `nz-toast` |
| «toc» | `nz-toc` |
| «tool-call» | `nz-toolcall` |
| «toolbar» | `nz-toolbar` |
| «tooltip» | `nz-popover` |
| «tree» | `nz-arbol` |
| «tree-view» | `nz-tree` |
| «truncate» | `nz-truncate` |
| «typing-indicator» | `nz-thinking` |
| «upload» | `nz-filezona` |
| «visually-hidden» | `nz-visually-hidden` |
| «window» | `nz-window` |

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
:root {
  --nz-radius-md: 12px;
  --nz-container-max: 72rem;
}
```

Los 236 tokens están inventariados en `components.json` (sección
`tokens_def`, con nombre, valor y sección). Nada fuera de ese catálogo.

## 8. Anti-patrones (NO lo hagas)

- ❌ Pegar el CSS de los packs en el prompt (250 KB ≈ 60.000 tokens). Enlaza por CDN.
- ❌ Inventar clases (`nz-gradient-text`, `nz-btn--glass-liquid-brand`, `nz-card--glass`): no existen aquí. Es la doctrina de Aurora v6, **jubilada**: Aurora es sólido, sin glass ni gradientes.
- ❌ Escribir colores a mano (`#2563eb`, `rgb(...)`): usa tokens `var(--nz-*)`.
- ❌ Texto blanco sobre relleno de acento o texto acento plano (`color: var(--nz-accent)`):
  en claro cae a 2,80:1 y falla WCAG. Texto de acento → `var(--nz-accent-text)`;
  tinta sobre relleno de acento → `var(--nz-accent-ink)`. La auditoría
  `scripts/auditar-contraste.py` lo caza.
- ❌ Gradientes, `backdrop-filter` o `!important`: prohibidos por el manifiesto y la CI los detecta.
- ❌ Clases globales sin `.nz-`: romperías la convivencia con otros frameworks.
- ❌ Desktop-first: el sistema es responsive first (base móvil en 1 columna, crece con
  `min-width` hasta el escritorio, y los objetos responden a su contenedor).
- ❌ Dejar media pantalla vacía en un monitor grande: un panel o una herramienta usan
  `.nz-container--app`; el lienzo ya crece solo hasta 96rem desde 1440px.
- ❌ `font-weight` a mano (700/800 sueltos) o negritas porque sí: usa `--nz-peso-*`.
  El 800 no existe en el sistema y nada por debajo de 16px lleva 700.
- ❌ Texto de interfaz a 12px: los 12px son para datos, no para etiquetas.
- ❌ Enlazar Google Fonts (o cualquier CDN de fuentes): `tokens.css` ya sirve la fuente.
- ❌ Enlazar `@master` en producción: pinea la versión (`@v10.1.0`) o jsDelivr te servirá CSS viejo desde su caché.

## 8b. Canales: qué versión enlazar

Dos canales, un sistema. La regla de oro: **nunca `@master`**.

| Canal | URL | Cuándo |
|---|---|---|
| vivo | `@v10` | webs propias: recibe cada release 9.x sin tocarlas |
| congelado | `@10.1.0` | entregas a cliente: reproducible dentro de dos años |

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
índice machine-readable: 411 familias con su markup, 236 tokens,
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
