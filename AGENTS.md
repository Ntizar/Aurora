# AGENTS.md — reglas duras para trabajar en Aurora

Este repositorio es un **design system CSS puro**, sin build y sin dependencias.
Si eres un agente (o una persona con prisa), lee esto antes de tocar nada.

> Aurora **no** es `Ntizar-Aurora` (la versión v5/v6 con liquid glass, mesh y skins).
> Aquí el manifiesto es otro: sólido, sin gradientes, sin glass. No mezcles sus clases.

---

## 1. Las 10 reglas del sistema

1. **Todo lo público vive bajo `.nz-`**. Nada de clases globales sueltas.
2. **Todo valor es un token `--nz-*`**. Ni un `#2563eb` ni un `16px` de diseño a mano.
3. **Sin gradientes, sin `backdrop-filter`, sin `!important`** — salvo las dos
   excepciones oficiales, que este sistema SÍ ofrece y no son un error:
   - **La capa de cristal `p16-cristal.css`** (`.nz-cristal`, `data-nz-estilo="cristal"`):
     es la ÚNICA capa con `backdrop-filter` y gradiente. Uso CONTROLADO — navegación,
     superficie flotante o panel destacado sobre fondo con profundidad; nunca cristal
     anidado ni detrás de tablas y formularios (ley B01 del plan: material, no adorno).
     Trae su fallback opaco y `prefers-reduced-transparency` propio.
   - **`.nz-visually-hidden`, `.nz-vh`, `.nz-print-hide`**: `!important` de ocultación.
   Todo lo demás, cero. Si necesitas cristal en un pack nuevo, va por `p16-cristal`,
   no se reimplementa.
4. **BEM**: `.nz-thing`, `.nz-thing__parte`, `.nz-thing--modificador`, estado `.is-x` o `[aria-*]`.
5. **Responsive first de verdad**: el objeto responde primero a su **contenedor**
   (container queries) y después al viewport (base móvil en 1 columna, crecer con
   `@media (min-width: 640/960/1200/1440)`). Nunca `max-width` como estrategia de página,
   nunca «solo móvil»: el escritorio también es objetivo.
6. **Táctil 44px** en todo lo que se pulsa.
7. **Una clase, un dueño**: una clase se declara en un solo pack.
8. **La base de datos no se escribe a mano.** `datos/base-diseno.json` se genera con
   `scripts/generar-base-datos.py` desde `components.json`, `specs/`, `bloques/recetas/`,
   `bloques/combos/` y `marcas/`; `base.html` es solo la vista. Si se edita a mano, `--check` lo caza.
9. **Responsive por contenedor, no por monitor.** Los objetos compuestos (`.nz-dash-grid`,
   `.nz-split`, `.nz-bento`, `.nz-chart`, `.nz-chat`, `.nz-kanban-wrap`) consultan su
   contenedor. La base sigue siendo móvil; los escalones de contenedor solo suman.
   Cuando el objeto no es contenedor, se declara el contexto con `.nz-cq`.
10. **Un icono es SVG `.nz-icon` y sale del repositorio `iconos/`.** Nunca un símbolo de
    texto (`▦`, `⚙`, `⌕`, `✎`, `▶`) haciendo de icono: cambia de forma según la fuente del
    sistema y rompe la paridad entre móvil, PC y capturas. El dibujo se toma del
    repositorio numerado (`nz-i-NNN`, licencia en `iconos/iconos.json`), no se copia de
    internet ni se dibuja a mano. `scripts/auditar-coherencia.py` lo caza.

## 2. Dónde va cada cosa

| Archivo | Qué es | ¿Se edita a mano? |
|---|---|---|
| `tokens.css` | Fuente única de verdad de los tokens | Sí |
| `packs/pN-*.css` | Los 18 packs, uno por categoría | Sí |
| `packs/p0-catalog.css` | Shell del catálogo (`.cat-*`) | Sí, pero **solo con clases `.cat-*`** |
| `specs/NN.json` | **Fuente de verdad de las demos** (titulo, tag, markup) | Sí |
| `paginas/*.html` | Catálogo generado | **No** — se regenera |
| `index.html` | Portada generada | **No** — se regenera |
| `briefs/portada.openui` | **Fuente de la portada**: programa openui-lang | Sí |
| `briefs/portada.tmpl.html` | Portada horneada (`{{OBJETOS}}`, `{{PROGRAMA}}` sin clavar) | **No** — `scripts/hornear.py` |
| `datos/objetos.json` | Índice para el buscador | **No** — se regenera |
| `datos/base-diseno.json` | Base de datos de diseño (familias, tokens, recetas, combos, marcas) | **No** — se regenera |
| `base.html` | Explorador de la base de datos (vista) | Sí |
| `stress-test.html` | Prueba viva del responsive por contenedor | Sí |
| `bloques/combos/*.html` | Esqueletos de página por tipo | **No** — los genera `generar-llm-docs.py` |
| `bloques/ejemplos/` · `bloques/recetas/` | Páginas completas para copiar | Sí |
| `openui/componentes.json` · `openui/ejemplos.json` | **Fuente** de la capa generativa (qué componente expone qué objeto) | Sí |
| `openui/aurora.spec.json` · `aurora.schema.json` · `PROMPT.md` | Salidas de `generar-openui.py` | **No** — se regeneran |
| `openui/aurora-openui.js` · `openui/index.html` | Runtime vanilla y probador en vivo | Sí |
| `openui/plantillas/*.json` | Plantillas por arquetipo (fuente) | Sí |
| `openui/plantillas/index.json` | Índice generado de plantillas | **No** — `plantilla.py --index` |
| `briefs/*.json` | Encargos de ejemplo para `generar-web.py` | Sí |
| `scripts/hornear.py` | Convierte un `.openui` en HTML estático (Chrome headless) | Sí |
| `datos/canales.json` | A qué versión apunta cada canal (vivo / congelado) | Sí |
| `openui/migraciones/*.json` | Recetas de migración para un major | Sí |
| `docs/planes/` | Planes archivados | Sí, pero no es documentación viva |
| `audit/` | Informe de auditoría | **No** — se regenera |
| `iconos/iconos.json` · `iconos/NNN-*.svg` · `iconos/sprite.svg` · `iconos/index.html` | Repositorio de iconos numerados: manifiesto, fichas, sprite y catálogo | **No** — `scripts/iconos.py` |
| `iconos/README.md` | Doctrina del repositorio de iconos (numeración, licencia, consumo) | Sí |
| `js/catalog.js` · `js/base-datos.js` · `js/iconos.js` | Comportamiento del catálogo, del explorador y del catálogo de iconos | Sí |

### ⚠️ El error que costó más caro

`p0-catalog.css` **no puede declarar clases del sistema**. Si el shell define `.nz-btn`,
como el catálogo carga el shell después de los packs, **pisa el componente real** y el
catálogo enseña algo que no es el sistema. El shell solo tiene clases propias: `.cat-*`
y `.demo-*`.

## 3. Cómo añadir o ampliar un objeto

1. Declara sus clases en el pack que le corresponda.
2. Añade su demo en `specs/NN.json` (una línea de markup, contenido real, sin JavaScript).
3. Regenera y valida:

```bash
# EL ORDEN IMPORTA: components.json manda, base-diseno deriva de él y audit/ lleva la
# versión dentro. Regenerar en otro orden deja ficheros desfasados que la CI caza.
python scripts/generar-llm-docs.py     # LLM.md + components.json + llms.txt
python scripts/generar-base-datos.py   # índice de la base de datos (deriva de components.json)
python scripts/build-catalog.py        # páginas + portada + índice del buscador
python scripts/audit-catalog.py        # auditoría campo a campo → audit/AUDITORIA.md
python scripts/audit-html.py           # informe navegable → audit/index.html
python scripts/validar-css.py          # manifiesto + cobertura (esto es lo que corre CI)
python scripts/auditar-base.py --check # la base de datos, sin referencias rotas
python scripts/auditar-responsive.py   # container queries y escalones no se debilitan
python scripts/generar-openui.py       # capa OpenUI: spec, schema y prompt
python scripts/auditar-openui.py       # censo, deriva, runtime, enums y ejemplos
python scripts/canal.py --check        # canales y versiones en orden
python scripts/plantilla.py --validar-todas
python scripts/generar-web.py --brief briefs/panel-ferroviaria.json --dry-run
python scripts/hornear.py briefs/portada.openui --salida briefs/portada.tmpl.html --plantilla-base
python scripts/iconos.py --check              # sprite y catálogo de iconos, byte a byte
python scripts/auditar-iconos.py --check      # numeración, fichas, licencia e higiene del SVG
```

4. Si `validar-css.py` no dice `RESULTADO: VÁLIDO`, no está terminado.

## 4. Léxico de modificadores

Los 18 packs hablan el mismo idioma. Usa estos modificadores, y solo estos:

| Eje | Modificadores |
|---|---|
| Tamaño | `--2xs` `--xs` `--sm` `--lg` `--xl` |
| Tono | `--brand` `--accent` `--success` `--warning` `--danger` `--info` `--neutral` |
| Énfasis | `--solid` `--soft` `--outline` `--ghost` |
| Disposición | `--vertical` `--horizontal` `--inline` `--compact` `--spacious` `--center` `--between` `--end` |
| Forma | `--square` `--rounded` `--pill` |
| Elevación | `--flat` `--raised` |
| Estado | `.is-active` `.is-disabled` `.is-loading` `.is-done` `.is-error` `.is-empty` `.is-selected` o `[aria-current]` `[aria-selected]` `[aria-expanded]` |

## 5. Consumir el sistema (tú, agente, desde otro proyecto)

- `base.html` — **base de datos de diseño consultable**: busca por lo que quieres construir,
  abre la ficha y copia el markup real. Si dudas, empieza aquí.
- `datos/base-diseno.json` — el mismo índice en machine-readable: familias con markup,
  tokens con valor, recetas, combos, marcas y las 12 leyes.
- `LLM.md` — guía de decisión (~20 KB): qué pack cargar y qué clases usar.
- `components.json` — API completa machine-readable: familia → pack, clases, modificadores,
  partes, tokens y página de demo.
- `bloques/ejemplos/` y `bloques/recetas/` — páginas completas que puedes copiar y adaptar.
- `paginas/` — catálogo con una demo viva por objeto.
- `iconos/` — repositorio de iconos numerados: `iconos/README.md` (doctrina),
  `iconos/index.html` (catálogo navegable), `iconos/iconos.json` (manifiesto con licencia)
  y `iconos/sprite.svg` (uso con `<use href="iconos/sprite.svg#nz-i-042">`).

**No pegues los packs CSS en el prompt** (≈340 KB). Enlaza por CDN con el canal, nunca `@master`:

```html
<!-- web propia: canal vivo (se mueve con cada 9.x) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9/packs/all.css">

<!-- entrega a cliente: tag exacto, congelado -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9.5.0/tokens.css">
```

Canales, compatibilidad, lock y migración: **[CONTRATO.md](CONTRATO.md)**. No se decide aquí.

## 6. Atribución

Todo HTML generado lleva el pie exacto:

```
Hecho con ❤️ por David Antizar
```

Sin variantes, sin «via Mastermind», sin `(L)`.
