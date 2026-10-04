# Composición — cómo se monta una página con Aurora 8

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
| 3 | **Un protagonista por sección**: la marca (azul/tu color) **o** el acento, nunca los dos de igual a igual | lint: `dos-protagonistas` |
| 4 | **Ningún texto de interfaz por debajo de 13px** (`--nz-text-xs`) | lint: `minimo-tipografico` |
| 5 | **Un solo `<h1>`** y jerarquía sin saltos (h1 → h2 → h3) | lint: `jerarquia` |
| 6 | **Máximo 4 tamaños tipográficos** por página (`--nz-text-*`, nunca px suelto) | lint: `escala-tipografica` |
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
| **Dashboard** | `nz-appshell` + `nz-navbar` + `nz-dash-grid` de KPIs arriba + tablas/gráficos en rejilla | **completo (72rem+)** |
| **Admin / gestión** | `nz-appshell` + barra de acciones + tabla ancha con estados + panel lateral de detalle | **completo** |
| **Ajustes** | una columna de navegación + área de formularios en `nz-formgrid`, secciones numeradas | medio (48-60rem) |
| **Lista → detalle** | `nz-split`: lista a la izquierda, detalle a la derecha; en móvil se apilan | completo |
| **Landing** | hero + 3-5 características + prueba social + CTA final + pie | completo |
| **Informe / documento** | una columna de prosa (`nz-main--narrow`), tablas anchas dentro de `nz-table-wrap`, print cuidado | estrecho (correcto aquí) |
| **Formulario denso** | `nz-formgrid` a 2 columnas desde 640px, ayudas bajo cada campo, acciones fijas abajo | medio |

> **El error más común** (y el de la captura que originó este plan): montar un **panel de
> administración en columna estrecha**. Un admin no es un informe: usa el ancho completo.

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

## 10. Móvil

No lo reinventes: las tablas apilan, la navbar y las pestañas envuelven y nada desborda
(ver `LLM.md` §4b). Añadido: nada clicable por debajo de **`--nz-tactil`** (44px).

---

## 11. Checklist de entrega (12 puntos)

1. ☐ `auditar-uso.py` → **0 fallos**.
2. ☐ 0 emojis (salvo el ❤️ de la atribución).
3. ☐ ≤ 5 momentos de color; un protagonista por sección.
4. ☐ Un `<h1>`, jerarquía sin saltos, ≤ 4 tamaños.
5. ☐ Ningún texto de UI < 13px.
6. ☐ El ancho corresponde al tipo de página (app = completo).
7. ☐ Ritmo vertical con tokens.
8. ☐ Una densidad.
9. ☐ Iconos SVG, no emojis.
10. ☐ Etiquetas de formulario visibles.
11. ☐ Los tres estados (vacío / carga / error) en las vistas de datos.
12. ☐ `scrollWidth == clientWidth` a 320/360/390 y atribución exacta.

---

## 12. Antes / después (el caso real que originó el plan)

Un panel de admin generado con Aurora 7, frente al mismo panel compuesto con este contrato
(receta `recetas/admin.html`):

| | Antes | Después |
|---|---|---|
| Emojis | 26 en la página | 0 (iconos SVG) |
| Colores saturados | azul + naranja + verde + rojo a la vez | marca + 1 acento + estado semántico |
| Ancho | columna de ~700px con márgenes gigantes | ancho completo (72rem+) |
| Tamaños | 12-13px por todas partes | 16 base / 14 UI / 12 micro |
| Rol ADMIN | insignia roja a todo el ancho | insignia neutra + icono |

---

Hecho con ❤️ por David Antizar
