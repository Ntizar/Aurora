# Aurora — guía de decisión para agentes

Design system CSS puro, sin dependencias ni build. 1907 objetos en 15 categorías.
**No pegues el CSS en el prompt**: enlaza por CDN y usa las clases de esta guía.

## 1. Mínimo obligatorio

```html
<html lang="es" data-nz-theme="light">
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.0.0/tokens.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.0.0/packs/all.css">
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
| escritorio-app | `tokens.css` + `p1-layout.css, p2-navigation.css, p3-typography.css, p4-actions.css, p8-data.css, p15-apps.css` | window + appnav + kanban/agenda + statusbar |
| e-commerce | `tokens.css` + `p1-layout.css, p3-typography.css, p4-actions.css, p10-commerce.css, p8-data.css` | producto + cart + checkout-steps + pricetable |
| prototipo | `tokens.css` + `all.css` | exploración rápida: un solo enlace con los 15 packs |

Carga **solo los packs que uses** en producción (cada uno pesa 12-40 KB) o
`packs/all.css` para prototipos. `tokens.css` siempre primero.

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

Aurora usa nombres en castellano en algunas familias. Aliases verificados:

| Buscas | Usa |
|---|---|
| «cloud-logo» | `nz-logo-nube` |
| «command-palette» | `nz-cmd` |
| «confirm-dialog» | `nz-confirm` |
| «dashboard-grid» | `nz-dash-grid` |
| «data-grid» | `nz-datagrid` |
| «empty-state» | `nz-empty` |
| «error-hint» | `nz-hint-error` |
| «error-state» | `nz-errorstate` |
| «figure» | `nz-figura` |
| «file-dropzone» | `nz-filezona` |
| «form-grid» | `nz-formgrid` |
| «gallery» | `nz-galeria` |
| «hide-desktop» | `nz-hide-escritorio` |
| «hide-mobile» | `nz-hide-movil` |
| «kbd» | `nz-atajo-teclado` |
| «keyboard-shortcut» | `nz-atajo-teclado` |
| «logo-cloud» | `nz-logos` |
| «map-placeholder» | `nz-mapa-placeholder` |
| «message» | `nz-msg` |
| «mobile-nav» | `nz-navbar` |
| «note» | `nz-nota` |
| «popup-menu» | `nz-menu-pop` |
| «pricing-plan» | `nz-plan` |
| «pricing-plans» | `nz-plans` |
| «show-desktop» | `nz-show-escritorio` |
| «show-mobile» | `nz-show-movil` |
| «social-links» | `nz-social` |
| «spinner» | `nz-spinner` |
| «task-plan» | `nz-taskplan` |
| «theme-badge» | `nz-tema-badge` |
| «tooltip» | `nz-popover` |
| «tree» | `nz-arbol` |

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
:root {
  --nz-font: "Inter", system-ui, sans-serif;
  --nz-radius-md: 12px;
  --nz-container-max: 72rem;
}
```

Los 170 tokens están inventariados en `components.json` (sección
`tokens_def`, con nombre, valor y sección). Nada fuera de ese catálogo.

## 8. Anti-patrones (NO lo hagas)

- ❌ Pegar el CSS de los packs en el prompt (250 KB ≈ 60.000 tokens). Enlaza por CDN.
- ❌ Inventar clases (`nz-gradient-text`, `nz-btn--glass-liquid-brand`, `nz-card--glass`): no existen aquí. Es la doctrina de Aurora v6, **jubilada**: Aurora es sólido, sin glass ni gradientes.
- ❌ Escribir colores a mano (`#2563eb`, `rgb(...)`): usa tokens `var(--nz-*)`.
- ❌ Gradientes, `backdrop-filter` o `!important`: prohibidos por el manifiesto y la CI los detecta.
- ❌ Clases globales sin `.nz-`: romperías la convivencia con otros frameworks.
- ❌ Desktop-first: el sistema es mobile-first (base 1 columna, `min-width` para crecer).
- ❌ Enlazar `@master` en producción: pinea la versión (`@v8.0.0`) o jsDelivr te servirá CSS viejo desde su caché.

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
