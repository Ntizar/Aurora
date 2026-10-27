# Changelog — Aurora

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

## [10.9.0] — 2026-10-27

### Añadido

- **Marca `monocromo` v2 — light prioritaria**: el lienzo por defecto de la marca
  pasa a blanco pisado (#ffffff) con dato en negro y texto secundario casi
  blanco (#ececec): la jerarquía la dan tamaño y peso, el gris queda como
  affordancia (botones, chips, bordes). El **full black** (#000000, ZeroLeaks
  pleno) se activa con `data-nz-theme="dark"` — decision de David tras iterar
  6 maquetas: «la light prioritaria siempre, con opción de cambiar».
- **Señal tokenizada**: `--nz-mono-azul` / `--nz-mono-naranja` (SOLO gráficos:
  donut, barras, sparkline) y `--nz-signal-danger/warning/success` para el
  semáforo de estado **en punto** (dot de 8px dentro de chip neutro, nunca chip
  lleno). Light lleva tonos oscurecidos AA sobre blanco; dark, vivos sobre negro.
- `scripts/auditar-contraste.py` entiende bloques `[data-nz-theme="dark"]`
  dentro de los ficheros de marca: se aplican solo en el tema oscuro, así que
  pisar lienzos ya no despista al auditor (v1 pasaba por suerte).
- El registro de marca incluye `tema_prioritario`, `lienzo` y `senal` por tema.

## [10.8.0] — 2026-10-27

### Añadido

- **Séptima marca: `monocromo`** — la primera acromática, estilo panel ZeroLeaks:
  tinta #111111 (estructura) + resalte #a3a3a3 (el dato que importa), grises
  neutros sin croma en las dos rampas.
- `scripts/generar-marca.py --mono <nombre>`: una marca monocroma no sale del
  generador de rampas ancladas (la compresión de luz no llega nunca a los claros
  desde una tinta oscura), así que lleva escaleras fijas calibradas y el mismo
  informe de contraste AA que las cromáticas.
- **Estados jerarquizados por luminancia**: success/danger/warning se reparten en
  grises (crítico = más oscuro en claro) y **en oscuro el peligro se invierte a
  blanco** (el chip invertido de los paneles monocromos). La marca pisa solo
  `--nz-success/-danger/-warning` y sus softs/tints; las rampas de estado
  (`--nz-green/red/amber`) quedan intactas para las demás marcas.
- La demo `marcas/`, la portada (data-driven: «Marcas listas» cuenta el registro),
  LLM.md, components.json, la base de datos y `marcas/registro.json` recogen la
  séptima marca.
- `--todas` ya no pierde las marcas registradas fuera de `PRESETS` (ntizar, monocromo…).

## [10.7.0] — 2026-10-26

### Presentaciones en el lenguaje: el modelo compone el deck

- **`Presentacion` + `Slide`** (40 componentes, grupo «Presentación»): el
  programa solo declara slides y contenido — **el runtime pinta el contador
  («02 / 03 · el dato») y las anclas (Anterior · Siguiente · ↺ Repetir) desde
  la posición real**: las posiciones no se escriben, luego no se
  desincronizan. `Slide(children, titulo?, fondo?)` con `fondo="profundo"`
  para el cierre; fuera de deck se pinta como slide suelta.
- **Modo deck automático**: al pintar un `Presentacion` el runtime marca
  `<html data-nz-presentacion>` — el snap del navegador y una **navbar fixed**
  solo en modo presentación: la barra no ocupa flujo, cada slide mide
  exactamente la pantalla y el camino de vuelta nunca se pierde (el primer
  snap la escondía y el flujo desbordaba el 100svh: medido y corregido).
- **Plantilla «presentación»** (sexto arquetipo) y **ejemplo en el prompt**
  del generador: portada, dato y cierre en once líneas.
- **Prueba end-to-end**: programa → `programa-a-html` → navegador: DOM con
  los tres contadores coherentes, anclas con destino, atributo de snap
  activo, lint del sitio en **0 fallos** y captura de las tres slides
  verificada. Docs al día: 40 componentes, 6 arquetipos, 9 combos.

## [10.6.0] — 2026-10-26

### Presentaciones: de charla en beats a deck de verdad

- **Modo presentación (p18)**: `.nz-presentacion` convierte la página en un
  deck — cada `.nz-escenario--pantalla` ocupa el viewport completo y el
  navegador salta de slide en slide con rueda, swype o anclas (scroll-snap,
  **cero JS**). El snap solo se activa cuando el deck es hijo directo de
  `<body>`: una demo suelta en el catálogo no secuestra el scroll de su
  página.
- **Barra de slide**: `.nz-esc-nav` con contador de posición (`02 / 03 · el
  dato`) y anclas reales `← Anterior` / `Siguiente →` / `↺ Repetir`
  (`.nz-esc-nav__enlace--final` en naranja). Táctil 44 px y foco del sistema.
- **Combo `presentacion`** (noveno): esqueleto generado de la demo real —
  deck de tres slides (portada, dato, cierre) con contadores coherentes, listo
  para rellenar y proyectar en F11.
- **Dos demos nuevas en la categoría 18** (20 demos): deck completo con
  snap + barra, y slide de dos columnas (tesis/evidencia) con `nz-split`.
- **Lint afinado**: una página de escenario/presentación deja de leerse como
  «panel» (`ancho-composicion`) y `charla-beats` se queda solo con los packs
  que usa (p3/p4 declarados sin uso) — ambos combos en **0 fallos, 0 avisos**.

## [10.5.0] — 2026-10-26

### Limpieza de portada e índices, esquinas rectas y escala medida

- **Portada al día del proyecto**: texto de «36 componentes» a la cifra viva
  (nuevo placeholder `{{COMPONENTES}}` clavado desde `openui/componentes.json`,
  igual que `{{VIVO}}` y `{{CONGELADO}}` desde `datos/canales.json`). Secciones
  reorganizadas a «cómo funciona hoy»: héroe con cifras fundidas, **Cómo
  funciona** (cuatro pasos reales), comparación, tres puertas, **mapa del
  sistema** (seis tarjetas con enlace a cada índice), marcas, **Versionado y
  agentes** (canales `@v10`/`10.5.0` + MCP) y el programa.
- **Menú único de seis en todos los índices** (portada, base, iconos, marcas,
  openui, recetas, combos): Catálogo · Bloques · Marcas · Iconos · OpenUI ·
  GitHub — mismo orden en cada página; antes cada índice tiraba a su bola
  (faltaba Iconos en la portada, GitHub en cinco).
- **Esquinas rectas en todo el sistema**: la escala `--nz-radius-*` pasa a 0
  (decisión de dirección); los círculos semánticos (`50%` de puntos y avatares)
  se conservan. Consistente por construcción en los 18 packs, el shell del
  catálogo y las demos.
- **Tipografía con topes medidos** (plan §4.2): sección 24 · página 28 ·
  display de landing 38 (antes llegaban a 27/34/50).
- **Doc enderezada**: `bloques/recetas/` **sí existe** (recetas canónicas) —
  se retiró el «404» de SKILL y README; la capa L1 del README deja de citar
  cifras sin fuente.

## [10.4.0] — 2026-10-26

### Del wireframe al producto: rediseño de las referencias y expresión del lenguaje

- **Crítica de diseño atacada en su causa**: las golden eran 3 tarjetas gordas en
  blanco plano y el lenguaje no dejaba hacerlo mejor. De 36 a **38 componentes**
  (todas con clases que ya estaban en el censo):
  - `Hero(children, tono?, densidad?)` — banda a sangre (bg-soft de ritmo o
    `--brand` azul con tinta invertida; dentro, solo Titular/Texto/Etiqueta).
  - `Seccion(..., densidad)` → `nz-section--compact`.
  - `Titular(texto, "display")` — h1 de apertura 4xl con tracking (hero aprobado).
  - `Icono(numero)` — sprite numerado (`iconos/sprite.svg#nz-i-NNN`),
    `aria-hidden`, resuelto bajo subruta con el nuevo `--base` de hornear para
    el sprite (antes solo para CSS).
- **Golden v4**: héroe display sobre azul,8 fichas en rejilla fija de 4 con
  icono arriba, KPIs `sm`, banda de ritmo con sparkline y tabla `compacta`,
  ficha con split60/40 (partidas + historial + progreso).
- **Tests estabilizados**: `probar-producto.py` ya no ata sus aserciones al copy
  (h1 y homeRoute, no frases), la jerarquía sin entradilla consta como «no
  aplica» en vez de reventar, y `pend` se inicializa antes de usarse.
- **Auditor del lenguaje**: el regex no confunde fragmentos de URL (`#nz-i-*`)
  ni `data-nz-*` con clases.

## [10.3.0] — 2026-10-26

### Agent-ready: Aurora que habla con los agentes (referencia affectUI)

- **`scripts/mcp-aurora.py` — servidor MCP** en stdlib pura (NDJSON sobre stdio, cero
  dependencias, autochequeo `--test` en la CI): `estado_del_sistema` (versión y canales
  vivos — el PASO 0 automatizado, nunca de memoria), `buscar_por_necesidad` (índice del
  censo en castellano), `leer_componente` (API exacta: clases, markup, tokens, noUsar),
  `validar_html` (el auditar-uso.py del repo como juez remoto) y `compilar_programa`
  (OpenUI Lang → HTML con marca/packs/firma). Conexión: `claude mcp add aurora -- …`.
- **`llms-full.txt`** — referencia completa por componente (411 familias con markup real,
  tokens, alias y anti-patrón, 255 KB) generada desde `components.json`; `llms.txt` la
  enlaza. Estándar llms-full del ecosistema de agentes.
- **README: «Pantallas completas, no solo piezas»** — plantillas (5 arquetipos), combos
  (8 tipos) y `examples/golden/` presentados como el producto de tres capas; la vía
  «Agente» documenta el MCP; `bloques/recetas/` deja de citarse (404).
- **SKILL.md**: fila MCP y `llms-full.txt` en §14, referencias en §15.

## [10.2.0] — 2026-10-26

### Contrato de producto: inicio, política de URL, firma y marca (plan de mejora)

- **Shell con ruta de inicio (B03/A02)**: `Navegacion` gana la prop opcional
  `inicio` (homeRoute) con prioridad `p.inicio` → `<html data-nz-inicio>` → marca
  sin enlace. La marca es un `<a>` real al inicio del producto y funciona bajo
  subruta desde móvil y desde enlace profundo (`examples/golden/` lo demuestra
  medido en navegador, no prometido).
- **Política de protocolos doble (B04/A04)**: el compilador rechaza el programa
  (`javascript:`/`vbscript:`/`data:` con línea informada) y los renderers del
  runtime no pintan enlaces con esquema inadmisible (`urlAdmitida()`), además del
  auditor sobre DOM real: anclajes resueltos, IDs duplicados, protocolos,
  placeholders `#` en modo producto, base de despliegue y externos con caché.
- **Firma configurable (B05/A08)**: `--firma full|subtle|none` en compilador y
  horneado → `data-nz-firma`; el lint comprueba la política elegida (0 o 1 vez;
  repetida = fallo) y excluye las demos vivas del recuento. Nada de firmas
  incrustadas en piezas sueltas.
- **Preset de marca cargado de verdad (B02/A09)**: `programa-a-html.py` y
  `hornear.py` enlazan `marcas/<marca>.css` detrás de `tokens.css`; marca
  inexistente = error con diagnóstico (sin fallback silencioso). Medido:
  aurora `#2563eb` vs ntizar `#0057ff` en estilos computados.
- **Doctrina de materiales unificada (A01/B01)**: el cristal deja de estar
  «prohibido y implementado»: `p16-cristal` es la ÚNICA capa oficial con blur y
  gradiente, de uso controlado (navegación o superficie flotante), en AGENTS.md,
  COMPOSICION.md (ley 11) y el prompt de LLM. Resto del sistema, cero.
- **Fallbacks de cristal corregidos (B07)**: rama oscura en el fallback sin blur
  (antes caía sobre blanco con texto claro) y `prefers-reduced-transparency`
  que ahora anula el filtro y reasigna superficies opacas por tema.

### Producto de muestra y pruebas de navegador (§15)

- **`examples/golden/`**: landing (`index.html`) y ficha de detalle generadas
  desde `.openui` con modo producto, marca ntizar y firma política — 0 fallos de
  composición, 985 enlaces locales, 0 anclajes rotos.
- **`scripts/probar-producto.py`**: matriz mínima de navegador real (plan §12.3)
  — 18 comprobaciones: marca computada, política de firma, recorrido
  ficha↔inicio con HTTP real, overflow 390/768/1440 en claro y oscuro y
  jerarquía tipográfica computada. Declara sus pendientes; no los aprueba por
  herencia.
- **`scripts/hornear-golden.py`**: única definición del horneado golden; local y
  CI ejecutan lo mismo y `--check` detecta HTML desfasado de su fuente.
- **CI**: golden en el lint, paso de producto en navegador y `--check` de golden
  en la sección de regeneración.

### Documentación alineada (A11)

- README: recuento vivo único (2.195 objetos), badge `10.2.0` (era 9.12.1) y
  canal vivo `@v10` con consumidores de la serie 9 intactos; `CONTRATO.md`
  refleja el mismo canal. Registro de contradicciones A01–A13 en
  `docs/current/contradicciones.md` con estado y garantía de cada una.

### La portada se hornea: una sola fuente, la mitad de tokens

- **`scripts/hornear.py`** cierra el círculo: `.openui` → compila → pinta en Chrome
  headless (con la red servida por HTTP local, que el runtime hace `fetch`) → extrae
  el `<main>` y escribe el HTML estático, sin JS. La portada ya no se escribe a mano:
  10 secciones y 14,5 KB de marcado se mantenían en paralelo al programa y
  divergían (la página prometía «el programa se muestra abajo» y no había nada
  abajo).
- **La portada pasa de 10 bloques a 6** y deja de contar capas internas: cuenta
  qué es OpenUI, qué ahorra y cómo se usa, con tres pasos. El programa completo va
  inyectado por el build dentro de la sección «Transparencia», así que la promesa
  es verificable.
- **Cifras sin deriva**: `build-catalog.py` clava `{{OBJETOS}}`, `{{FAMILIAS}}`,
  `{{PACKS}}` y `{{MARCAS}}` desde el censo. Antes la entradilla decía «411 objetos»
  (son familias) y el KPI «2.195 objetos»: dos cifras incompatibles en la misma
  pantalla.
- **7 packs en vez de 8**: fuera `p13-charts.css` (−29,7 KB) al sustituir las barras
  por un `Progreso`. CSS enlazado: 204 KB → 158 KB (−22 %).
- **Menos tokens por generación**: `generar-web.py --prompt breve` (por defecto)
  omite los tres ejemplos largos de `PROMPT.md` cuando ya se parte de una plantilla
  de arquetipo: 4.164 caracteres menos (≈1.040 tokens) en cada generación.
  `--prompt completo` mantiene el comportamiento anterior.

### OpenUI: el vocabulario puede navegar (y deja de duplicar titulares)

- **`Boton(..., href?)`**: con `href` se pinta como enlace con la misma pinta. Sin
  él, `<button>`. Antes todos los CTA de una página generada eran botones muertos.
- **`Navegacion(marca, enlaces, urls?)`**: `urls` va en paralelo a `enlaces`. Antes
  todos los enlaces salían `href="#"`.
- **`Seccion(titulo)` pinta un rótulo (`nz-lbl`), no un `h2`**: el rótulo y el
  titular competían como dos títulos del mismo tamaño en la misma sección. Cada
  sección tiene ahora un solo `h2`.

### Sistema

- **`.nz-stepper` envuelve en móvil** (`flex-wrap: wrap` hasta 640 px): medido a
  320 px, los pasos 2 y 3 quedaban fuera del viewport y solo se alcanzaban
  arrastrando en horizontal. Desde 640 px sigue siendo la fila de siempre.

## [10.1.0] — 2026-10-22

### La portada explica el proyecto

- **`index.html` es la portada generada con OpenUI**: un programa openui-lang
  (`briefs/portada.openui`, 50 líneas) pre-renderizado en
  `briefs/portada.tmpl.html`; `build-catalog.py` le clava las cifras reales del
  censo y el rango del canal vivo. Narrativa de historia, no de inventario:
  qué es, cómo funciona, el mismo encargo con y sin sistema, tres formas de
  construir, marca tuya, mapas y el programa a la vista. El shell `cat-*`
  desaparece de la portada (su contenido vive en `base.html` y `marcas/`).

### Limpieza de carpetas

- `recetas/`, `examples/` y `combos/` -> **`bloques/{recetas,ejemplos,combos}/`**:
  un solo concepto con tres sabores, como ya se documentaba.
- `data/` y `datos/` fusionadas en **`datos/`** (dos carpetas con nombre casi
  idéntico era ruido puro).
- Retirados `portada-v10.html` y `briefs/portada-v10.openui` (sustituidos por
  `index.html` y `briefs/portada.openui`).

## [10.0.0] — 2026-10-22

### Calma (el presupuesto manda)

- **Presupuesto de sombra en el shell**: las cajas del catálogo (`.cat-demo`, `.cat-cat`,
  `.cat-live-card`, fichas de `base.html`) pasan a plano + filete; la elevación se queda en
  el topbar sticky y los anillos de foco. Medido: la portada baja de 67 elementos con sombra
  a 15 sin tocar el layout.
- **`.nz-dash-grid--ajuste`**: rejilla con `auto-fit minmax(16rem, 1fr)` que encaja las
  piezas al ancho real. El runtime OpenUI la emite por defecto (`Rejilla` en modo `auto`).
- **Lint (auditar-uso.py)**: dos reglas nuevas — `anidacion-superficies` (superficie dentro
  de superficie -> aviso) y `sombra-a-mano` (box-shadow fuera de token -> aviso). Selftest: 15 defectos.

### Generative UI

- **`portada-v10.html`**: la demo de portada generada con openui-lang, ahora pre-renderizada
  y estática (12 KB, cero JS obligatorio, lint 0 fallos y 0 avisos, móvil medido sin desbordes
  en 320/390/1280). El hero del catálogo enlaza a ella.

### Casa

- **Canales**: el canal vivo pasa a `@v10` y el congelado a `@v10.0.0` (salto de major a propósito, `data/canales.json`).

- Licencia **MIT** (`LICENSE` + `NOTICE.md` para terceros y atribución).
- Censo: 2195 objetos. `briefs/portada-v10.openui` versionado como demo del pipeline.

## [9.12.1] — 2026-10-22

### Corregido

- El informe de auditoría (`audit/`) se había quedado en la versión anterior: la CI regenera
  `audit-catalog.py` y `audit-html.py` y compara bytes, así que el tag 9.12.0 salió con el
  informe desfasado aunque todo lo demás estuviera verde en local. Ya está regenerado.
  La lección no es nueva (está escrita en §13: **la cadena entera, en el orden de la CI**),
  pero se me volvió a escapar el mismo paso: ahora `audit/` entra en la comprobación mental
  antes de taggear, no después.

## [9.12.0] — 2026-10-22

### Añadido

- **Segunda colección: Solar (CC BY 4.0)**. 50 iconos **lineales** —el peso de trazo, no los
  `bold`/`outline`/`duotone`, que son otro dibujo y romperían la unidad— con número
  **continuo**: `nz-i-289`…`nz-i-338`. El número sigue siendo único entre colecciones; lo que
  cambia es el estilo, y el manifiesto dice de dónde sale cada uno (`coleccion` + `origen`).
- `iconos/iconos.json` pasa a declarar **`colecciones`** con la licencia y la atribución de
  cada una (ISC · Lucide Contributors; CC BY 4.0 · 480 Design). Un icono de Solar no viaja
  sin su atribución: `auditar-iconos.py` falla si falta.
- `iconos.py` entiende cualquier prefijo de Iconify (`anadir solar:magic-stick-3`), normaliza
  los atributos de trazo de Solar y ya no deduplica nombres **entre** colecciones: dos
  «estrella» legítimas, dos números distintos.
- El catálogo muestra `coleccion:origen` en cada ficha, cuenta las colecciones en la cabecera
  y atribuye las dos licencias al pie.

### Corregido

- El slug del fichero ya no añade `-2` cuando dos iconos comparten nombre: el número del
  prefijo ya hace único el fichero. Lo cazó el auditor en el propio sembrado.

## [9.11.2] — 2026-10-22

### Cambiado

- **La marca escala con su tipografía**: `.nz-brand__mark` pasa de 28/36/22 px a
  1,75/2,25/1,7 **em**. Un logotipo en una cabecera grande o en una tarjeta pequeña crece y
  encoge con el texto en vez de quedarse clavado en píxeles.
- **Logos fluidos**: en `.nz-logos`, las imágenes y los textos llevan `max-height: 1.75em`
  (antes 28 px) y `max-width: 100%` con `object-fit: contain`; un logotipo ancho se encoge en
  su hueco en vez de desbordar. Los hijos ya no fuerzan el ancho del contenedor.
- **Nube de logotipos por contenedor**: `.nz-logo-nube` deja los escalones 1→2→4 columnas por
  `@media` y usa `auto-fit` con `minmax(min(100%, 12rem), 1fr)`. En una barra lateral de 20rem
  ya no intenta cuatro columnas; en una página ancha pasa de cuatro sin media queries.
- `.nz-brand` y `.nz-logomark` no pueden ser más anchos que su caja (`max-width: 100%`).

## [9.11.1] — 2026-10-22

### Corregido

- `examples/forms.html` usaba `.nz-icon` (lo metió el barrido de glifos) sin enlazar
  `p9-media.css`: la receta se servía con el icono sin estilo. Lo cazó el lint del consumidor
  en la CI, no en local — el paso que audita `examples/` es el único que se me quedó sin
  correr antes de taggear. Regla para la próxima: **la cadena entera, en el orden de la CI**.

## [9.11.0] — 2026-10-22

### Corregido

- **129 símbolos de texto haciendo de icono** en el catálogo (`★ ♥ ♡ 🛒 ☰ ⚠ 📦 🔍 📂 🎉 🔗 ✉ ➤
  🔖 ✓ ✗ ⛔ 💬 ◆ ● ■ ▲ ▸ ▾ ◍ ▢ ▤ ◦ ⬆ ↻`). La regla 10 llevaba incumplida desde siempre por dos
  motivos: `migrar-iconos.py` solo conocía un puñado de glifos y `paginas/` no pasa por el lint
  del consumidor, así que nadie lo veía. Ahora son SVG del sistema, el migrador los conoce
  todos (incluida la pasada para «5★» y «★★★★★») y el único glifo de texto que queda es la
  atribución y las teclas de `<kbd>`, que son tipografía, no icono.
- Un `<button>` del feed se quedó sin nombre accesible al cambiar el glifo por un SVG: lleva
  `aria-label`. Lo cazó `audit-a11y.py`.

### Añadido / Cambiado

- **`.nz-icon--xl` pasa de `2rem` a `2em`**: el icono grande también sigue a la tipografía, así
  que en un panel con texto a 13 px no se queda clavado en 32 px.
- **`.nz-grid-auto`** (ya existía) se endurece con `minmax(min(100%, 240px), 1fr)`: una rejilla
  de fichas ya no desborda dentro de un contenedor estrecho. `--compact` (160 px) y
  `--spacious` (320 px) ganan **eje de tamaño** —antes solo cambiaban el hueco—, y el catálogo
  de iconos los usa: dos columnas desde 360 px, seis o más en escritorio.
- La demo de «Aspect ratio» deja de saltarse el sistema con un `style="grid-template-columns:…"`
  inline: usa el modificador.
- Nueva demo «Rejilla automática: caben las que quepan» con los tres tamaños.

## [9.10.0] — 2026-10-22

### Añadido

- **Tono del icono**: `.nz-icon--accent`, `--success`, `--warning`, `--danger`, `--info`,
  `--invert`. El trazo es `currentColor`, así que el color es un modificador y no un segundo
  fichero: el naranja (acento) entra en la iconografía sin duplicar los 288 SVG.
- **Grosor**: `.nz-icon--fino` (1,5) y `.nz-icon--grueso` (2,25), con tokens
  `--nz-icon-stroke-fino` y `--nz-icon-stroke-grueso`.
- **Catálogo de iconos con selector de tono** en vivo (Neutro · Acento · Marca · Éxito ·
  Peligro · Contorno) y `?tono=acento` para abrirlo directamente en naranja. El código que
  copia el botón se lleva el tono puesto.
- Demo nueva en `specs/09.json` con los siete modificadores.

### Corregido

- `specs/06`, `specs/07` y `specs/09` usaban **✳, ✦ y `!` de texto como iconos** — regla 10
  del sistema, incumplida desde siempre porque el migrador no conocía esos símbolos y
  `paginas/` no pasa por el lint del consumidor. Ahora son SVG y `migrar-iconos.py` los
  conoce para que no vuelvan.

## [9.9.1] — 2026-10-22

### Corregido

- `iconos.py anadir --nombre` bautizaba **todos** los iconos del comando con el mismo nombre
  castellano: el segundo acababa en `290-pastilla-2.svg` y `auditar-iconos.py` lo rechazaba
  con razón. Ahora `--nombre` exige un solo icono por invocación.
- `anadir` permitía dos iconos con el mismo nombre. El número los distingue, el nombre no:
  ahora se niega y dice qué número lo tiene ya.

## [9.9.0] — 2026-10-22

### Añadido

- **Repositorio de iconos numerados** (`iconos/`): **288 iconos** de Lucide (ISC) con número
  estable `nz-i-NNN` que **no se reutiliza nunca** — el número es la referencia, el nombre es
  la comodidad. Cada icono es un SVG de 24×24 con `fill="none"` y `stroke="currentColor"`
  (sin un solo color a mano), así que funciona igual en claro y en oscuro.
- **`iconos/iconos.json`**: manifiesto con número, id de Lucide, nombre castellano, grupo,
  licencia, alias y hash de cada fichero. La licencia viaja con el icono: sin atribución no
  se sirve.
- **`iconos/sprite.svg`** (288 `<symbol id="nz-i-NNN">`) e **`iconos/index.html`**: catálogo
  navegable por número, nombre o id de Lucide, con buscador y copia del código al portapapeles.
- **`scripts/iconos.py`**: `sembrar`, `anadir`, `retirar` (deja el hueco declarado),
  `listar`, `sprite`, `catalogo` y `--check` (compara bytes: el catálogo no se edita a mano).
- **`scripts/auditar-iconos.py`**: numeración sin huecos ni repetidos, ficha ↔ fichero,
  higiene del SVG (ni color ni `stroke-width` ni `<text>`), sprite y catálogo sincronizados.
  Va en la CI, junto al lint del catálogo.
- `components.json` publica el bloque `iconos` (total, grupos, manifiesto, sprite, uso) y
  `LLM.md` explica cómo consumirlo: un agente ya no puede elegir «un emoji que parezca un
  icono» sin salirse de lo escrito.

### Corregido

- `README.md` anunciaba la versión **9.6.0** con el sistema en 9.8.0 (badge y ejemplo de
  entrega congelada).

## [9.8.0] — 2026-10-21

### Añadido

- **`canal.py --purgar`**: purga los 34 ficheros del canal vivo en jsDelivr y **verifica** que
  `@v9` sirve ya la versión vigente. Sin esto, el rango puede seguir sirviendo la versión
  anterior durante horas y el canal vivo miente. Forma parte del release (CONTRATO.md §2b).

### Corregido

- El canal vivo servía **9.5.0** con el tag ya en 9.7.1: lo arregló la purga. La promesa «un
  cambio llega solo» tiene una condición que ahora está escrita y automatizada.

## [9.7.1] — 2026-10-21

### Corregido

- **`generar-web.py` no arrancaba en CI**: leía `~/.hermes/config.yaml` sin comprobar que
  existe, así que el humo `--sin-modelo` (que no necesita modelo) reventaba en un runner
  limpio. Ahora la configuración es opcional: sin clave avisa y ofrece `--sin-modelo`.
  Lo pilló la CI, no el portátil — que es exactamente para lo que está.

## [9.7.0] — 2026-10-21

**El conector: de un encargo a una página, con el modelo y con el lint delante.** Y la portada
cuenta por fin lo nuevo: el sistema entero, con la capa generativa como protagonista.

### Añadido

- **`scripts/generar-web.py`** — cadena completa: brief → plantilla del arquetipo → modelo
  (`PROMPT.md` como system prompt) → validación → página → `auditar-uso`. Si el modelo falla,
  **una segunda oportunidad con los errores delante**; si vuelve a fallar, usa la plantilla con
  los datos del brief y lo dice. Modelo y clave salen de `~/.hermes/config.yaml` / `.env`.
- `briefs/` — dos encargos de ejemplo (panel de flota e informe de energía) y su README.
- CI: humo del conector sin red (`--sin-modelo`) y validación de plantillas.

### Cambiado

- **Portada reescrita de arriba abajo** (generada desde `build-catalog.py`):
  - Hero nuevo: un sistema, tres formas de construir (a mano, agente, modelo).
  - Sección **Generative UI** con las cuatro capas, el par «lo que escribe el modelo / lo que
    pinta Aurora» (código real y su render), los cuatro pasos (valida, pinta, sella, versiona)
    y las cinco plantillas.
  - Sección **dos canales** con los snippets vivo y congelado, el rango leído de
    `data/canales.json`.
  - Las tarjetas de OpenUI salen de «el sistema en cinco ideas» para no duplicar: esa sección
    vuelve a ser de cinco.
- Stat del hero pasa a contar lo que el sistema hace: 36 componentes generativos, 5 arquetipos,
  6 marcas, 0 clases inventadas.

### Verificado

- Conector probado contra la API real: 1 intento, 5.527 tokens de entrada y 987 de salida,
  19 líneas de programa, **0 fallos de lint**.
- Portada: `auditar-uso` 0 fallos · coherencia VÁLIDA · `validar-css` VÁLIDO · a11y VÁLIDO.

## [9.6.0] — 2026-10-21

**Plantillas por arquetipo: el esqueleto decidido, el modelo rellena.** Es la pieza que
convierte «generar webs con un modelo» en algo que siempre sale con el mismo sistema.

### Añadido

- `openui/plantillas/` — cinco arquetipos completos y válidos: **panel-operativo**, **informe**,
  **landing**, **ajustes** y **agente**, con variables de texto (`{{titulo}}`, `{{entidad}}`…).
  No llevan lógica: la estructura la decide Aurora, los datos los pone el modelo.
- **`scripts/plantilla.py`** — `--lista`, `--var clave=valor`, `--salida`, `--validar-todas`
  (CI) y `--index` (genera el índice que consume la demo). Una plantilla solo se emite si el
  programa resultante **valida**: si no, se niega.
- `openui/plantillas/index.json` — índice generado, con el programa y sus variables.
- **Demo**: sección «Plantillas por arquetipo» con un botón por arquetipo que lo carga en el
  probador (las variables se sustituyen por sus valores por defecto).
- `PROMPT.md` §Plantillas: el modelo recibe nombre, descripción y variables de cada arquetipo,
  y la regla de **partir de la plantilla en vez de inventar estructura**.
- Portada: tarjetas de «Plantillas por arquetipo» y «Contrato de versiones».

### Verificado

- 5/5 plantillas válidas con el parser oficial y con el analizador del repo.
- Cadena completa probada en dos arquetipos: plantilla → programa → página con
  `programa-a-html.py` → `auditar-uso.py`: **0 fallos y 0 avisos**.
- `PROMPT.md` sigue por debajo del presupuesto (14,4 KB de 16).

## [9.5.0] — 2026-10-21

**Canales, lock y migrador: cómo cambia Aurora a todas las webs a la vez** — y cómo se
deshace. Más la limpieza del proyecto: README reescrito y contrato en un solo documento.

### Añadido

- **`CONTRATO.md`** — qué propaga solo (tokens, CSS, aditivo) y qué no (renombrar, quitar,
  estructura), semántica de versiones, lock por web, rollback y regeneración.
- **`data/canales.json`** — canal **vivo** (`@v9`, webs propias) y **congelado** (tag exacto,
  entregas). El rango cubre solo el major.
- **`scripts/canal.py`** — resuelve el canal a tag exacto desde los tags de git, `--check`
  para CI (`--online` comprueba además el CDN), `--lock` y `--verificar` para cada web.
- **`scripts/programa-a-html.py`** — de un `.openui` a una página completa: resuelve la
  marca, el tema, el canal, **solo los packs que el programa usa** y deja el runtime puesto.
- **`scripts/migrar-programas.py`** + `openui/migraciones/` — migra programas en un major:
  renombra componentes y **se niega** si el resultado no valida; los cambios de props
  posicionales los marca como manuales con la línea exacta.
- `auditar-uso.py` entiende páginas generadas: lee el programa embebido y justifica los
  packs que el runtime usará al pintar. Una página generada pasa el lint con 0 avisos.

### Cambiado

- **README reescrito** de cero: qué es, empezar en diez segundos, las cuatro capas, tres
  formas de consumirlo, garantías y estructura. De 295 líneas de acumulación a una portada
  que se lee en tres minutos.
- `AGENTS.md`: el snippet de consumo ya no pinea `v9.2.0` (estaba viejo): explica los canales
  y remite al contrato. Nuevos scripts en la cadena.
- `LLM.md` §8b (generado): canales y lock, con el rango leído de `data/canales.json`.

### Notas

- Un tag publicado es inmutable: lo que se mueve es el rango del canal, no el tag.
- El canal vivo llega a todas las webs a la vez: CI verde → canario → 48 h → resto.

## [9.4.1] — 2026-10-21

Correcciones salidas de la auditoría externa de la demo y del ojo de David: **botones que no
respondían** y **figuras demasiado grandes**. Una en el sistema, dos en la capa generativa, y
la demo deja de esconder sus propios errores.

### Corregido

- **`.nz-btn` desbordaba con etiquetas largas** (`p4-actions.css`): `white-space: nowrap`
  impedía encoger y, dentro de `nz-row`, el botón se salía del contenedor. Ahora
  `white-space: normal` + `text-wrap: balance` + `max-width: 100%`: la etiqueta envuelve y el
  botón nunca es más ancho que su caja. Es un fallo del sistema, no del proyecto que lo sufre.
- **`Fila` estiraba a los hijos**: emitía `nz-row` (100 % en móvil, 50 % desde 640) y convertía
  un grupo de botones en bloques enormes. Ahora emite `nz-cluster`: mide lo que mide y envuelve.
- **`Barras` dibujaba un muro**: metía un `<figure class="nz-chart">` (superficie + 8 rem) aunque
  ya fuera dentro de una `Tarjeta` → doble superficie. Ahora emite solo las barras, a 5 rem.
  `Anillo` baja a 5 rem y admite `lg` para el dato protagonista.
- **La demo escondía los errores**: un programa inválido dejaba el lienzo vacío y un contador.
  Ahora muestra una alerta con código traducido, componente, path y mensaje (recortado), y hay
  un botón «Probar un error» para verlo.
- **«179 clases emitidas» no tenía criterio reproducible** (auditoría). La cifra ahora se mide
  en el navegador sobre los 3 ejemplos: 121 clases distintas. El benchmark se etiqueta como del
  vendedor (OpenUI) y se añade el dato frente a YAML.

### Notas

- `auditar-openui.py` mantiene las cifras honestas: informa de las clases del censo
  **referenciadas por el runtime** (182), que es otra cuenta distinta de las emitidas.

## [9.4.0] — 2026-10-21

**Generative UI: OpenUI Lang sobre el censo.** Aurora deja de ser solo el CSS que un agente
lee; ahora es también la biblioteca que un modelo *usa* en tiempo de ejecución.

El modelo emite 8-20 líneas de openui-lang (`root = Pagina([...])`) en vez de HTML+CSS: un
52 % menos de tokens que JSON según el benchmark público de OpenUI. Aurora conserva el
control visual porque el lenguaje no puede inventar clases: elige entre 36 componentes del
censo y el runtime emite su markup real.

### Añadido

- `openui/componentes.json` — 36 componentes Aurora expuestos, derivados del censo.
- `openui/aurora-openui.js` — runtime vanilla (sin React, sin build): OpenUI Lang → DOM
  con clases `.nz-*`; streaming, y parser local de reserva si el CDN no responde.
- `openui/PROMPT.md` + `aurora.spec.json` + `aurora.schema.json` — generados desde la fuente.
- `openui/ejemplos.json` — 3 programas reales (flota, informe, agente) validados con el
  parser oficial `@openuidev/lang-core` 1.0.1: 0 errores.
- `openui/index.html` — probador en vivo con streaming simulado, telemetría y el HTML
  generado a la vista.
- `scripts/generar-openui.py` y `scripts/auditar-openui.py` — generador con `--check` y
  puerta de CI (censo, deriva, renderizadores, enums, ejemplos).
- Portada: tarjeta hacia el probador. `LLM.md` §10, `README`, `AGENTS.md`.

### Corregido

- `auditar-uso.py` escaneaba el **interior** de `<pre>/<code>/<textarea>`: un snippet con
  `href=".../packs/all.css"` contaba como CSS enlazado y daba todos los packs por muertos.
  Ahora se vacía el contenido y se conserva la etiqueta.
- `nz-kpi__delta--sube` y equivalentes: el enum castellano de `tendencia` se concatenaba
  tal cual al modificador inglés (`--up/--down/--flat`). Cazado por el test de render; el
  auditor ahora exige que cada valor de enum esté tratado o sea modificador real.

### Garantías medidas

- 3/3 ejemplos: 0 errores del parser oficial · 123 clases distintas emitidas, 0 fuera del censo.
- Streaming = render de una vez (mismo DOM).
- `auditar-uso.py openui/index.html` → 0 fallos.

## [9.3.1] — 2026-10-19

Corrección de concepto (David): el sistema no es «mobile first», es **RESPONSIVE first**.
El objeto responde primero a su contenedor (container queries, v9.2) y después al viewport;
el móvil es el punto de partida de la escala (320px), no la identidad del sistema. La v8.4
ya lo demostró: pensar «solo móvil» dejó el escritorio a la deriva.

### Corregido

- Doctrina renombrada en todas las fuentes: regla del sistema, LLM.md (anti-patrón,
  llms.txt, `responsiveFirst` en components.json), README, SKILL.md, cabecera y
  breakpoints de `tokens.css`, cabeceras de 9 packs, portada del catálogo y los
  mensajes de `auditar-responsive.py` y `auditar-uso.py`.

## [9.3.0] — 2026-10-19

Color de acento legible en cualquier fondo y tokens en OKLch. Aplica el patrón
verificado de oneo-me/manta (tokens semánticos light/dark) y la gobernanza de
capas de oneo-me/onevra.

### Añadido

- **Tokens semánticos de acento**: `--nz-accent-text` (texto con color de acento
  sobre fondo: acento-700 en claro, acento-400 en oscuro) y `--nz-accent-ink`
  (tinta sobre relleno de acento: gray-950 en claro, el fondo oscuro en dark).
  El blanco sobre acento-500 medía 2,80:1 (F en WCAG); ahora todos los pares
  de acento pasan su mínimo (4,5:1 texto, verificado por tema y por marca).
- **Doble declaración OKLch**: los 59 tokens de color de `tokens.css` llevan
  debajo su gemela `oklch(...)` (conversión exacta, round-trip verificado).
  Navegadores modernos usan OKLch; los antiguos quedan con el hex. Sin JS.
- **`scripts/auditar-contraste.py`**: auditoría WCAG de los pares semánticos por
  tema (claro/oscuro) y por preset de marca, con cascada var() y resolución de
  `color-mix`; además verifica la paridad de la doble declaración OKLch.
  CI-ready (exit 1 si falla), `--informe` para modo consultivo.
- **Gobernanza de capas en AGENTS.md** (refina upstream / rellena huecos /
  defer to upstream) — pendiente de aprobación explícita del fichero protegido.

### Corregido

- 14 rellenos de acento dejaban el texto en blanco (`--nz-gray-0`) o en
  `--nz-text-invert` (blanco en claro): badges, botón y segmented de acento,
  banner, callout ribbon, treemap, tooltip, KPI, audio, inputgroup, actbar.
- 9 usos del acento como color de texto directo pasan a `--nz-accent-text`.
- `generar-marca.py`: garantiza AA del par texto-acento s/ acento-soft (700
  sobre 50 ≥ 4,5) oscureciendo el 700 lo justo; el CLI registra la marca en
  `marcas/registro.json` (antes una marca creada por CLI se perdía con `--todas`).
- Regenerados presets con la garantía nueva: esmeralda (3,82→4,58) e indigo
  (4,13→4,60). `ntizar` restaurada vía motor: `ntizar.css` idéntico byte a byte.

## [9.2.0] — 2026-10-17


Release de cierre de la línea 9. Las fases 9.0 y 9.1 se desarrollaron sin tag
intermedio; se publican juntas aquí para que el CDN tenga una sola foto coherente.

### Añadido

- **Migración de iconos de texto a SVG**: 60 bloques de demos de 12 categorías, el shell
  del catálogo y `examples/login.html`. Los símbolos (`▦ ⚙ ⌕ ✎ ▶`) cambian de forma según
  la fuente del sistema; los SVG no.
- `scripts/auditar-coherencia.py`: puerta que detecta iconos de texto, recetas forzadas a
  dark, CDN con versión vieja y footers sin atribución. Baseline: 211 fallos; hoy: 0.
- `docs/RUTA-COHERENCIA.md`: ruta por fases para coherencia total, responsive real y
  detalles de buen gusto.

- **Base de datos de diseño**: `base.html` (explorador con búsqueda, filtros, ficha,
  preview real y copia de markup) y `datos/base-diseno.json` (índice machine-readable
  de 411 familias, 2.186 clases, 189 tokens, 6 recetas, 5 ejemplos, 8 combos, 6 marcas,
  12 leyes y el léxico).
- Generadores y puertas: `scripts/generar-base-datos.py` (determinista, `--check`),
  `scripts/auditar-base.py` (referencias, mínimos, sincronía) y
  `scripts/auditar-responsive.py` (container queries, escalones y stress test).
- **Responsive multifunción**: `container-type` en `.nz-dash-grid`, `.nz-split`,
  `.nz-thirds`, `.nz-bento`, `.nz-chart`, `.nz-chat` y `.nz-kanban-wrap`; utilidad
  `.nz-cq` para declarar el contexto; escalones `@media (min-width: 1200px)` y
  `(min-width: 1440px)` en `p1`, `p13`, `p15` y `p17`.
- **`stress-test.html`**: el mismo panel en 320, 480, 768 y ancho completo, con el
  mismo HTML y las mismas clases.
- Sección de base de datos y nueva galería de cifras en la portada.
- `CHANGELOG.md` y `docs/planes/` (planes archivados).
- `combos/` entra en git: `components.json` ya los enlazaba y en la web daban 404.

### Cambiado

- `components.json` enriquecido por familia: clases, partes, modificadores, tokens,
  markup mínimo, `noUsar` y alias inversos. `LLM.md` y `llms.txt` lo reflejan.
- La portada deja de enlazar Google Fonts: Inter ya viaja en `tokens.css`. El probador
  de tipografías sigue cargando las fuentes de muestra solo bajo demanda.
- Versión unificada a 9.2.0 en `components.json`, `LLM.md`, `llms.txt`, `index.html`,
  README, AGENTS y SKILL.
- Reglas duras: 9 en vez de 7 (base de datos generada y responsive por contenedor).

### Corregido

- En móvil, la ficha del explorador aparece **antes** de la lista de resultados (`order: -1`):
  al tocar una tarjeta se lee la ficha sin recorrer 655 tarjetas. En escritorio sigue a la derecha.
- Los símbolos de texto de la barra y el buscador (`⌂ ¶ ◐ ▦ ✓ ⌕`) pasan a SVG `.nz-icon`:
  la ley 10 del sistema prohíbe fuentes de iconos improvisadas.
- La base de datos estrena dirección **editorial**: hero asimétrico con una `A` de fondo,
  índice de categorías tipo revista, rejilla de archivo numerada y ficha con lomo de acento.
  Sin gradientes ni glass: papel y tinta.

### Eliminado

- `PLAN-AURORA.md` y `PLAN-AURORA-9.md` de la raíz → `docs/planes/`.
- `scripts/spec-04.py`, `spec-13.py`, `spec-14.py` y `scripts/trasfondo/` (sondas
  one-off ya volcadas a `specs/`).
- `audit/MOVIL.md` y `audit/movil.json` (25-09, caducados; se regeneran con
  `scripts/auditar-movil.py` en el PC).

## [9.1.0] — 2026-10-16

### Añadido

- `components.json` como API de consulta LLM de primera: markup mínimo por familia,
  tokens consumidos, `noUsar` y alias.
- `llms.txt` y esqueletos `combos/*.html` por tipo de página.
- 150 alias EN→ES y el léxico cerrado de modificadores.

## [9.0.0] — 2026-10-15

### Añadido

- Plan Aurora 9: responsive multifunción (container queries) y API LLM.
- Primeros contenedores de consulta y escalones anchos.

## [8.4.2] — 2026-10-09

### Corregido

- El sistema cumple su propio mínimo tipográfico: 12px solo para datos, 13px de
  interfaz, pesos por token y el 800 retirado.
- Inter variable self-hosted en `tokens.css`; escritorio con lienzo 72 → 84 → 96rem;
  `.nz-container--app` para herramientas.

Hecho con ❤️ por David Antizar
