# AGENTS.md — reglas duras para trabajar en Aurora

Este repositorio es un **design system CSS puro**, sin build y sin dependencias.
Si eres un agente (o una persona con prisa), lee esto antes de tocar nada.

> Aurora **no** es `Ntizar-Aurora` (la versión v5/v6 con liquid glass, mesh y skins).
> Aquí el manifiesto es otro: sólido, sin gradientes, sin glass. No mezcles sus clases.

---

## 1. Las 10 reglas del sistema

1. **Todo lo público vive bajo `.nz-`**. Nada de clases globales sueltas.
2. **Todo valor es un token `--nz-*`**. Ni un `#2563eb` ni un `16px` de diseño a mano.
3. **Sin gradientes, sin `backdrop-filter`, sin `!important`**
   (solo se admiten en `.nz-visually-hidden`, `.nz-vh` y `.nz-print-hide`).
4. **BEM**: `.nz-thing`, `.nz-thing__parte`, `.nz-thing--modificador`, estado `.is-x` o `[aria-*]`.
5. **Mobile-first de verdad**: base 1 columna y se crece con `@media (min-width: …)`
   (640 / 960 / 1200 / 1440). Nunca `max-width` como estrategia de página.
6. **Táctil 44px** en todo lo que se pulsa.
7. **Una clase, un dueño**: una clase se declara en un solo pack.
8. **La base de datos no se escribe a mano.** `datos/base-diseno.json` se genera con
   `scripts/generar-base-datos.py` desde `components.json`, `specs/`, `recetas/`,
   `combos/` y `marcas/`; `base.html` es solo la vista. Si se edita a mano, `--check` lo caza.
9. **Responsive por contenedor, no por monitor.** Los objetos compuestos (`.nz-dash-grid`,
   `.nz-split`, `.nz-bento`, `.nz-chart`, `.nz-chat`, `.nz-kanban-wrap`) consultan su
   contenedor. La base sigue siendo móvil; los escalones de contenedor solo suman.
   Cuando el objeto no es contenedor, se declara el contexto con `.nz-cq`.
10. **Un icono es SVG `.nz-icon`.** Nunca un símbolo de texto (`▦`, `⚙`, `⌕`, `✎`, `▶`)
    haciendo de icono: cambia de forma según la fuente del sistema y rompe la paridad
    entre móvil, PC y capturas. `scripts/auditar-coherencia.py` lo caza.

## 2. Dónde va cada cosa

| Archivo | Qué es | ¿Se edita a mano? |
|---|---|---|
| `tokens.css` | Fuente única de verdad de los tokens | Sí |
| `packs/pN-*.css` | Los 18 packs, uno por categoría | Sí |
| `packs/p0-catalog.css` | Shell del catálogo (`.cat-*`) | Sí, pero **solo con clases `.cat-*`** |
| `specs/NN.json` | **Fuente de verdad de las demos** (titulo, tag, markup) | Sí |
| `paginas/*.html` | Catálogo generado | **No** — se regenera |
| `index.html` | Portada generada | **No** — se regenera |
| `datos/objetos.json` | Índice para el buscador | **No** — se regenera |
| `datos/base-diseno.json` | Base de datos de diseño (familias, tokens, recetas, combos, marcas) | **No** — se regenera |
| `base.html` | Explorador de la base de datos (vista) | Sí |
| `stress-test.html` | Prueba viva del responsive por contenedor | Sí |
| `combos/*.html` | Esqueletos de página por tipo | **No** — los genera `generar-llm-docs.py` |
| `examples/` · `recetas/` | Páginas completas para copiar | Sí |
| `docs/planes/` | Planes archivados | Sí, pero no es documentación viva |
| `audit/` | Informe de auditoría | **No** — se regenera |
| `js/catalog.js` · `js/base-datos.js` | Comportamiento del catálogo y del explorador | Sí |

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
python scripts/generar-base-datos.py   # índice de la base de datos
python scripts/build-catalog.py        # páginas + portada + índice del buscador
python scripts/generar-llm-docs.py     # LLM.md + components.json + llms.txt
python scripts/audit-catalog.py        # auditoría campo a campo → audit/AUDITORIA.md
python scripts/audit-html.py           # informe navegable → audit/index.html
python scripts/validar-css.py          # manifiesto + cobertura (esto es lo que corre CI)
python scripts/auditar-base.py --check # la base de datos, sin referencias rotas
python scripts/auditar-responsive.py   # container queries y escalones no se debilitan
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
- `examples/` y `recetas/` — páginas completas que puedes copiar y adaptar.
- `paginas/` — catálogo con una demo viva por objeto.

**No pegues los packs CSS en el prompt** (≈340 KB). Enlaza por CDN (siempre pineado, nunca @master):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9.2.0/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9.2.0/packs/all.css">
```

## 6. Atribución

Todo HTML generado lleva el pie exacto:

```
Hecho con ❤️ por David Antizar
```

Sin variantes, sin «via Mastermind», sin `(L)`.
