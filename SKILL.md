---
name: aurora-design-system
description: "Usa al construir o tocar cualquier web con Aurora (Ntizar/Aurora). El repo manda: resuelve la versión vigente y pide LLM.md + components.json antes de escribir CSS."
version: "8.2.0"
tags: [css, design-system, aurora, ntizar, agent-ready, movil]
---

# Aurora — doctrina única (el repo es la orden máxima)

Design system CSS puro, sin build, sin dependencias, namespaced bajo `.nz-`.
**v8.2.0 · 2176 objetos · 408 familias · 648 demos · 18 categorías · 185 tokens.**
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
git -C C:/Users/d_ant/Projects/Aurora-7 fetch --tags -q
V=$(git -C C:/Users/d_ant/Projects/Aurora-7 describe --tags --abbrev=0)   # p.ej. v8.2.0

# b) sin repo — pregunta a GitHub
curl -s https://api.github.com/repos/Ntizar/Aurora/tags | grep -m1 '"name"'
```

Y lee los **documentos generados** (el repo los produce solo, no los escribas tú):

```bash
# LEER la verdad viva: master / latest (no hay caché que te estorbe, no se sirve a nadie)
curl -s https://cdn.jsdelivr.net/gh/Ntizar/Aurora@master/LLM.md           # ~10 KB
curl -s https://cdn.jsdelivr.net/gh/Ntizar/Aurora@master/components.json  # API completa

# PUBLICAR: siempre el tag resuelto en $V (jsDelivr cachea @master por edge)
#   https://cdn.jsdelivr.net/gh/Ntizar/Aurora@$V/tokens.css
```

Con el repo clonado, tira de disco (más rápido, sin red):
`C:/Users/d_ant/Projects/Aurora-7/{LLM.md,components.json,examples/,SKILL.md}`.

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
| Página completa que ya funciona | `@master/examples/` (login, dashboard, landing, chat-ia, forms) |
| Demo viva de un objeto | `https://ntizar.github.io/Aurora/paginas/NN-*.html` |
| Reglas duras y estado del repo | `@master/AGENTS.md` · `@master/SKILL.md` |

**Corolario:** si algo no está en `components.json`, no existe. No lo inventes: o usas
el objeto que sí existe, o **se añade al repo** (§9), que es donde vive todo el CSS
bueno y de donde lo heredará el siguiente proyecto. Un patrón resuelto dos veces en dos
proyectos es un fallo del sistema, no del proyecto.

## 2. Contrato de sincronía (esta skill ↔ repo)

El repo manda; la skill se reescribe en el mismo ciclo. La CI lo exige:

1. Sube la versión en el repo (`scripts/generar-llm-docs.py` → `VERSION`, README, AGENTS.md).
2. Actualiza **`SKILL.md` dentro del repo** (viaja con el código).
3. Copia ese `SKILL.md` a esta skill local (una sola fuente, sin divergencias).
4. Tag `vX.Y.Z` **en el último commit verde** y `git push origin vX.Y.Z`.
5. `python scripts/validar-css.py` → `RESULTADO: VÁLIDO`. Si no, no está terminado: la
   puerta compara `components.json`, el generador, el tag de git y **este `SKILL.md`**.

Consecuencia práctica: **la versión de esta cabecera es lo único que caduca.** Todo lo
demás (objetos, clases, cifras, móvil) se lee del repo en el PASO 0, así que una versión
nueva del sistema no te deja ciego: solo obliga a refrescar la cabecera.

## 3. CDN pineado (nunca @master para servir CSS en producción)

```html
<html lang="es" data-nz-theme="light">   <!-- o "dark" -->
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.2.0/tokens.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v8.2.0/packs/all.css">
</head>
<body class="nz">
```

Sustituye `v8.0.0` por **`$V`** (el tag que resolviste en el PASO 0): el ejemplo es de la
última vez que se tocó esta cabecera. `all.css` solo para prototipos; en producción enlaza
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

## 5. Las reglas duras (la CI las valida)

1. Todo lo público vive bajo `.nz-` (nada de clases globales).
2. Todo valor es un token `var(--nz-*)` — ni un `#2563eb` ni un `16px` a mano.
3. **0 gradientes, 0 `backdrop-filter`, 0 `!important`** (excepciones: `.nz-visually-hidden`, `.nz-print-hide`, helpers de visibilidad con sufijo `[class]`).
4. BEM: `.nz-thing`, `__parte`, `--modificador`, estado `.is-x` o `[aria-*]`.
5. Mobile-first real: base 1 columna, crecer con `@media (min-width: 640/960/1200)`. Nunca `max-width` como estrategia (los `max-width` de consumidor solo para apagar un patrón móvil, nunca para construirlo).
6. Táctil 44px en todo lo que se pulsa.
7. Una clase, un dueño (un pack). El shell del catálogo (`.cat-*`) jamás declara `.nz-*`.
8. Footer exacto: `Hecho con ❤️ por David Antizar` (emoji U+2764, sin variantes).
9. Todo en castellano (clases incluidas cuando toca: `nz-arbol`, `nz-filezona`, `nz-fieldset__leyenda`).

## 6. Flujo del agente para generar HTML con Aurora

1. **PASO 0**: resuelve `$V` y lee `LLM.md` + `components.json` del repo.
2. **Copia una receta de `examples/`** y quítale lo que no uses.
3. **Escribe el HTML** con los objetos del censo, mobile-first, tokens, 44px.
4. **Verifica el HTML**: `python scripts/auditar-uso.py tu-pagina.html` → clases inventadas, packs que faltan, gradientes, colores a mano, desktop-first, atribución. 0 fallos o no está terminado.
5. **Mídelo en móvil de verdad**, no de vista: viewport a 320/360/390 y comprobar que `document.scrollingElement.scrollWidth == clientWidth` en todas las pestañas/secciones. Es la prueba objetiva de que nada se sale.
6. Verificación visual en preview (el lint no ve la estética). Texto por código (`grep`), no por visión: `vision_analyze` alucina erratas.

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

Léxico cerrado de modificadores (igual en los 15 packs): tamaño `--2xs/--xs/--sm/--lg/--xl`,
tono `--brand/--accent/--success/--warning/--danger/--info/--neutral`, énfasis `--solid/--soft/--outline/--ghost`,
disposición `--vertical/--horizontal/--inline/--compact/--spacious/--center/--between/--end`,
forma `--square/--rounded/--pill`, elevación `--flat/--raised`, estados `.is-active/.is-disabled/.is-loading/.is-done/.is-error/.is-empty/.is-selected`.

## 8. Verificación pre-entrega (checklist)

1. PASO 0 hecho: `$V` resuelto del repo, no de memoria.
2. `auditar-uso.py` sobre el HTML → 0 fallos.
3. `<html lang="es" data-nz-theme="light">` + `<body class="nz">` + CDN pineado a `$V`.
4. Footer exacto con atribución.
5. Móvil medido, no admirado: `scrollWidth == clientWidth` a 320/360/390 en todas las pestañas; táctil 44px.
6. Escritorio y print (si es informe) sin regresión. Mirar la página en preview.

## 9. Ampliar el repo (aquí va todo el CSS bueno)

Cuando un proyecto necesita algo que no existe, **se sube al repo**, no se queda en el
CSS del proyecto:

1. Declara las clases en el pack correspondiente (tokens, sin `!important`, sin gradientes).
2. Añade su demo en `specs/NN.json` (markup en UNA línea, contenido real en castellano, inline solo para geometría con `var(--nz-*)`).
3. Regenera y valida hasta verde: `python scripts/build-catalog.py && python scripts/audit-catalog.py && python scripts/audit-html.py && python scripts/validar-css.py`. Cero «clases declaradas sin demo», cero duplicados entre packs.
4. Sube la versión (`VERSION` + README + AGENTS.md + `SKILL.md`) y tag `vX.Y.Z` en el último commit verde.
5. Actualiza la cabecera de esta skill (una línea) y el tag del proyecto consumidor.

Criterio de admisión: (a) resuelve un problema real y repetido, (b) es mobile-first sin JS,
(c) encaja en el léxico cerrado, (d) lleva demo viva, (e) no duplica nada que ya exista.

## 10. Anti-patrones (errores reales acumulados)

- ❌ Clases de la v6: `nz-card--glass-liquid-*`, `nz-gradient-text`, `nz-aurora-mesh`, `nz-orb`, `u-nz-text-brand`, `data-nz-skin`. En v7 no existen. Títulos destacados: `.nz-h1--brand`.
- ❌ Inventar clases (auditadas en el pasado: `nz-btn--glass-liquid-secondary`, `nz-fieldset__legend` — lo real es `__leyenda`). Si no está en `components.json`, no existe.
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
- ❌ Dejar el patrón resuelto en el proyecto y no subirlo al repo.

## 11. Excepciones vigentes (cuándo NO usar Aurora)

- **Design systems corporativos**: si un equipo pide un CSS con los colores de SU marca (ej. Kaizen/Ineco #1A4488), se crea un sistema propio alineado con su manual, no Aurora.
- **Presentaciones consulting / informes ejecutivos** (estilo McKinsey/BCG): fondo blanco elegante, sin estética tech. David rechazó Aurora para esos entregables.

## 12. Migrar de v6.1 a v7

No es cambiar dos URLs: es reescribir markup. Medido en caso real: de 107 clases usadas
solo 22 existían en v7. Sin equivalencia 1:1 (`nz-card` → `nz-article`/`nz-bento`/`nz-thirds`;
mesh/orbs/3D desaparecen). Receta y script de medición en `references/migracion-v6-a-v7.md`.

## 13. Lecciones que costaron tiempo (verificadas, no teoria)

1. **Corre la cadena ENTERA que corre la CI antes de pushear.** No basta `validar-css.py`: la CI
   pasa además `audit-a11y.py` (inputs sin etiqueta), `audit-tema.py` (supervivencia a modo
   oscuro), `audit-catalog.py`, `audit-html.py` y `auditar-uso.py`. Pushear con la CI en rojo es
   pushear a medias. Cadena completa:
   `python scripts/validar-css.py && python scripts/audit-catalog.py && python scripts/audit-html.py && python scripts/audit-a11y.py && python scripts/audit-tema.py && python scripts/auditar-uso.py --selftest`
2. **El estado inicial de una animación NUNCA es 0.** Arrancar en `scaleY(0)` / `opacity: 0` y
   confiar en que el JS revele deja el dato invisible si el JS falla, si una captura headless
   congela la animación o si la pestaña está en segundo plano. Arranca en `0.55` y pon red de
   seguridad por tiempo: el dato siempre se lee, la animación solo lo adereza.
3. **Verificar en navegador tiene dos trampas.** (a) En pestaña oculta `IntersectionObserver` y
   `setTimeout` no disparan: llama a `Page.bringToFront` y espera antes de medir. (b) Al editar
   CSS/JS en `file://` el navegador sirve caché: `Network.setCacheDisabled(true)` o verás el
   fichero viejo y perseguirás un bug fantasma (y creerás que tu arreglo no funciona).
4. **Un tag de git es inmutable.** El CDN `@vX.Y.Z` seguirá sirviendo el commit viejo aunque
   `master` avance: cualquier funcionalidad nueva necesita versión nueva (`VERSION` en
   `scripts/generar-llm-docs.py`, `components.json`, badge del README, tag) y todas deben decir
   lo mismo — el validador lo comprueba contra el último tag.

## 14. Referencias


- **`Ntizar/Aurora`** — la orden máxima. `LLM.md`, `components.json`, `AGENTS.md`, `examples/`, `specs/`, `paginas/`, `audit/`, `scripts/auditar-uso.py`.
- Este mismo `SKILL.md` **dentro del repo** (la CI valida que no se separe).
- `references/migracion-v6-a-v7.md` y el caso Aurora en la skill `design-system-coherence-audit`.

Hecho con ❤️ por David Antizar