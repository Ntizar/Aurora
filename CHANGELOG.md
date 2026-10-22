# Changelog — Aurora

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

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
