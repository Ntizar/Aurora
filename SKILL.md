---
name: aurora-design-system
description: "Usa al construir o tocar cualquier web con Aurora (Ntizar/Aurora). El repo manda: resuelve la versión vigente y pide LLM.md + components.json antes de escribir CSS."
version: "10.5.0"
tags: [css, design-system, aurora, ntizar, agent-ready, movil, escritorio, tipografia]
---

# Aurora — doctrina única (el repo es la orden máxima)

Design system CSS puro, sin build, sin dependencias, namespaced bajo `.nz-`.
**v10.5.0 · 2195 objetos · 411 familias · 659 demos · 18 categorías · 189 tokens · 59 gemelas OKLch · 38 componentes generativos · 338 iconos numerados.**
*(Cabecera de testigo, no de autoridad: resuélvela con el PASO 0.)*

> ⚠️ `Ntizar/Aurora` **manda sobre esta skill**. Esta skill es un puntero; el repo
> es la fuente de verdad, porque es ahí donde se añade todo el CSS bueno. Si lo que
> dice esta página y lo que dice el repo no coinciden, **gana el repo** — sin dudar
> y sin preguntar. Versión nueva del repo ⇒ se reescribe el primer bloque, nada más.
> La v5/v6 (liquid glass, mesh, orbs, skins OKLCH, escenas Three.js) está **JUBILADA**:
> `nz-glass-*`, `nz-aurora-mesh`, `nz-orb`, `nz-card--glass*`, `data-nz-skin`,
> `three-scenes.js` **no existen en v7**. Solo para mantener repos legacy.

## 0. PASO 0 obligatorio: pregunta al repo antes de escribir una línea

**Nunca uses una versión «de memoria».** La versión cambia; lo que no cambia es el
procedimiento. Resuélvela en cada tarea:

```bash
# a) con el repo clonado (lo normal en esta máquina) — la vía rápida
#    (ajusta la carpeta al nombre de tu clon: Aurora-8, Aurora-7, Aurora…)
git -C C:/Users/d_ant/Projects/Aurora-8 fetch --tags -q
V=$(git -C C:/Users/d_ant/Projects/Aurora-8 describe --tags --abbrev=0)   # p.ej. v10.2.0

# b) sin repo — pregunta a GitHub
curl -s https://api.github.com/repos/Ntizar/Aurora/tags | grep -m1 '"name"'
```

Y lee los **documentos generados** (el repo los produce solo, no los escribas tú):

```bash
# LEER la verdad viva: master / latest (no hay caché que te estorbe, no se sirve a nadie)
curl -s https://cdn.jsdelivr.net/gh/Ntizar/Aurora@master/LLM.md           # ~12 KB
curl -s https://cdn.jsdelivr.net/gh/Ntizar/Aurora@master/components.json  # API completa

# PUBLICAR: siempre el tag resuelto en $V (jsDelivr cachea @master por edge)
#   https://cdn.jsdelivr.net/gh/Ntizar/Aurora@$V/tokens.css
```

Con el repo clonado, tira de disco (más rápido, sin red):
`C:/Users/d_ant/Projects/Aurora-8/{LLM.md,components.json,COMPOSICION.md,bloques/recetas/,SKILL.md}`.

**La regla, en una línea:** *para leer, la verdad viva; para publicar, el tag resuelto.*
`@master` sirve para consultar documentos; el `<link>` que entregas va siempre pineado
al último tag. Zero números hardcodeados: `$V` se resuelve, no se recuerda.

## 1. Pide la solución, no la escribas (~60k tokens menos)

El repo **ya genera la solución** para agentes. Leerla cuesta ~10 KB; leer los 15 packs
cuesta ~250 KB. Nunca pegues CSS de packs en el prompt.

| Necesitas | De dónde (versión resuelta en PASO 0) |
|---|---|
| Qué packs enlazar y qué clases usar | `@master/LLM.md` (o `@$V/LLM.md` si quieres la foto exacta de una release) |
| API exacta: familias, partes, modificadores, tokens, alias EN→ES | `@master/components.json` |
| Página completa que ya funciona | `@master/bloques/ejemplos/` (`landing.html`, `login.html`, `dashboard.html`, `chat-ia.html`, `forms.html`) |
| Esqueleto mínimo por tipo de página | `@master/bloques/combos/<arquetipo>.html` (los 8 de `combosEsqueleto` en `components.json`) |
| Demo viva de un objeto | `https://ntizar.github.io/Aurora/paginas/NN-*.html` |
| Markup exacto de un objeto | `components.json` → `objetos[<familia>].markup.markup` (el bloque real, extraído de su demo) |
| Reglas duras y estado del repo | `@master/AGENTS.md` · `@master/SKILL.md` |

**Tres familias de `bloques/`, no una**: `recetas/` son las páginas canónicas por tipo
(admin, dashboard, ajustes, acceso…), `ejemplos/` las completas listas para copiar
(landing, login, dashboard, chat-ia, forms) y `combos/` los esqueletos por arquetipo.
Para el markup de UN objeto concreto, `objetos[...].markup.markup` es la vía corta.

**Corolario:** si algo no está en `components.json`, no existe. No lo inventes: o usas
el objeto que sí existe, o **se añade al repo** (§9), que es donde vive todo el CSS
bueno y de donde lo heredará el siguiente proyecto. Un patrón resuelto dos veces en dos
proyectos es un fallo del sistema, no del proyecto.

### 1b. Consumir el censo desde FUERA del repo (página en otro lenguaje o proyecto)

Cuando el consumidor no es Python (un `src/censo.json` en Node, un port a otro lenguaje),
aplanar el censo a `clase → pack` es el primer paso de cualquier herramienta propia. Dos
trampas que cuestan una ronda entera:

- **`objetos[f].pack` es el NOMBRE del fichero (`p1-layout.css`), no la ruta.** El `<link>`
  real y el auditor usan `packs/p1-layout.css`. Guarda ya la ruta (`'packs/' + pack`) o
  reportará «falta por enlazar el pack» en TODAS las páginas correctas.
- **`objetos[f].clases` trae base + modificadores + partes.** Recórrelas todas: si solo
  indexas el nombre de la familia, cualquier modificador suelto (`nz-btn--lg`) sale como
  clase inventada.

**Prueba diferencial obligatoria:** pasa el MISMO fichero por `scripts/auditar-uso.py` (el
original, que es el juez) y por tu port. Mismo veredicto, o el que está mal es el port. Y una
prueba de fuego con un HTML saboteado a propósito (clase inventada + gradiente +
`backdrop-filter` + `!important` + dos `<h1>` + un emoji): los dos tienen que cantar los seis.

**Iconos en una página autocontenida:** `<use href="iconos/sprite.svg#nz-i-NNN">` depende de
una ruta relativa que resuelva. Cuando la página se sirve suelta (generada, descargada,
embebida), descarga `iconos/NNN-nombre.svg` e **incrusta su contenido en línea** dentro del
`<svg class="nz-icon" viewBox="0 0 24 24">`. Los SVG ya vienen con
`stroke="currentColor"`, así heredan el color del contenedor.

## 2. Contrato de sincronía (esta skill ↔ repo)

El repo manda; la skill se reescribe en el mismo ciclo. La CI lo exige:

1. Sube la versión en el repo (`scripts/generar-llm-docs.py` → `VERSION`, README, AGENTS.md).
2. Actualiza **`SKILL.md` dentro del repo** (viaja con el código).
3. Copia ese `SKILL.md` a esta skill local (una sola fuente, sin divergencias).
4. Tag `vX.Y.Z` **en el último commit verde** y `git push origin vX.Y.Z`.
5. `python scripts/validar-css.py` → `RESULTADO: VÁLIDO`. Si no, no está terminado: la
   puerta compara `components.json`, el generador, el tag de git y **este `SKILL.md`**.
6. **Canales (el lock manda)**: el canal vivo es un RANGO jsDelivr (`@v10`) gobernado por
   `datos/canales.json`; NUNCA un tag flotante de git (el validador toma «último tag» y
   exige la versión exacta). El canal congelado se sube «a propósito» en cada release; si
   no, `canal.py --check` pone la CI en rojo. Procedimiento y horneado estático:
   `references/portada-y-canal.md`.

Consecuencia práctica: **la versión de esta cabecera es lo único que caduca.** Todo lo
demás (objetos, clases, cifras, móvil) se lee del repo en el PASO 0, así que una versión
nueva del sistema no te deja ciego: solo obliga a refrescar la cabecera.

## 3. CDN pineado (nunca @master para servir CSS en producción)

```html
<html lang="es" data-nz-theme="light">   <!-- o "dark" -->
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/tokens.css">   <!-- canal vivo -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/packs/all.css">
</head>
<body class="nz">
```

`@v10` es el **canal vivo** (se mueve con cada 10.x). Para una entrega congelada, el tag exacto
que resolviste en el PASO 0. Nunca `@master`. Los consumidores fijados en `@v9` o en un tag
exacto de la serie 9 no cambian: `@v9` resuelve su major para siempre (el detalle está en
`CONTRATO.md` del repo). `all.css` solo para prototipos; en producción enlaza
los packs que uses (12-40 KB cada uno). Purga: `curl https://purge.jsdelivr.net/gh/Ntizar/Aurora@$V/<fichero>`.

## 4. Móvil: ya viene resuelto — no lo reinventes por proyecto

Esto es lo que se rompía una y otra vez. Ahora lo garantiza el sistema, sin JS.
(Consulta `LLM.md` para el detalle vivo: puede haber más objetos nuevos.)

| Problema clásico | Objeto del sistema |
|---|---|
| Tabla que debe caber entera (p8) | `.nz-table-wrap--apilable` > `.nz-table--apilable` con `data-etiqueta="Columna"` en cada `td`. En móvil cada fila es una tarjeta con el nombre de su columna delante; desde 640 px vuelve a ser tabla. **Las DOS clases van juntas**: el wrap apilable quita su overflow a móvil a propósito (el marco lo llevan las tarjetas); si la `<table>` no lleva `nz-table--apilable`, la tabla nativa desborda la página |
| Tabla ancha de verdad (Gantt, calendario) | `.nz-table-wrap` (scroll propio). **Nunca** una tabla ancha suelta fuera de un wrap: su `min-width: 30rem` estira la página entera |
| Pestañas que se cortan | `.nz-tabs` **envuelve** en varias líneas (todas alcanzables). Una sola línea a propósito: `.nz-tabs--scroll` |
| Acciones de la navbar inalcanzables | `.nz-navbar` y `.nz-navbar__links` **envuelven**: ninguna acción se corta |
| Un hijo de rejilla que desborda | `.nz-dash-grid`, `.nz-split`, `.nz-thirds`, `.nz-bento`, `.nz-grid-12`, `.nz-holy`, `.nz-article` ya traen `min-width: 0` en sus hijos |

```html
<div class="nz-table-wrap nz-table-wrap--apilable">
  <table class="nz-table nz-table--apilable">
    <thead><tr><th>Entrega</th><th>Entregable</th><th class="nz-table__right">Horas</th></tr></thead>
    <tbody>
      <tr><th scope="row">Informe de requisitos</th>
        <td data-etiqueta="Entrega">oct 2026</td>
        <td class="nz-table__num nz-table__right" data-etiqueta="Horas">32 h</td></tr>
    </tbody>
  </table>
</div>
```

Regla de dedo: **ancho intrínseco → scroll**; **datos tabulares → apilable**.

## 4b. Escritorio y tipografía: lo que arregla la v8.4

**Escritorio** (el fallo que originó esta revisión: un producto mobile-first que se plantaba
en 960px y dejaba el 40% de la pantalla vacío en un monitor):

| Necesito | Cómo |
|---|---|
| Una **herramienta** (panel, tablero, tabla, mapa, editor) a pantalla completa | `<main class="nz-container nz-container--app">` — **sin tope de ancho** |
| Prosa o landing que no se estire hasta reventar | `.nz-container` (72 → 84rem ≥1200 → 96rem ≥1440, ya viene solo) |
| Rejilla de panel en escritorio | `.nz-dash-grid` (llega a 6 columnas en el tramo de 1440) |
| Muchas fichas pequeñas (iconos, miniaturas) | `.nz-grid-auto` (+`--compact` 160 px, `--spacious` 320 px): auto-fit con `min(100%, N)`, sin media queries y sin desbordar a 320 px |
| Márgenes laterales correctos | `--nz-gutter` (16 → 24 → 32px, automático) |
| **Chat o herramienta conversacional** con compositor siempre a la vista | `.nz-chat` con **altura definida** (`min-height` solo no basta: crece con el hilo y empuja el compositor fuera de pantalla) + `.nz-prompt` dentro de `.nz-chat__foot`, y en escritorio `.nz-split--3-2` con un panel de fuentes/contexto al lado |

**Texto** (lo que se verifica contra el censo): el cuerpo va en `.nz-prose`, los rótulos y
notas en `.nz-lbl`, la entradilla en `.nz-lead`. La familia `nz-text` existe **solo con
modificador** (`--muted`, `--small`, `--large`, `--peso-*`…): `nz-text` a secas,
`nz-text--2xs` y `nz-text--xs` **no existen** y el auditor los canta como clase inventada.

La **letra no crece** con el monitor: los titulares están topados a propósito (3xl 34px,
4xl 50px). Un h1 de 56px en un 27" no es jerarquía, es desproporción.

**Tipografía** (dos defectos que David detectó como «tamaños raros» y «negritas cuando no toca»):

| Lo que se hacía | Lo que se hace (v8.4) |
|---|---|
| Micro-rótulos de interfaz a **12px peso 800** | 13px (`--nz-text-xs`) peso 600 (`--nz-peso-fuerte`) |
| `font-weight: 700` y `800` a mano por los packs | Tokens `--nz-peso-*`: 400 cuerpo · 500 apoyo · 600 interfaz · 700 **solo** titulares y cifras |
| `--nz-font: "Inter"` declarada pero **nunca cargada** (se veía la fuente del sistema) | Inter variable **self-hosted** en `tokens.css` (`fuentes/*.woff2`): la misma letra en todas las máquinas y en las capturas |
| Titulares hasta 56px, KPI 28px | Cima recortada (34/50) y la escala baja monótona: 12·13·14·16·18·20·24·28·36·50 |
| Texto real por debajo de 13px (36 casos en un panel: contra la ley 4 del propio contrato) | 13px el mínimo de interfaz; **12px solo para datos** (ejes, contadores, notas) |

El naranja: la doctrina es que **la marca hace la estructura y el acento marca el dato que
importa**. Si una página sale toda azul, no es culpa del diseño: es que no se usó el acento.
El lint lo comprueba (`acento-ausente`, `acento-testimonial`).

## 5. Las reglas duras (la CI las valida)

1. Todo lo público vive bajo `.nz-` (nada de clases globales).
2. Todo valor es un token `var(--nz-*)` — ni un `#2563eb` ni un `16px` a mano.
3. **0 gradientes, 0 `backdrop-filter`, 0 `!important`** — salvo las dos excepciones
   oficiales que el sistema SÍ ofrece: la capa de cristal `p16-cristal.css` (`.nz-cristal`,
   `data-nz-estilo="cristal"`: ÚNICA capa con blur y gradiente, uso CONTROLADO — navegación,
   superficie flotante o panel destacado; nunca cristal anidado ni detrás de tablas y
   formularios; trae fallback opaco por tema) y los helpers de ocultación
   (`.nz-visually-hidden`, `.nz-print-hide`, helpers de visibilidad con sufijo `[class]`).
   Si necesitas cristal en un pack nuevo, va por `p16-cristal`, no se reimplementa.
4. BEM: `.nz-thing`, `__parte`, `--modificador`, estado `.is-x` o `[aria-*]`.
5. Responsive first: contenedor primero (container queries), base móvil en 1 columna y crecer con `@media (min-width: 640/960/1200)` hasta el escritorio. Nunca `max-width` como estrategia (los `max-width` de consumidor solo para apagar un patrón móvil, nunca para construirlo).
6. Táctil 44px en todo lo que se pulsa.
7. Una clase, un dueño (un pack). El shell del catálogo (`.cat-*`) jamás declara `.nz-*`.
8. Footer exacto: `Hecho con ❤️ por David Antizar` (emoji U+2764, sin variantes).
9. Todo en castellano (clases incluidas cuando toca: `nz-arbol`, `nz-filezona`, `nz-fieldset__leyenda`).
10. **Tipografía con juicio (v8.4)**: 13px es el mínimo del texto de interfaz; los 12px
    (`--nz-text-2xs`) son **solo para datos** (ejes, contadores, notas al pie). El peso es un
    token (`--nz-peso-normal/medio/fuerte/titulo` → 400/500/600/700): **el 800 no existe** y
    **nada por debajo de 16px lleva 700** (puerta `peso-por-tamano` de `validar-css.py`;
    excepciones: cifras con `tabular-nums` y símbolos). La fuente la sirve el sistema (Inter
    variable en `tokens.css`): no enlaces Google Fonts.
11. **Escritorio de verdad (v8.4)**: el lienzo crece (72rem → 84rem ≥1200 → 96rem ≥1440) y
    una herramienta (panel, tablero, tabla, mapa, editor) usa **`.nz-container--app`** para
    llenar la pantalla. La **letra no crece** con el monitor; crece el lienzo. Prueba
    objetiva: a 1920px una herramienta ocupa ≥95% del ancho (100% con `--app`) y una página de
    contenido no baja del 80% (en v8.3 era el 60%).
12. **El acento tiene papel (v8.4)**: la marca hace la estructura, el acento marca **el dato
    que importa y la acción secundaria** (delta de KPI, 2ª serie, foco, `--accent` de botón,
    `nz-lead--accent`, `nz-highlight--accent`). Cada página lleva al menos un momento de
    acento y la marca no acapara más de dos tercios (lint: `acento-ausente`,
    `acento-testimonial`).

## 6. Flujo del agente para generar HTML con Aurora

1. **PASO 0**: resuelve `$V` y lee `LLM.md` + `components.json` del repo. Si buscas por necesidad («tabla apilable», «dashboard», «acento»), empieza por `base.html` o `datos/base-diseno.json`: es el índice que ya trae markup, tokens y anti-patrón.
2. **Copia una receta de `bloques/recetas/` o un bloque de `bloques/ejemplos/`** y quítale
   lo que no uses. Para un objeto suelto, el markup está en `components.json` →
   `objetos[...].markup.markup`. **Si vas a generar muchas páginas con la misma
   forma, no copies markup a mano:** escribe un renderizador de bloques (una función por
   bloque, objetos y variantes como datos) y deja que el lint lo cubra. Copiar a mano se
   desincroniza del sistema en cuanto cambia un pack.
3. **Escribe el HTML** con los objetos del censo, responsive first, tokens, 44px. Si la
   interfaz la genera un modelo en caliente (chat, panel dinámico), ve a §14: lenguaje +
   `PROMPT.md` + `aurora-openui.js`, no HTML suelto.
4. **Verifica el HTML**: `python scripts/auditar-uso.py tu-pagina.html` → clases inventadas, packs que faltan, gradientes, colores a mano, desktop-first, atribución. 0 fallos o no está terminado.
5. **Mídelo en móvil de verdad**, no de vista: viewport a 320/360/390 y comprobar que `document.scrollingElement.scrollWidth == clientWidth` en todas las pestañas/secciones. Es la prueba objetiva de que nada se sale.
6. Verificación visual en preview (el lint no ve la estética). Texto por código (`grep`), no por visión: `vision_analyze` alucina erratas.

### 6b. Método de diseño antes de escribir HTML (brief → critique → harden → polish)

1. **Brief** (3-5 líneas, explícitas): quién usa la página y en qué situación, la tarea
   principal que debe poder hacer en 30 segundos, y qué se conserva (marca, hechos, comportamiento).
2. **Critique** (sin tocar nada): ¿el dato que importa está en acento?, ¿la página guía la
   tarea? Salida: 3 fortalezas a conservar + prioridades. Solo después se escribe código.
3. **Harden** (el paso que más bugs evita): probar datos extremos y fallos ANTES de entregar —
   texto de 60+ caracteres sin romper (nunca `nowrap` a ciegas), vacío (`.is-empty` con acción),
   error que no pierde lo escrito, doble submit (`.is-loading`), cifras dispares
   (`nz-chart-tablebar`/bullet escalonado), listas largas (paginación, no desborde). Medir, no admirar.
4. **Polish**: el checklist §8, cuando la dirección y los estados de fallo ya están resueltos.

Checklists completos: `references/metodo-diseno.md` (skill local). Método absorbido de
Impeccable (impeccable.style) como metodología, nunca como dependencia: no instalar su
paquete ni generar `DESIGN.md`/`.impeccable/` — duplicarían `LLM.md` + `components.json`.

### 6c. Vía generativa: el modelo escribe el diseño (openui-lang)

El programa usa los 36 componentes de `openui/PROMPT.md` (argumentos POSICIONALES, sin nombrados;
`root = Pagina([...])` en la primera línea). Se compila desde el repo:

`python scripts/programa-a-html.py mi-programa.openui --salida out.html --marca ntizar --tema light --canal congelado --titulo "..." [--firma full|subtle|none] [--inicio ruta.html] [--modo producto]`

`--canal vivo` emite los enlaces al rango `@vX` (webs propias); `--canal congelado`, para entregas
a cliente. `--packs` imprime solo los packs que el programa usa (el compilador resuelve marca,
tema y packs exactos). `--marca` inexistente **falla con diagnóstico** (el preset va enlazado
detrás de `tokens.css`, nunca fallback silencioso). `--firma` declara la política de atribución
(`full`/`subtle`/`none` → `data-nz-firma`; exactamente una aparición o ninguna, repetida = fallo
del lint). `--inicio` + `--modo producto` marcan el homeRoute y las reglas de producto (la marca
enlaza al inicio, ningún `#` placeholder). Desde ahí, flujo normal: `auditar-uso.py` → 0 fallos,
y render medido en navegador — **ojo a la trampa (c) de §13.3 antes de dar nada por roto**.

**Página estática de verdad (sin JS): hornea, no copies a mano.** `programa-a-html.py` deja el
`<main>` vacío y pinta en cliente. Si la página debe hablar a SEO (landing, portada del propio
sistema) o no debe depender de JavaScript, se hornea:

`python scripts/hornear.py prog.openui --salida out.html [--plantilla-base] [--base ../] [--firma ...] [--inicio ...] [--modo producto]`

Compila, sirve el repo por HTTP local (el runtime carga la spec con `fetch`, que en `file://`
falla por CORS), pinta en Chrome/Edge headless con `--virtual-time-budget`, extrae el `<main>`
ya pintado y escribe el estático. **Nunca escribas el HTML a mano a partir del programa**: es
cómo la portada de Aurora llegó a prometer «el programa se muestra abajo» sin nada abajo, y
cuesta el doble de tokens en cada retoque. En la portada del sistema la cadena es
`briefs/portada.openui` → `hornear.py --plantilla-base` → `briefs/portada.tmpl.html` →
`build-catalog.py` (clava `{{OBJETOS}}`, `{{FAMILIAS}}`, `{{PACKS}}`, `{{MARCAS}}` y el
programa entero en un `<pre>` para que la promesa sea verificable). Las páginas de producto de
referencia (`examples/golden/`) se hornean con `scripts/hornear-golden.py` — única definición,
`--check` detecta HTML desfasado de su `.openui`.

Dos detalles del vocabulario que se aprendieron midiendo: `Boton(texto, tono?, tamano?, bloque?,
href?)` pinta `<a>` cuando lleva `href` (sin él, `<button>`; antes todos los CTA de una página
generada eran botones muertos), y ningún enlace con esquema inadmisible pinta: el compilador
rechaza `javascript:`/`vbscript:`/`data:` en el programa y los renderers vuelven a comprobarlo
(`urlAdmitida()`), además del `auditar-enlaces.py` sobre DOM real. `Navegacion(marca, enlaces,
urls?, inicio?)` lleva las URLs en paralelo con sus enlaces y `inicio` es el homeRoute: si va,
la marca se pinta como `<a>` a ese destino; si no, se usa `data-nz-inicio` de la página y, sin
destino admisible, la marca queda sin enlace (nunca un `#` de relleno en modo producto). Y
`Seccion(children, rotulo?, borde?)` pinta el rótulo como `nz-lbl`, no como `h2`: dos `h2` del
mismo tamaño en la misma sección son ruido, no jerarquía.

Para gastar menos prompt: `generar-web.py --prompt breve` (por defecto) omite los tres ejemplos
largos de `PROMPT.md` cuando ya se parte de una plantilla de arquetipo (~1.040 tokens menos por
generación); `--prompt completo` los devuelve. Procedimiento completo de horneado + release:
`references/portada-y-canal.md`.

**Compilar desde fuera del repo (Node, sin Python) y validar el programa antes de pintarlo.**
`auditar-openui.py` audita la coherencia interna del repo, **no** una pagina generada:
para una pagina tuya el juez es `auditar-uso.py` sobre el HTML resultante. El runtime se
usa en Node cargando el IIFE `openui/aurora-openui.js` en un contexto `vm` con un `fetch`
que devuelve `aurora.spec.json` desde disco y un `import` que rechaza (fuerza el parser
local), y llamando `pintar(programa, null)`: sin contenedor no toca DOM y devuelve el HTML
como cadena. **Y valida los argumentos contra `spec.schema.$defs` ANTES de compilar, porque
el runtime no lo hace**: un booleano en la posicion de un enum pinta `.nz-btn--true` (clase
inventada) y una cadena donde se espera una lista **se imprime como contenido visible** en
la pagina. Recetas de carga, validacion, reparacion mecanica, presupuesto de color sobre el
programa y reglas de prompt: `references/openui-desde-fuera.md`.

**Un generador con N plantillas fijas es una jaula.** Si el producto solo elige entre
composiciones predefinidas, N documentos distintos producen N webs que se parecen y el
usuario lo nota («no me gusta que todo sea lo mismo»). Cuando pida variedad, dale al modelo
un lenguaje de composicion (openui-lang) mas un registro de estilo, y **mide que N estilos
dan N estructuras** — conjunto de componentes y secuencia de bloques distintos, no «se ven
distintas» a ojo — y que las N pasan el lint con 0 fallos.

**Variedad NO es recargar.** La misma peticion que pide formatos distintos suele pedir,
literalmente en la misma frase, que el diseno sea «mas simple y agradable». Las dos cosas
van juntas o la entrega falla: la variedad se paga con **estructura** (que componentes, en
que orden, con que densidad), nunca con mas adornos, mas sombras ni mas color. Si al
diversificar suben las superficies, las sombras o los momentos de marca, has entendido mal
la peticion (§13b). Antes de dar por buena una variante, comprueba que su presupuesto de
superficies y color no es peor que el de la receta canonica.

Dos verdades de auditoria medidas, no deducidas: que la portada del sistema vista el sistema se
comprueba con `grep -c 'class="cat-' index.html` (el shell cat-* es legitimo solo en el catálogo;
cientos de usos en la portada = no-dogfooding); y «que cualquiera pueda usarlo» exige un
`LICENSE` en la raíz del repo — sin licencia es legalmente falso. Comprueba ambos antes de
vender la promesa.

## 7. Necesito X → uso Y (verificado contra el censo)

| Necesito | Clases |
|---|---|
| Botón (p4) | `.nz-btn` + `--primary/--accent/--ghost/--soft/--outline/--danger` + `--sm/--lg/--icon` |
| Superficie (p1) | `.nz-article`, `.nz-bento`, `.nz-thirds`, `.nz-hero-bleed` · **`.nz-card` NO existe** |
| Formulario (p5) | `.nz-field` > `__label` + `.nz-input` + `__help`, `.nz-formgrid`, `.nz-fieldset__leyenda` |
| Opciones (p5) | `.nz-checkbox`, `.nz-radio`, `.nz-switch`, `.nz-segmented` |
| Aviso (p6) | `.nz-alert--info/--success/--warning/--danger`, `.nz-callout`, `.nz-badge--*` |
| Tabla ancha (p8) | `.nz-table-wrap` > `.nz-table` (+ `--striped`, `__num`, `__status`) |
| Tabla que debe caber entera (p8) | `.nz-table-wrap--apilable` > `.nz-table--apilable` + `data-etiqueta` |
| KPI (p8) | `.nz-kpi` (`__label/__value/__delta`) |
| Gráfico (p13) | `.nz-chart` + `.nz-chart-bar/-line/-donut/-gauge`, `.nz-heatmap` |
| Magnitudes dispares en una comparativa (p13) | `.nz-chart-tablebar` (barras alineadas por fila, cada una con su cifra) — no barras de una sola escala |
| Presupuesto real vs objetivo (p13) | `.nz-bullet`: escalona la pista ×1,5 y fija la línea de objetivo al 66,7% (barra=real, línea=objeto); tonos reales: brand/accent/success (sin danger) |
| Desglose desde un total (nómina→colchón) (p13) | `.nz-chart-waterfall`: tramos `--down` como altura acumulada % del total, cierre `--up` (verde) o `--total` |
| Métrica con tendencia (p13) | `.nz-chart-stat` + `.nz-sparkline` (7-9 barras, meses completos; excluye el mes en curso parcial) |
| Diálogo (p7) | `.nz-modal` (sin JS), `.nz-drawer`, `.nz-sheet` |
| Layout (p1) | `.nz-appshell`, `.nz-with-sidebar`, `.nz-split`, `.nz-dash-grid`, `.nz-container` |
| Navegación (p2) | `.nz-navbar`, `.nz-tabs` (+ `--scroll`, `--pill`), `.nz-breadcrumb`, `.nz-stepper`, `.nz-pagination` |
| Chat IA (p14) | `.nz-chat`, `.nz-msg`, `.nz-prompt`, `.nz-toolcall`, `.nz-taskplan`, `.nz-approval` |
| Presentar una charla en beats (p18) | `.nz-escenario` (+ `--lienzo`, `--profundo`) con `.nz-esc-titular/editorial/numeral/etiqueta/dato`, `.nz-nodo`, `.nz-enlace`, `.nz-qr` |
| Escritorio (p15) | `.nz-window`, `.nz-appnav`, `.nz-kanban`, `.nz-actbar`, `.nz-statusbar` |
| Herramienta a pantalla completa (p1) | `.nz-container--app` (junto a `.nz-container`) |
| Buscar por necesidad, no por clase | `base.html` (explorador) · `datos/base-diseno.json` (índice machine-readable) |
| Que un objeto responda a su contenedor, no al monitor (v9.2) | `.nz-cq` en el marco + `.nz-dash-grid`/`.nz-split`/`.nz-bento`; `.nz-chart`, `.nz-chat`, `.nz-kanban-wrap` ya son contenedores |
| Kanban en un sidebar estrecho | `.nz-kanban-wrap` > `.nz-kanban`: en <48rem se queda en filas |
| El dato que importa en acento (p3/p8) | `.nz-num--accent`, `.nz-kpi--accent`, `.nz-lbl--accent`, `.nz-lead--accent`, `.nz-text--accent-soft`, `.nz-highlight--accent` |
| Énfasis sin negrita | `.nz-text--peso-medio`, `.nz-text--peso-fuerte` |
| Un icono (p9) | `.nz-icon` + SVG **del repositorio** `iconos/` (`nz-i-042`): `<svg class="nz-icon nz-icon--accent"><use href="iconos/sprite.svg#nz-i-042"/></svg>`. Tono con `--accent/--brand/--success/--warning/--danger/--info`; grosor con `--fino/--grueso`. Nunca un emoji ni un símbolo de texto |

Léxico cerrado de modificadores (igual en los 18 packs): tamaño `--2xs/--xs/--sm/--lg/--xl`,
tono `--brand/--accent/--success/--warning/--danger/--info/--neutral`, énfasis `--solid/--soft/--outline/--ghost`,
disposición `--vertical/--horizontal/--inline/--compact/--spacious/--center/--between/--end`,
forma `--square/--rounded/--pill`, elevación `--flat/--raised`, estados `.is-active/.is-disabled/.is-loading/.is-done/.is-error/.is-empty/.is-selected`.

## 8. Verificación pre-entrega (checklist)

1. PASO 0 hecho: `$V` resuelto del repo, no de memoria.
2. `auditar-uso.py` sobre el HTML → 0 fallos.
3. `<html lang="es" data-nz-theme="light">` + `<body class="nz">` + CDN pineado a `$V`.
4. Footer exacto con atribución.
5. Móvil medido, no admirado: `scrollWidth == clientWidth` a 320/360/390 en todas las pestañas; táctil 44px.
   Procedimiento fiable de emulación con CDP: abre la pestaña en `about:blank`, aplica
   `Emulation.setDeviceMetricsOverride(width, height, deviceScaleFactor, mobile)` ANTES de navegar al HTML, y mide después. Si aplicas el override sobre una página YA cargada, el layout sigue hecho al ancho de viewport anterior y mide desbordes fantasma (p. ej. el contenedor queda a 374px con clientWidth 320): el desborde es del test, no de la página. Para medir otra ventana no sirven `window.open` en `file://`: el origen null bloquea el acceso al documento hijo (cross-origin).
   **Y si `innerWidth` no coincide con el ancho que pediste, el test no ha corrido: no lo interpretes.** Encadenar overrides en una sesión de navegador ya usada deja de aplicarse en silencio —pides 360 y `innerWidth` sigue en 1264— y cualquier medida que saques de ahí es del escritorio disfrazada de móvil. Comprueba `innerWidth + '×' + innerHeight` en cada iteración y, si no cuadra, repite en una **sesión limpia**; no des el móvil por bueno hasta que el ancho declarado y el real coincidan.
5b. **La acción principal se ve sin desplazar, y también en MÓVIL.** En una herramienta (chat, formulario, panel) el control que el usuario necesita —enviar, guardar, filtrar— debe estar dentro del viewport a 1908×913. Ni el auditor ni el test de móvil lo detectan: mide `getBoundingClientRect()` del control contra `innerHeight`. Un titular grande + entradilla + aviso antes de la herramienta se come 200px y deja el compositor por debajo del pliegue.
    **El escritorio aprobado no implica el móvil aprobado:** el mismo hero a dos columnas se apila en móvil, el titular se come la pantalla y el botón queda al borde (medido: 695-747px de 760 en 320×760, que en un terminal real de 640 de alto no cabe). Mide a 320/360/390 con el override aplicado **antes** de navegar, y si no cabe, sube la herramienta con `order` en el contenedor flex —**sin cambiar el orden del DOM**, para no romper el lector de pantalla— y aprieta el hero solo en móvil (`@media (max-width: 639px)`, titular un escalón menos y fuera los adornos).
6. Escritorio y print (si es informe) sin regresión. Mirar la página en preview.
7. Si tocaste el sistema: `generar-base-datos.py && auditar-base.py --check && auditar-responsive.py` en verde. La base de datos y los container queries no se degradan en silencio.
8. **Enlaces y navegación**: `python scripts/auditar-enlaces.py` → 0 enlaces rotos, 0 anclajes
   rotos, 0 IDs duplicados, 0 protocolos inseguros, 0 placeholders `#` en modo producto y
   camino a la portada (o al `data-nz-inicio` del producto) en todas las páginas. Nació de un
   fallo caro: al mover `recetas/` a `bloques/recetas/` las rutas se quedaron en `../` (un
   nivel) y **todas las recetas se sirvieron sin CSS** durante una release entera; nadie lo
   vio porque el HTML era válido. Mover una carpeta = reescribir rutas relativas + pasar este
   auditor. Ignora `<pre>`/`<code>` (ahí hay ejemplos escapados, no enlaces) y también los
   comentarios: un `<h1>` citado en un comentario corta la búsqueda y da un falso «sin botón».
9. Si la página la generó openui-lang: compilada con `programa-a-html.py` (u horneada con
   `hornear.py`/`hornear-golden.py`), `auditar-uso.py` en 0 fallos y render medido en navegador
   **tras resolver el runtime** (trampa c de §13.3). Si es producto de referencia:
   `python scripts/probar-producto.py` → 18 comprobaciones (marca computada, política de firma,
   recorrido de navegación, overflow y jerarquía) en verde.

## 9. Ampliar el repo (aquí va todo el CSS bueno)

Cuando un proyecto necesita algo que no existe, **se sube al repo**, no se queda en el
CSS del proyecto:

1. Declara las clases en el pack correspondiente (tokens, sin `!important`, sin gradientes).
2. Añade su demo en `specs/NN.json` (markup en UNA línea, contenido real en castellano, inline solo para geometría con `var(--nz-*)`).
3. Regenera y valida hasta verde: `python scripts/build-catalog.py && python scripts/audit-catalog.py && python scripts/audit-html.py && python scripts/validar-css.py`. Cero «clases declaradas sin demo», cero duplicados entre packs.
4. Sube la versión (`VERSION` + README + AGENTS.md + `SKILL.md`) y tag `vX.Y.Z` en el último commit verde.
5. Actualiza la cabecera de esta skill (una línea) y el tag del proyecto consumidor.

Criterio de admisión: (a) resuelve un problema real y repetido, (b) es responsive first sin JS,
(c) encaja en el léxico cerrado, (d) lleva demo viva, (e) no duplica nada que ya exista.

## 10. Anti-patrones (errores reales acumulados)

- ❌ Clases de la v6: `nz-card--glass-liquid-*`, `nz-gradient-text`, `nz-aurora-mesh`, `nz-orb`, `u-nz-text-brand`, `data-nz-skin`. En v7 no existen. Títulos destacados: `.nz-h1--brand`.
- ❌ Inventar clases (auditadas en el pasado: `nz-btn--glass-liquid-secondary`, `nz-fieldset__legend` — lo real es `__leyenda`). Si no está en `components.json`, no existe.
- ❌ **Malos tamaños de texto.** `nz-text` a secas (sin modificador), `nz-text--2xs` y `nz-text--xs` **no existen** (cuerpo = `nz-prose`, rótulo = `nz-lbl`, entradilla = `nz-lead`; de la familia `nz-text` solo valen los modificadores: `--muted`, `--small`, `--large`, `--peso-*`), y las partes de `.nz-alert` son `__icon`/`__body`/`__title`/`__msg`/`__action`/`__close` — `__text` tampoco. El auditor las caza todas, pero cuesta una iteración cada vez: consúltalas antes de escribir el primer párrafo.
- ❌ **`.nz-switch` sin `__track` + `__thumb`.** El markup correcto es `<label class="nz-switch"><input type="checkbox"><span class="nz-switch__track"><span class="nz-switch__thumb"></span></span><span class="nz-switch__label">…</span></label>`. Sin el track/thumb el `<input>` queda **inerte**: el usuario no puede cambiar de estado y lo reporta como «no me deja», no como bug de UI. Compruébalo con un clic real y leyendo `checked` antes y después.
- ❌ **Usar `.nz-callout` para texto largo o citas.** Es un objeto de **aviso corto** (título + mensaje): metido en un contenedor estrecho parte la prosa palabra por palabra y parece una tabla. Para una cita: atribución en `.nz-lbl` y el texto literal en `.nz-prose`; una sola insignia de estado por respuesta, no una por cita.
- ❌ **Emojis como iconos de estado** (✅ ❔ ⚠): el auditor los marca (`emoji-en-ui`) y cambian de forma según la fuente. Usa el sprite: `nz-i-069` verificado, `nz-i-073` pregunta, `nz-i-072` atención, `nz-i-016` cerrar, `nz-i-074` información.
- ❌ **Creer al auditor cuando dice «pack p9-media sin uso aparente».** Solo ve el HTML estático: si los `.nz-icon` los crea el JS, el pack hace falta igualmente. Comprueba en el navegador (`document.querySelectorAll('svg.nz-icon').length`) antes de quitarlo.
- ❌ **Escribir `body { … }` o cualquier CSS propio en la página, más allá de un contenedor de layout.** No hace falta: `tokens.css` ya pinta `body` (fondo, tinta, Inter) y los packs dan las superficies. Un `<style>` propio solo invita a colores a mano (el lint lo marca) y a competir con la cascada del sistema. Si lo que quieres no existe, va al repo (§9) o se resuelve con un objeto existente.
- ❌ **`span.nz-lbl` suelto como hijo directo de `nz-stack`:** se estira a todo el ancho y parece una barra vacía. Envuélvelo en `nz-cluster` (o úsalo dentro de un cluster junto a otros elementos).
- ❌ **Dejar el `<h1>` con `nz-h1--brand` por defecto.** El titular en tinta + UN momento de marca en la acción principal (botón primario) + UN momento de acento en el dato lee mejor y respeta el presupuesto: con `--brand` en el h1 más dos botones primarios, `acento-testimonial` salta. La receta de `bloques/ejemplos/landing.html` lo hace así.
- ❌ **Poner un `.nz-lead`, `.nz-prose` o `.nz-text--muted` dentro de un `--brand` a sangre.** `.nz-hero-bleed--brand` pinta fondo de marca y tinta invertida en el contenedor, pero las familias de texto traen su propio `color: var(--nz-text-soft)`: gris oscuro sobre azul, ilegible. El sistema **no tiene utilidad de texto invertido**, así que o el hero de marca lleva solo titulares (que heredan la tinta invertida) o va en fondo suave. Con `--brand` y prosa dentro, el contraste se rompe aunque el lint no lo vea.
- ❌ **Un elemento de rejilla/flex dentro de un contenedor que es flex en columna y no estira a sus hijos.** `.nz-cta-banner` es `display:flex; flex-direction:column; align-items:flex-start`: un `.nz-split` hijo NO reparte en columnas y el texto se queda en una columna de un carácter (con el titular partido palabra por palabra). Para repartir dentro de un banner, el cuerpo se monta con `.nz-cluster`/`.nz-split` **con `width:100%`**, o se usa el objeto tal como viene. Síntoma delator: un titular de 4 palabras en 4 líneas. Se ve en captura, no en el lint.
- ❌ **`.nz-timeline` con contenido rico sin envolver los textos en pila.** `__title`, `__desc` y `__time` son `inline`: puestos como hermanos dentro de `__item` se leen en una sola línea corrida («Solicita acceso Contacta para abrir…»). Van dentro de un `.nz-stack nz-stack--2xs` dentro del `__item`. Y si cada paso tiene muy poco texto, el timeline se queda flaco en una columna estrecha: para procesos de negocio (3-4 pasos con una frase) unas `.nz-article` con `.nz-badge` numerado ocupan el ancho mejor que un timeline.
- ❌ **`.nz-list--icon` esperando que pinte un icono.** Pinta una **caja** de fondo marca-soft y el icono que pongas dentro se suma a ella: sale un cuadro vacío que parece un checkbox de formulario. Para una lista de puntos con marca de verificación usa `.nz-list--check` y deja que el sistema ponga el glifo; el `--icon` es para cuando la caja ES el icono.
- ❌ **Dar por hecho que el acordeón se ve desplegable.** `.nz-preguntas-frecuentes__pregunta` no trae indicador: sin chevron el usuario ve cajas de texto estáticas y no sabe que se abren. Añade el icono del sprite (`iconos/011-angulo-abajo.svg`) dentro del `<summary>` y gíralo con `.nz-preguntas-frecuentes__item[open] .nz-preguntas-frecuentes__pregunta .nz-icon { transform: rotate(180deg) }` — es geometría, no color, así que cabe en un `<style>` propio.
- ❌ Usar una versión «de memoria» en vez del PASO 0 (resolver `$V` del repo).
- ❌ Colores a mano o degradados azul→naranja: el azul es primario y el naranja acento, **en elementos separados**. Gradiente solo monocromo si acaso (en v7, ninguno).
- ❌ KPIs gigantes (2.5rem+) y bordes decorativos superiores en cards («look de IA»).
- ❌ Enlazar `@vX.Y.Z` que no sea el último tag, o pegar el CSS de los packs en el prompt.
- ❌ Desborde horizontal: nada puede dejar `scrollWidth > clientWidth` en el documento. Si pasa, es un fallo de entrega, no un detalle.
- ❌ Arreglar el móvil con `max-width` como estrategia, con `overflow-x` a lo bruto en el `body`, o escondiendo columnas con `display:none` (se pierde el dato).
- ❌ `white-space: nowrap` en una tabla que se apila: mata el apilado y fuerza scroll.
- ❌ Pinear un tag que existe **solo en local** y no está pusheado a GitHub: el CDN da 404 y la página sale sin CSS (bug real: `@v7.2.2` local sin pushear → 404 en todos los packs → HTML crudo). Tras resolver `$V`, **comprueba que el tag está publicado**: `git ls-remote --tags origin | grep vX.Y.Z`, y verifica el 200 del CDN: `curl -o /dev/null -w "%{http_code}" https://cdn.jsdelivr.net/gh/Ntizar/Aurora@$V/tokens.css`. Si solo existe en local, o se pushea el tag o se usa el último **publicado**.
- ❌ Verificar el CSS por las **clases en el DOM** en vez de por los **estilos computados**: las clases `nz-*` aparecen en el markup aunque el `<link>` al CDN dé 404 (el HTML se sirve igual, sin CSS). Prueba real: `getComputedStyle` de `.nz-navbar` debe dar `display:flex`, no el default; y `document.styleSheets` debe listar las 7 hojas.
- ❌ Enlazar un tag que NO está pusheado a origin: si el tag solo existe en local, jsDelivr da 404 y la página se ve pelada (pasó con v7.2.2). Tras resolver $V, verificar `git ls-remote --tags origin` o `curl -o /dev/null -w %{http_code}` del tokens.css del tag; si 404, usar el último tag publicado. Verificar visual con computed styles (getComputedStyle), no solo con el lint: el lint no ve el CSS caído.
- ❌ Comparar órdenes de magnitud en `.nz-chart-bar`/`.nz-bullet` de una sola escala (29.262 € junto a 109 €: las barras pequeñas desaparecen y el gráfico miente). Para mezclas dispares, `.nz-chart-tablebar`; para presupuestos, bullet con pista escalonada.
- ❌ **Contenedor con solo `min-height` cuando su hijo usa `height: 100%`**: el porcentaje no resuelve y el hijo colapsa. Bug real: `.nz-chart-bar__col` (y `__bar`) se quedaban en 2px en TODAS las gráficas de barras, y la cascada en 0px — roto también en el catálogo oficial durante meses. Da altura **definida** al contenedor (`height: 8rem`, no `min-height`) o usa `inset: 0` si el hijo es absoluto. El lint no lo ve: hay que medirlo (`getBoundingClientRect().height` en el navegador).
- ❌ **Dejar una familia declarada en dos packs** aunque sea por un modificador suelto: el censo asigna la familia al pack de la primera clase que encuentra, y un agente que siga `components.json` enlaza el pack equivocado → el componente sale **sin estilos**. Bug real: `.nz-sidebar--sticky` vivía en `p1-layout.css` mientras la familia estaba en `p2-navigation.css`, y la barra lateral salía pelada. **Una familia, un pack**; auditarlo cruzando el censo con las declaraciones reales (no solo por clase, por FAMILIA).
- ❌ **Estilar el markup de una demo con un selector de elemento pelado en el shell.**
  `.cat-stage p` (0,1,1) gana a cualquier objeto del sistema (0,1,0): las demos de tipografía
  llevaban desde siempre pintándose a 13px apagados (`nz-display`, `nz-h1`, `nz-esc-titular`) sin
  que el lint lo viera, porque el lint mira clases declaradas, no quién gana la cascada. Se descubre
  **midiendo** el tamaño computado en el navegador. El shell estila lo suyo con `:not([class])`.
- ❌ **Declarar una fuente que no se carga.** `--nz-font: "Inter"` sin `@font-face` ni
  `<link>`: el navegador cae a la fuente del sistema y **nadie se entera**, porque el CSS
  es válido y el lint mira tokens, no si la letra llega. Medido (v8.3): el ancho de «Inter»
  era idéntico al de una familia inventada (612,47px), `document.fonts` traía 0 fuentes web
  y aun así `document.fonts.check('16px Inter')` devolvía `true` (falso positivo) — se
  comprueba **midiendo anchos**, no preguntando. En v8.4 Inter viaja en `tokens.css`.
- ❌ **Negritas a mano por todo el sistema.** 70+ `font-weight: 700/800` sueltos y 167 de
  887 elementos en negrita en una portada (19%; 26% en un panel): cuando todo es negrita
  nada destaca, y el texto de 12px en negrita se lee peor, no mejor. El peso es un token y
  el 800 no existe.
- ❌ **Dejar el escritorio a la deriva.** Responsive first no es «solo móvil»: si no hay ningún
  escalón por encima de 960px, el producto enseña 768px de margen en un monitor de 1920
  (40% de la pantalla, medido). El lienzo crece; la letra no.
- ❌ **Enlazar Google Fonts o cualquier CDN de fuentes** en un producto Aurora: la letra
  ya viene en el sistema, y una dependencia externa rompe las capturas headless y la
  paridad entre máquinas. La portada lo hacía con Inter (duplicaba la fuente que sirve
  `tokens.css`); corregido en 9.2: el `<link>` externo sobra.
- ❌ **Editar a mano algo que genera un script.** `components.json`, `datos/base-diseno.json`,
  `paginas/*.html`, `bloques/combos/*`, `iconos/index.html`, `briefs/portada.tmpl.html`,
  `examples/golden/*.html`: son salidas de build. Parchearlas a mano parece que funciona y la
  siguiente regeneración lo pisa o el `--check` lo canta en el acto («desincronizado: ejecuta
  iconos.py todo»). **Se arregla el generador y se regenera**; si el cambio debe durar, va al
  generador con su comentario de por qué.
- ❌ **Insertar una etiqueta «después del atributo» en vez de después de la etiqueta.** Un
  `<link rel="stylesheet" href="...p1.css"` + `<link ... p2.css">>` deja la primera sin su `>` y el
  sobrante cierra la segunda: el navegador carga 6 hojas y no la 7, el HTML «valida» y el elemento
  sale con el azul por defecto del enlace. Ancla el reemplazo en el `>` de cierre
  (`href="...\.css">`) y deja que el auditor cace cualquier `<link>` sin cerrar.
- ❌ **Suponer que el CDN ya tiene lo que acabas de escribir en el repo.** El tag publicado va por
  detrás: si añades `text-decoration: none` a `.nz-navbar__brand` y la página enlaza `@vX.Y.Z`, la
  marca sale subrayada allí. Puente sin release: suma una clase que **ya** traiga la propiedad en
  el tag publicado (`class="nz-navbar__brand nz-navbar__link"`), o publica versión nueva — nunca
  `style=""` a mano.
- ❌ **Resolver un objeto compuesto solo con `@media`.** Un chart o un kanban dentro de
  un sidebar de 320px se rompe aunque el monitor sea 4K. Los objetos compuestos consultan
  su contenedor; si el objeto no es contenedor, se declara el contexto con `.nz-cq`.
- ❌ **Declarar `container-type` en `.nz-table-wrap`.** El `thead` sticky necesita su
  propio scroll container; el contexto de consulta lo ponen `.nz-dash-grid` y `.nz-split`.
- ❌ **Dejar el patrón resuelto en el proyecto y no subirlo al repo.**
- ❌ **Un `.nz-segmented` de 3+ opciones dentro de un panel estrecho (inspector de 20rem) sin wrap**: la última opción se trunca fuera del panel. `flex-wrap: wrap` en los segmented del panel (página herramienta → `references/paginas-herramienta.md`).
- ❌ **`pre { white-space: pre }` dentro de una rejilla hecha a mano sin `min-width: 0` en el ítem**: el ancho intrínseco del código empuja el track y el documento desborda en móvil — aunque los objetos del sistema ya traigan `min-width: 0`, una rejilla local no lo hereda.

## 11. Excepciones vigentes (cuándo NO usar Aurora)

- **Design systems corporativos**: si un equipo pide un CSS con los colores de SU marca (ej. Kaizen/Ineco #1A4488), se crea un sistema propio alineado con su manual, no Aurora.
- **Presentaciones consulting / informes ejecutivos** (estilo McKinsey/BCG): fondo blanco elegante, sin estética tech. David rechazó Aurora para esos entregables.

## 12. Migrar de v6.1 a v7

No es cambiar dos URLs: es reescribir markup. Medido en caso real: de 107 clases usadas
solo 22 existían en v7. Sin equivalencia 1:1 (`nz-card` → `nz-article`/`nz-bento`/`nz-thirds`;
mesh/orbs/3D desaparecen). El caso completo, con el script de medición de clases supervivientes,
está en la skill `design-system-coherence-audit` (en la instalación local ya no existe
`references/migracion-v6-a-v7.md`: no apuntes a ficheros que no puedas abrir).

## 13. Lecciones que costaron tiempo (verificadas, no teoria)

1. **Corre la cadena ENTERA que corre la CI antes de pushear.** No basta `validar-css.py`: la CI
   pasa además `audit-a11y.py` (inputs sin etiqueta), `audit-tema.py` (supervivencia a modo
   oscuro), `audit-catalog.py`, `audit-html.py` y `auditar-uso.py`. Pushear con la CI en rojo es
   pushear a medias. Cadena completa:
   `python scripts/validar-css.py && python scripts/audit-catalog.py && python scripts/audit-html.py && python scripts/audit-a11y.py && python scripts/audit-tema.py && python scripts/auditar-base.py --check && python scripts/auditar-responsive.py && python scripts/auditar-uso.py --selftest`
2. **El estado inicial de una animación NUNCA es 0.** Arrancar en `scaleY(0)` / `opacity: 0` y
   confiar en que el JS revele deja el dato invisible si el JS falla, si una captura headless
   congela la animación o si la pestaña está en segundo plano. Arranca en `0.55` y pon red de
   seguridad por tiempo: el dato siempre se lee, la animación solo lo adereza.
3. **Verificar en navegador tiene cuatro trampas.** (a) En pestaña oculta `IntersectionObserver` y
   `setTimeout` no disparan: llama a `Page.bringToFront` y espera antes de medir. (b) Al editar
   CSS/JS en `file://` el navegador sirve caché: `Network.setCacheDisabled(true)` o verás el
   fichero viejo y perseguirás un bug fantasma (y creerás que tu arreglo no funciona). (c) Una
   página compilada desde openui-lang **pinta en cliente**: el compilador deja `<main>` vacío y
   embebe el programa y el runtime (`openui/aurora-openui.js`; la ruta `js/aurora-openui.js`
   no existe). La primera pasada recién cargada da Times New Roman y 0 componentes — no está
   rota: `AuroraOpenUI.iniciar` aún está resolviendo la spec. Espera ~3 s y **remide**
   (estilo computado, `querySelector` de `.nz-*`, desborde) antes de concluir nada. (La vía
   `probar-producto.py` y el horneado existen precisamente para no depender de esa espera.)
   (d) Si el CSS viene del CDN, 1-2 s no bastan: medido, a 1,2 s la navbar daba 36 px y peso 400
   (sin hoja) y a 5 s daba 61 px y `display:flex`. Antes de gritar «sin CSS», lista
   `document.styleSheets` y comprueba que **el pack que necesitas está en la lista**; y no te fíes
   de `curl -w %{size_download}` contra jsDelivr (devuelve 0 B con 200): el estado fiable es el
   navegador, no el tamaño.
4. **Un tag de git es inmutable.** El CDN `@vX.Y.Z` seguirá sirviendo el commit viejo aunque
   `master` avance: cualquier funcionalidad nueva necesita versión nueva (`VERSION` en
   `scripts/generar-llm-docs.py`, `components.json`, badge del README, tag) y todas deben decir
   lo mismo — el validador lo comprueba contra el último tag.
5. **Un design system se contradice en silencio.** v8.3 declaraba «13px es el mínimo de
   interfaz» mientras tenía 36 textos por debajo en un producto real y 137 usos de 12px en
   los packs; y la documentación empujaba `data-nz-marca="indigo"` como ejemplo, así que
   todos los productos salían azules y el naranja desaparecía. Se arregla **poniendo la
   regla en el lint** (`minimo-tipografico`, `peso-a-mano`, `acento-ausente`) y **cambiando
   el ejemplo de la doc al preset por defecto**. Lección: el ejemplo de la documentación *es*
   doctrina — lo que muestras es lo que se construye.
6. **«Mide, no admires» también vale para el diseño.** Los tres defectos que originaron la
   v8.4 (40% de pantalla vacía, Inter que nunca se cargaba, 19-26% de negritas) no se ven
   mirando una captura con cariño: se ven con `getBoundingClientRect()`, midiendo el ancho
   de un texto contra una familia inventada y contando `getComputedStyle().fontWeight`.
7. **Una base de datos que se escribe a mano miente.** `components.json` ya tenía 409
   familias con markup real, pero nadie podía consultarlo sin cargar 487 KB. La base de
   datos (`datos/base-diseno.json` + `base.html`) se **deriva** de las fuentes y se audita;
   si se retoca a mano, la siguiente regeneración la pisa y `--check` lo caza. El índice no
   es un documento: es una salida de build.
8. **El responsive de un design system no es solo `@media`.** Los objetos viven dentro de
   sidebars, drawers y modales; un chart a 320px no puede comportarse como uno a página
   completa. Medido antes de v9.2: **0 container queries en los packs y un solo `@1200`**.
   Se arregla declarando `container-type` en los contenedores correctos (nunca en
   `.nz-table-wrap`, que rompe el sticky-head) y con una prueba viva —`stress-test.html`—
   que enseña el mismo panel en cuatro anchos. Lo que no se mide en su contenedor se
   rompe en silencio.
9. **El recoloreado en vivo se rompe por la UX, no por el CSS.** Las variables hacen
   su trabajo (`fill: var(--serie-N)` recolorea sin re-render), pero recrear los
   pickers dentro del handler `input` corta el arrastre a mitad de gesto, y cambiar
   de tema sin re-aplicar la paleta activa deja colores ilegibles en el nuevo tema.
   Pickers creados una vez, estado «a mano» cuando el usuario toca un picker, y cada
   paleta con tonos light y dark propios.
10. **La cascada se pelea con igualdad de especificidad y la gana el que va después.**
   `[data-nz-marca="x"]` y `:root` puntúan lo mismo (0,1,0): el `<link>` de la marca tiene que
   ir **después** de `tokens.css` o los defaults del sistema pisan la marca y el color elegido
   no aparece por ningún sitio. El lint no lo ve (las clases y los tokens son correctos): se
   diagnostica **midiendo** `getComputedStyle(document.documentElement).getPropertyValue('--nz-marca-600')`
   contra el color pedido (así se cazó y cerró el B02: el atributo declaraba una marca que
   nadie enlazaba). Lo mismo aplica a cualquier custom property que se consuma sobrescrita.
11. **Un helper que devuelve cadena vacía cuando falta el asset esconde el fallo.** Un
   `icono(nombre)` que hace `try { leer svg } catch { '' }` deja un hueco limpio y silencioso
   cuando el fichero no está descargado: el lint pasa, el render no desborda y el elemento
   simplemente no tiene icono (un `<summary>` sin chevron parece un diseño, no un bug).
   Cuenta los assets referenciados contra los presentes, o haz que el helper avise una vez.

## 13b. La elegancia vive en el presupuesto, no en el gusto (medido 2026-10-22)

El ruido visual que David detecta («cajas grandes que se pisan») NO está en los packs:
medido con arnés de superficies, la portada y su shell `cat-*` a mano tienen 104 superficies,
17 anidadas y 67 sombras; las recetas canónicas solo 33-37 superficies y 4 anidadas.
Recortar SOLO las sombras (presupuesto: 1 elemento elevado por región, cajas base =
plano + filete) bajó la portada de 67 sombras a 15 sin tocar nada más: el ruido es
presupuesto, no gusto. Para v10 eso pasa a lint (`sombra-budget`, `anidacion-max=2`,
densidad `compacta` por defecto, `Rejilla` auto-fit minmax en vez de columnas fijas)
y la portada se genera con openui en lugar del shell a mano. Plan: `docs/planes/PLAN-AURORA-v10.md`.

## 13c. Publicar una release y hornear páginas estáticas (verificado end-to-end)

- **Orden de regeneración obligatorio**: `generar-llm-docs.py` → `generar-base-datos.py` →
  `build-catalog.py` → `audit-catalog/audit-html` → `iconos.py todo`. La base de datos lee
  `components.json` (que escribe generar-llm-docs con la `VERSION` nueva): si inviertes el
  orden, se desincroniza y `auditar-base.py --check` la caza (cazado en vivo: 10.1.0 → 10.2.0).
- **El tag se crea sobre el commit final** y entonces `validar-css.py` pasa en verde: antes
  del tag dice «desalineación de versión» — es el huevo-gallina esperado, no lo persigas
  antes de tiempo.
- **Tras un salto de canal**, la CI caza dos rezagados siempre: páginas del site enlazando
  `@vX` viejo (sed de `Aurora@vX/` en `bloques/`) y `iconos/index.html` desincronizado
  (`python scripts/iconos.py todo`; ya va en la regeneración de la CI).
- **El canal congelado sube a propósito en cada release** (`datos/canales.json`): si no,
  `canal.py --check` lo caza con «actualízalo a propósito».
- **Renombrar carpetas del site**: el sed de `x/` NO basta — busca también la forma sin
  barra (`(ROOT / "x")` en scripts y workflows) o dejarás medios caminos rotos.
- **`git add -A` arrastra `scripts/node_modules`** si no está ignorado: revisa
  `git show --stat` antes de pushear.
- **El lint se caza a su autor**: un programa openui-lang con demasiados tonos falla
  `presupuesto-color` y `dos-protagonistas` al hornearlo — ajusta los tonos en el PROGRAMA,
  nunca parchees el HTML generado.

## 14. Interfaces generativas (OpenUI Lang, v9.4)

Cuando el HTML lo escribe **un modelo en tiempo de ejecución**, no le pases esta skill ni le
pidas HTML: dale el lenguaje y la biblioteca. El repositorio ya trae las dos cosas.

```
LLM → OpenUI Lang (8-20 líneas) → parser → runtime vanilla → markup .nz-* del censo
```

| Necesito | De dónde |
|---|---|
| System prompt para el modelo | `openui/PROMPT.md` (36 firmas + reglas de diseño + 3 ejemplos) |
| Biblioteca machine-readable | `openui/aurora.spec.json` (firmas + JSON Schema para el parser) |
| Pintar el resultado en el navegador | `openui/aurora-openui.js` → `AuroraOpenUI.iniciar()` + `.stream(texto, "#lienzo")` |
| Añadir un objeto al lenguaje | `openui/componentes.json` (a mano) → `python3 scripts/generar-openui.py` |
| Verlo funcionando | `openui/index.html` (probador en vivo + plantillas) |
| Empezar por un arquetipo | `openui/plantillas/` + `scripts/plantilla.py` (panel, informe, landing, ajustes, agente) |
| De un encargo a una página | `scripts/generar-web.py --brief encargo.json` (modelo + validación + lint) |
| Que un agente consulte Aurora sin bajar el censo | `scripts/mcp-aurora.py` (MCP en stdio, stdlib pura): `estado_del_sistema`, `buscar_por_necesidad`, `leer_componente`, `validar_html`, `compilar_programa`. Conexión: `claude mcp add aurora -- python scripts/mcp-aurora.py`; autochequeo `--test` (está en la CI) |
| API exacta de UNA familia en texto plano | `llms-full.txt` (411 familias: clases, markup, tokens, alias, noUsar) — generado por `generar-llm-docs.py` |
| De un programa a una página estática (0 JS) | `scripts/hornear.py prog.openui --salida x.html`: compila, pinta en Chrome headless y extrae el `<main>` ya horneado |

```js
await AuroraOpenUI.iniciar();                          // spec + parser oficial (ESM, 96 KB)
AuroraOpenUI.stream(respuestaDelModelo, "#lienzo");    // streaming; cae a parser local sin red
```

**Reglas de la capa generativa:**

1. **OpenUI pone el lenguaje; Aurora pone la verdad visual.** No se enlaza la librería React
   de OpenUI ni su CSS: el bundle oficial pesa 3,2 MB + 320 KB de estilos que competirían con
   el sistema. Solo se usa `@openuidev/lang-core` (parser + prompt).
2. **Cada componente emite markup del censo.** `scripts/auditar-openui.py` falla si el runtime
   emite una clase que no existe, si un renderizador falta, si la spec/PROMPT se ha
   desincronizado del generador o si un enum no está tratado.
3. **El enum castellano no es el modificador.** `tendencia: "sube"` → `nz-kpi__delta--up`.
   Tabla explícita en el runtime; concatenar a ciegas produce clases fantasma.
4. **Un valor de enum por defecto** (`"porDefecto"` en `componentes.json`) se pinta sin
   modificador: no es un fallo, es diseño.
5. **Si el modelo necesita algo que no está**, se añade al censo y a `openui/componentes.json`
   (§9). No se resuelve con CSS en el proyecto.
6. **El parser oficial valida** tipos, aridad y enums antes de pintar: un programa mal formado
   no llega al DOM. Los 3 ejemplos del repo tienen 0 errores con `lang-core` 1.0.1.
7. **`Fila` es `nz-cluster`, no `nz-row`.** Un grupo de botones o chips mide lo que mide; el
   `nz-row` estira a cada hijo al 100 % en móvil y 50 % desde 640 → un botón se vuelve un bloque.
   `nz-row` es para campos y bloques, no para acciones.
8. **Figuras compactas por defecto.** `Barras` emite solo las barras (5 rem) y **no** un
   `<figure class="nz-chart">`: dentro de una `Tarjeta` eso son dos superficies anidadas y un
   muro en una rejilla de 4. `Anillo` sale a 5 rem. `lg` solo para el gráfico protagonista.
9. **Etiquetas de botón cortas** y el botón envuelve (`white-space: normal`, v9.4.1): con
   `nowrap`, una etiqueta larga dentro de una rejilla desbordaba el contenedor.
10. **Parte de la plantilla, no de cero.** Si el encargo encaja con un arquetipo, se rellena
    su plantilla; la estructura ya está auditada y el modelo solo cambia datos.
11. **Qué enlaza cada web lo decide el contrato, no el proyecto** (`CONTRATO.md`): canal vivo
    `@v10` (recibe cada 10.x) o tag exacto (entrega congelada). Nunca `@master`. Un cambio
    aditivo llega solo; renombrar o quitar exige major + `migrar-programas.py`.

## 15. Referencias


- **`Ntizar/Aurora`** — la orden máxima. `LLM.md`, `components.json`, `AGENTS.md`, `COMPOSICION.md`, `bloques/{ejemplos,combos}/`, `examples/golden/`, `specs/`, `paginas/`, `audit/`, `scripts/auditar-uso.py`.
- **`openui/`** — capa generativa: `componentes.json` (fuente), `PROMPT.md`, `aurora.spec.json`, `aurora-openui.js`, `index.html` (probador), `plantillas/`, `ejemplos.json`.
- Este mismo `SKILL.md` **dentro del repo** (la CI valida que no se separe).
- El caso de migración v6→v7 y la auditoría de coherencia, en la skill `design-system-coherence-audit`.
- `references/portada-y-canal.md` — horneado estático de páginas openui-lang (portada del sistema), pipeline `briefs/portada.openui` → `portada.tmpl.html` → `index.html`, y doctrina de canales/release.
- `references/navegacion-del-sitio.md` — la barra de sitio: marca «Aurora» arriba a la izquierda, las cinco secciones, variante del catálogo, tabla de profundidad → prefijo relativo, y receta de arreglo masivo de rutas.
- `references/metodo-diseno.md` — checklists del método de diseño (brief → critique → harden → polish).
- `references/paginas-herramienta.md` — patrón inspector para páginas-herramienta y playgrounds: layout una vista, fit puro del lienzo, pickers y paletas en vivo, guía generada del mismo módulo.
- `scripts/mcp-aurora.py` — servidor MCP del sistema (5 herramientas sobre components.json, base-diseno.json y los auditores; NDJSON sobre stdio, cero dependencias).
- `references/openui-desde-fuera.md` — compilar openui-lang en Node sin Python (`pintar(programa, null)`), validar argumentos contra `$defs` (enum, tipo, obligatorios) porque el runtime no lo hace, reparación mecánica del opcional saltado, presupuesto de color sobre el programa, y las reglas de prompt que hacen que un modelo componga una landing bien.
- El censo visto desde fuera (aplanar `clase → pack`, iconos en línea, prueba diferencial contra `auditar-uso.py`): §1b de esta skill.
- **`iconos/`** — repositorio de iconos numerados (Lucide ISC + Solar CC BY 4.0; el número
  es único entre colecciones): `README.md` (doctrina y
  licencia), `iconos.json` (manifiesto), `sprite.svg`, `index.html` (catálogo). Se amplía con
  `python3 scripts/iconos.py anadir lucide:nombre`; el número no se reutiliza nunca.

Hecho con ❤️ por David Antizar