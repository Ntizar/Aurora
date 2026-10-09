# Auditoría campo a campo · Aurora

Generada por `scripts/audit-catalog.py` a partir de los packs CSS y de `specs/*.json`.

## Veredicto

| Comprobación | Valor | |
|---|---|---|
| Objetos declarados | 2176 |  |
| Familias de objeto | 408 |  |
| Demos en vivo | 648 |  |
| Clases usadas en demos | 2176 |  |
| Objetos fantasma (usados y no declarados) | 0 | 🟢 |
| Clases declaradas sin demo | 0 | 🟢 |
| Familias sin demo | 0 | 🟢 |
| Duplicados entre packs | 0 | 🟢 |
| Tokens inexistentes en uso | 0 | 🟢 |
| Gradientes fuera del cristal | 0 | 🟢 |
| Glass fuera del cristal | 0 | 🟢 |
| Colores a mano fuera de tokens.css | 0 | 🟢 |
| !important | 1 | 🟡 |

Familias sin ninguna variante (`--mod`): **163** de 408 — ahí está el margen de ampliación.

## 1. Por pack

| pack | líneas | objetos | familias | hex | grad. | glass | !imp. |
|---|---|---|---|---|---|---|---|
| p1-layout.css | 360 | 177 | 66 | 0 | 0 | 0 | 0 |
| p10-commerce.css | 258 | 156 | 22 | 0 | 0 | 0 | 0 |
| p11-social.css | 189 | 107 | 15 | 0 | 0 | 0 | 0 |
| p12-system.css | 143 | 80 | 25 | 0 | 0 | 0 | 1 |
| p13-charts.css | 363 | 216 | 22 | 0 | 0 | 0 | 0 |
| p14-ai.css | 287 | 180 | 28 | 0 | 0 | 0 | 0 |
| p15-apps.css | 364 | 74 | 30 | 0 | 0 | 0 | 0 |
| p16-cristal.css | 111 | 8 | 2 | 0 | 0 | 0 | 0 |
| p17-patrones.css | 659 | 224 | 46 | 0 | 0 | 0 | 0 |
| p18-escenario.css | 215 | 31 | 9 | 0 | 0 | 0 | 0 |
| p2-navigation.css | 179 | 78 | 10 | 0 | 0 | 0 | 0 |
| p3-typography.css | 198 | 130 | 41 | 0 | 0 | 0 | 0 |
| p4-actions.css | 172 | 78 | 7 | 0 | 0 | 0 | 0 |
| p5-forms.css | 278 | 102 | 20 | 0 | 0 | 0 | 0 |
| p6-feedback.css | 267 | 153 | 19 | 0 | 0 | 0 | 0 |
| p7-overlays.css | 207 | 118 | 12 | 0 | 0 | 0 | 0 |
| p8-data.css | 286 | 145 | 16 | 0 | 0 | 0 | 0 |
| p9-media.css | 205 | 119 | 18 | 0 | 0 | 0 | 0 |

## 2. Por categoría

| # | categoría | pack | objetos | familias | demos | sin demo | familias sin demo |
|---|---|---|---|---|---|---|---|
| 01 | Layout y estructura | p1-layout.css | 177 | 66 | 51 | 0 | 0 |
| 02 | Navegación | p2-navigation.css | 78 | 10 | 36 | 0 | 0 |
| 03 | Tipografía | p3-typography.css | 130 | 41 | 42 | 0 | 0 |
| 04 | Acciones y botones | p4-actions.css | 78 | 7 | 16 | 0 | 0 |
| 05 | Formularios e inputs | p5-forms.css | 102 | 20 | 44 | 0 | 0 |
| 06 | Feedback y estados | p6-feedback.css | 153 | 19 | 52 | 0 | 0 |
| 07 | Overlays y diálogo | p7-overlays.css | 118 | 12 | 34 | 0 | 0 |
| 08 | Datos, tablas y listas | p8-data.css | 145 | 16 | 40 | 0 | 0 |
| 09 | Media e iconografía | p9-media.css | 119 | 18 | 42 | 0 | 0 |
| 10 | Comercio y producto | p10-commerce.css | 156 | 22 | 48 | 0 | 0 |
| 11 | Social y marketing | p11-social.css | 107 | 15 | 39 | 0 | 0 |
| 12 | Accesibilidad y sistema | p12-system.css | 80 | 25 | 29 | 0 | 0 |
| 13 | Gráficos y visualización | p13-charts.css | 216 | 22 | 38 | 0 | 0 |
| 14 | IA y agentes | p14-ai.css | 180 | 28 | 32 | 0 | 0 |
| 15 | Apps y escritorio | p15-apps.css | 74 | 30 | 37 | 0 | 0 |
| 16 | Cristal (capa de estilo) | p16-cristal.css | 8 | 2 | 5 | 0 | 0 |
| 17 | Patrones compuestos | p17-patrones.css | 224 | 46 | 47 | 0 | 0 |
| 18 | Escenario (charlas en beats) | p18-escenario.css | 31 | 9 | 16 | 0 | 0 |

## 3. Objetos fantasma

Ninguno: todo lo que usan las demos existe en algún pack. ✅

## 4. Duplicados entre packs

Ninguno: cada objeto tiene un único dueño. ✅

## 5. Cumplimiento del manifiesto

- Colores a mano fuera de tokens.css: **0**
- `backdrop-filter`: **0**
- Gradientes: **0**
- `!important`: **1**
  - p12-system.css: 1
- Tokens inexistentes: **0**

## 6. Objetos declarados sin demo (por categoría)

Ninguno. ✅

## 7. Familias sin variantes (margen de ampliación)

`nz--leading-normal`, `nz--leading-snug`, `nz--leading-tight`, `nz--tracking-caps`, `nz--tracking-tight`, `nz-actbar`, `nz-activity`, `nz-agenda`, `nz-agenda-disponibilidad`, `nz-align-justify`, `nz-align-left`, `nz-align-right`, `nz-appempty`, `nz-appnav`, `nz-appstatus`, `nz-arbol`, `nz-aside`, `nz-asistente-pasos`, `nz-atajo-teclado`, `nz-attach`, `nz-aviso-accion`, `nz-aviso-sistema`, `nz-balance`, `nz-bandeja-avisos`, `nz-barra-filtros`, `nz-bloque-carga`, `nz-bloque-precios`, `nz-bloque-testimonio`, `nz-buscador-facetas`, `nz-cabecera-informe`, `nz-cabecera-pagina`, `nz-caja-comentarios`, `nz-caps`, `nz-center`, `nz-center-x`, `nz-center-xy`, `nz-center-y`, `nz-centro-notificaciones`, `nz-chart-radar`, `nz-chart-range`, `nz-chart-tablebar`, `nz-chat-empty`, `nz-checklist-entrega`, `nz-cite`, `nz-codepad`, `nz-col`, `nz-collapsible`, `nz-columns-2`, `nz-columns-3`, `nz-comparador-planes`, `nz-comparativa-productos`, `nz-cristal-barra`, `nz-dateline`, `nz-desglose-precio`, `nz-docs`, `nz-editor-campos`, `nz-esc-dato`, `nz-estado-vacio`, `nz-eyebrow`, `nz-facturacion-estados`, `nz-ficha-entidad`, `nz-ficha-producto`, `nz-figura`, `nz-filezona`, `nz-filtro-rango`, `nz-focus-accent`, `nz-focus-ring`, `nz-formulario-seccion`, `nz-galeria-filtros`, `nz-hide-escritorio`, `nz-hide-movil`, `nz-high-contrast-note`, `nz-indent`, `nz-initial`, `nz-input-icon`, `nz-inspector`, `nz-kanban`, `nz-launcher`, `nz-linea-pasos`, `nz-lista-tareas`, `nz-maintenance-banner`, `nz-menu-cuenta`, `nz-metrica-tendencia`, `nz-min-target`, `nz-month`, `nz-nav-landmark`, `nz-nota`, `nz-offline-bar`, `nz-overflow-x`, `nz-overflow-y`, `nz-panel-actividad`, `nz-panel-filtros`, `nz-password`, `nz-pathbar`, `nz-pay`, `nz-perfil-pestanas`, `nz-pie-acciones`, `nz-preferencias`, `nz-prefs`, `nz-preguntas-frecuentes`, `nz-pretty`, `nz-print-hide`, `nz-prompt`, `nz-propsheet`, `nz-ptemplate`, `nz-qr`, `nz-reason`, `nz-reduced-motion-ok`, `nz-rejilla-estadisticas`, `nz-resmon`, `nz-resumen-pedido`, `nz-ribbon`, `nz-root`, `nz-route`, `nz-rtl`, `nz-safe`, `nz-safe-x`, `nz-selector-vista`, `nz-show-escritorio`, `nz-show-movil`, `nz-skip-links-group`, `nz-social-proof`, `nz-span-1`, `nz-span-10`, `nz-span-11`, `nz-span-12`, `nz-span-2`, `nz-span-3`, `nz-span-4`, `nz-span-5`, `nz-span-6`, `nz-span-7`, `nz-span-8`, `nz-span-9`, `nz-splitview`, `nz-spotlight`, `nz-sr-only-focusable`, `nz-stat-badge`, `nz-sticky-bottom`, `nz-sticky-top`, `nz-sysdialog`, `nz-sysinfo`, `nz-sysnotif`, `nz-tabfocus-visible`, `nz-tabla-lote`, `nz-tabla-resumen`, `nz-tap-44`, `nz-tarjeta-curso`, `nz-tarjeta-equipo`, `nz-tarjeta-servicio`, `nz-tarjeta-suscripcion`, `nz-taskwin`, `nz-term`, `nz-tokens`, `nz-tray`, `nz-tree`, `nz-userbox`, `nz-version-badge`, `nz-vh`, `nz-visually-hidden`, `nz-widget`, `nz-winfoot`, `nz-wishlist`
