# Composición — cómo se monta una página con Aurora

> El sistema te da las piezas; **este documento es el contrato de cómo se montan**.
> Un HTML que usa las clases correctas pero incumple esto **no está terminado**, aunque
> el lint de clases pase. Es lo que faltaba: Aurora documentaba *objetos*, no *composición*.

Verificación: `python scripts/auditar-uso.py tu-pagina.html` comprueba estas reglas.

---

## 1. Las 12 leyes duras

| # | Ley | Cómo se comprueba |
|---|---|---|
| 1 | **0 emojis como icono de UI.** Único permitido: el ❤️ de la atribución. | lint: `emoji-en-ui` |
| 2 | **≤ 5 momentos de color saturado por página** | lint: `presupuesto-color` |
| 3 | **Un protagonista por sección**: la marca (azul/tu color) **o** el acento, nunca los dos de igual a igual. **Y el acento tiene que aparecer**: cada página lleva al menos un momento de acento, y la marca no acapara más de dos tercios | lint: `dos-protagonistas` · `acento-ausente` · `acento-testimonial` |
| 4 | **Ningún texto de interfaz por debajo de 13px** (`--nz-text-xs`); los 12px (`--nz-text-2xs`) son **solo para datos** (ejes, contadores, notas al pie) | lint: `minimo-tipografico` |
| 5 | **Un solo `<h1>`** y jerarquía sin saltos (h1 → h2 → h3) | lint: `jerarquia` |
| 6 | **Máximo 4 tamaños tipográficos** por página (`--nz-text-*`, nunca px suelto) y **pesos por token** (`--nz-peso-*`): 400 cuerpo · 500 apoyo · 600 interfaz · 700 titulares y cifras. El **800 no existe** y nada por debajo de 16px lleva 700 | lint: `escala-tipografica` · `peso-a-mano` |
| 7 | **Ancho por tipo de página** (ver §5). Una app no vive en columna estrecha | lint: `ancho-composicion` |
| 8 | **Ritmo vertical**: la separación entre secciones sale de `--nz-rh-seccion`, no del aire | lint: `ritmo-vertical` |
| 9 | **Una densidad por página** (compact / normal / spacious) | revisión |
| 10 | **Iconos = `.nz-icon` (SVG en línea con `currentColor`)**, nunca emoji ni fuente de iconos | lint: `emoji-en-ui` |
| 11 | **Cero gradientes, cero glass, cero `!important`** (manifiesto) | lint: manifiesto |
| 12 | **Todo color es un token** `var(--nz-*)`; cero hex a mano | lint: `color-a-mano` |

> Por qué la ley 1 y la 10: los emojis no son iconos. Cambian de forma en cada sistema
> operativo, no heredan el color del texto, no se alinean ópticamente y restan seriedad.
> En el sistema hay **0 emojis en 576 demos**; los ponía el generador. Se acabó.

---

## 2. Jerarquía tipográfica

- **Un `<h1>` por página.** El resto, `<h2>` por sección y `<h3>` dentro.
- Usa la escala del sistema: `--nz-text-2xl/3xl` para el título, `--nz-text-lg` para
  subtítulo, `--nz-text-base` (16) para el cuerpo, `--nz-text-sm/xs` (14/13) para la
  interfaz, `--nz-text-2xs` (12) **solo** para contadores y micro-etiquetas.
- **Máximo 4 tamaños por página.** Si necesitas un quinto, es que la jerarquía no está clara.
- **Pesos por token**, nunca a mano: `--nz-peso-normal` (400) cuerpo y datos ·
  `--nz-peso-medio` (500) apoyo y filas activas · `--nz-peso-fuerte` (600) rótulos de
  interfaz, insignias y botones · `--nz-peso-titulo` (700) **solo** titulares y cifras
  grandes. El **800 está retirado** y **nada por debajo de 16px lleva 700**: cuando todo
  es negrita, nada destaca (medido: el 26% de los elementos de una herramienta salía en
  negrita). Utilidades: `.nz-text--peso-medio`, `.nz-text--peso-fuerte`.
- **13px es el mínimo de la interfaz** (`--nz-text-xs`): etiquetas, insignias, estados.
  Los **12px** (`--nz-text-2xs`) son para **datos**: ejes, contadores, notas al pie,
  atajos de teclado. Una etiqueta nunca baja a 12px.
- **La fuente la sirve el sistema**: Inter variable viaja en `tokens.css`
  (`fuentes/*.woff2`). No enlaces Google Fonts ni cambies `--nz-font` sin motivo: así la
  letra es la misma en Windows, Android, Linux y en una captura headless.
- Un antetítulo (`.nz-eyebrow`) cuenta como parte del título, no como un tamaño más.

```html
<p class="nz-eyebrow">Administración</p>
<h1 class="nz-h1">Usuarios del sistema</h1>
<p class="nz-lead">Alta, rol y permisos de cada cuenta.</p>
```

---

## 3. Color: el presupuesto manda

**Regla del presupuesto:** cuenta los elementos que llevan color saturado (botón primario
lleno, insignia de tono, KPI destacado, serie de gráfico). **Máximo 5 por página.**

| SÍ lleva color | NO lleva color |
|---|---|
| CTA principal y, como mucho, uno secundario | Texto de cuerpo → `--nz-text` |
| Enlaces y elementos activos | Iconos decorativos → `--nz-text-mute` |
| 1-2 KPIs destacados | Bordes y separadores → `--nz-border*` |
| Insignias de estado **crítico** | Fondos de sección → `--nz-surface` / `--nz-bg-soft` |
| 1 serie de un gráfico | Todo lo demás |

**Un protagonista por sección:** la marca y el acento **no compiten**. Si la sección va de
la marca, el acento solo aparece en un detalle. Nunca azul y naranja llenos a la vez.

**Estados semánticos** (`success`/`warning`/`danger`) **no son decoración**: se usan para
decir un estado, no para alegrar la interfaz.

**El acento nunca lleva texto blanco**: es claro por diseño (AA falla). Texto en tinta
sobre acento (`--nz-text`), o acento solo en bordes/fondos suaves.

**El acento tiene un papel, no un hueco** (v8.4). La marca hace la estructura; el
acento marca **el dato que importa y la acción secundaria**:

| El acento SÍ aparece en | El acento NO se usa para |
|---|---|
| El delta de un KPI, la 2ª serie de un gráfico, la cifra que hay que mirar | Todo lo que ya hace la marca (enlaces, foco, activo) |
| Botón/acción secundaria (`.nz-btn--accent`), filete de titular (`.nz-lead--accent`) | Reemplazar a la marca por gusto |
| Resaltado de un dato (`.nz-highlight--accent`, `.nz-text--accent-soft`) | Estados semánticos (esos son success/warning/danger) |
| Un momento por sección, como máximo | Cinco cosas naranjas «para que se vea» |

Y la regla medible: **cada página lleva al menos un momento de acento, y la marca no
acapara más de dos tercios de los momentos de color** (lint: `acento-ausente`,
`acento-testimonial`). En v8.3 el sistema estaba 356 usos de marca por 110 de acento:
la página salía azul porque el CSS la hacía azul.

---

## 4. Densidad y ritmo

- **Una densidad por página**: `compact` (tablas y paneles densos), `normal` (por defecto),
  `spacious` (landing y lectura). No se mezclan.
- **Ritmo vertical**: `--nz-rh-bloque` (24) entre bloques de una misma sección,
  `--nz-rh-seccion` (40 en móvil → 64 en escritorio) entre secciones.
- El espacio interior de un bloque sale de `--nz-space-*`. Cero valores inventados.

---

## 5. Forma de cada tipo de página

Cada tipo tiene **una forma correcta**. Copia la receta de `recetas/`.

| Tipo | Estructura | Ancho |
|---|---|---|
| **Login / acceso** | centrado vertical, tarjeta única (`--nz-container-narrow`), un CTA, alerta de error encima del formulario | estrecho (correcto aquí) |
| **Dashboard** | `nz-appshell` + `nz-navbar` + `nz-dash-grid` de KPIs arriba + tablas/gráficos en rejilla | **completo (72 → 84 → 96rem)** |
| **Admin / gestión** | `nz-appshell` + barra de acciones + tabla ancha con estados + panel lateral de detalle | **completo** |
| **Ajustes** | una columna de navegación + área de formularios en `nz-formgrid`, secciones numeradas | medio (48-60rem) |
| **Lista → detalle** | `nz-split`: lista a la izquierda, detalle a la derecha; en móvil se apilan | completo |
| **Herramienta** (panel, tablero, mapa, editor) | contenedor propio con `.nz-container--app`: **sin tope de ancho** | **pantalla completa** |
| **Landing** | hero + 3-5 características + prueba social + CTA final + pie | completo |
| **Informe / documento** | una columna de prosa (`nz-main--narrow`), tablas anchas dentro de `nz-table-wrap`, print cuidado | estrecho (correcto aquí) |
| **Formulario denso** | `nz-formgrid` a 2 columnas desde 640px, ayudas bajo cada campo, acciones fijas abajo | medio |

> **El error más común** (y el de la captura que originó este plan): montar un **panel de
> administración en columna estrecha**. Un admin no es un informe: usa el ancho completo.

**El lienzo crece solo** (v8.4). `.nz-container` mide 72rem en móvil, 84rem desde 1200px
y 96rem desde 1440px, sin tocar nada. Antes de eso el sistema se plantaba en 960px: en un
monitor de 1920 sobraba el **40% de la pantalla** (768px medidos en producto vivo). Y lo
que **no** crece es la letra: los titulares van topados (34px / 50px) porque un titular de
56px en una pantalla de 27" no es jerarquía, es desproporción.

---

## 6. Tablas y datos

- Tabla de **datos tabulares** que debe caber entera → `.nz-table-wrap--apilable` >
  `.nz-table--apilable` con `data-etiqueta` en cada `td` (las **dos** clases van juntas).
- Tabla **ancha de verdad** (Gantt, calendario) → `.nz-table-wrap` (scroll propio). Nunca
  una tabla ancha suelta: estira la página.
- Números a la derecha (`.nz-table__num`), texto a la izquierda.
- Un estado por fila, no un color distinto por fila.

---

## 7. Formularios

- **Toda etiqueta es visible** (`.nz-field__label`). El placeholder **no** es una etiqueta.
- Ayuda bajo el campo (`.nz-field__help`); error con `.nz-hint-error` y estado `.is-error`.
- Campos agrupados con `.nz-formgrid` (1 columna en móvil, 2 desde 640px).
- Acción principal a la derecha en escritorio, ancho completo en móvil.

---

## 8. Estados: vacío, carga y error

Toda vista de datos tiene sus **tres estados**, no solo el feliz:

- **Vacío** (`.nz-empty`): explica **qué hacer** para llenarlo, no solo "no hay datos".
- **Carga** (`.nz-spinner` / esqueletos): mantén la forma del contenido.
- **Error** (`.nz-alert--danger`): qué pasó y cómo se arregla.

---

## 9. Iconos

- Clase `.nz-icon`, **SVG en línea** con `fill`/`stroke` en `currentColor`, trazo 1.75px,
  rejilla 24px, tamaños `--sm/--lg`.
- Hereda el color del texto: se apaga y se enciende con la interfaz. Un emoji, no.
- Set recomendado para el resto: **Lucide** (MIT), copiado como SVG en línea.

```html
<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="…"/></svg>
```

---

## 10. Móvil y escritorio

**Móvil**: no lo reinventes: las tablas apilan, la navbar y las pestañas envuelven y nada
desborda (ver `LLM.md` §4b). Añadido: nada clicable por debajo de **`--nz-tactil`** (44px).

**Escritorio** (v8.4): el sistema **crece**, no se queda en la columna del móvil. El lienzo
sube a 84rem (≥1200px) y a 96rem (≥1440px), los márgenes laterales suben con él
(`--nz-gutter`: 16 → 24 → 32px) y un panel o herramienta usa `.nz-container--app` para
llenar la pantalla. **La prueba objetiva**: a 1920px, el contenido debe ocupar más del 90%
del ancho; en v8.3 ocupaba el 60%.

---

## 11. Checklist de entrega (12 puntos)

1. ☐ `auditar-uso.py` → **0 fallos**.
2. ☐ 0 emojis (salvo el ❤️ de la atribución).
3. ☐ ≤ 5 momentos de color; un protagonista por sección; **el acento aparece** y la marca no pasa de 2/3.
4. ☐ Un `<h1>`, jerarquía sin saltos, ≤ 4 tamaños, **pesos por token** (nada de 700/800 a mano).
5. ☐ Ningún texto de UI < 13px (los 12px son datos, no etiquetas).
6. ☐ El ancho corresponde al tipo de página (app/herramienta = completo, `.nz-container--app`).
7. ☐ Ritmo vertical con tokens.
8. ☐ Una densidad.
9. ☐ Iconos SVG, no emojis.
10. ☐ Etiquetas de formulario visibles.
11. ☐ Los tres estados (vacío / carga / error) en las vistas de datos.
12. ☐ `scrollWidth == clientWidth` a 320/360/390 y atribución exacta.
13. ☐ **A 1920px el contenido ocupa más del 90% del ancho** (medido, no admirado).
14. ☐ La fuente es la del sistema (Inter servida por `tokens.css`), no la del sistema operativo.

---

## 12. Antes / después (el caso real que originó el plan)

Un panel de admin generado con Aurora, frente al mismo panel compuesto con este contrato
(receta `recetas/admin.html`):

| | Antes | Después |
|---|---|---|
| Emojis | 26 en la página | 0 (iconos SVG) |
| Colores saturados | azul + naranja + verde + rojo a la vez | marca + 1 acento + estado semántico |
| Ancho | columna de ~700px con márgenes gigantes | ancho completo (72rem+) |
| Tamaños | 12-13px por todas partes | 16 base / 14 UI / 12 micro |
| Rol ADMIN | insignia roja a todo el ancho | insignia neutra + icono |

## 13. Antes / después de la v8.4 (lo que cambió y por qué)

Medido en producto vivo (madrid-circula, 1920×1080) antes de la v8.4:

| | v8.3 | v8.4 | Cómo se comprobó |
|---|---|---|---|
| Ancho usado a 1920px | 1152px → **40% de pantalla vacía** | 1536px → 20% de margen (y 0% con `--app`) | `getBoundingClientRect()` del contenedor |
| Media queries por encima de 960px | **1** en 20 packs | escalón 1200 y 1440 en tokens | `grep min-width` |
| Fuente real | la del sistema operativo: **Inter no se cargaba nunca** | Inter variable servida por el repo | ancho de «Inter» vs familia inventada: idénticos en v8.3 |
| Texto de interfaz a 12px | 36 elementos (contra la ley 4 del propio contrato) | 0 rótulos: los 12px quedan para datos | recuento de `getComputedStyle().fontSize` |
| Negritas (≥700) | 167/887 (19%) en la portada · 140/548 (26%) en el panel | objetivo < 8% | recuento de `fontWeight` |
| Titulares | h1 38px · display hasta 56px | h1 34px · display 50px (tope a propósito) | token `--nz-text-3xl/4xl` |
| Uso del acento | 356 marca / 110 acento (3,2:1) | rol definido + lint `acento-ausente` | recuento de `var(--nz-accent*)` |

---

Hecho con ❤️ por David Antizar
