# Changelog — Aurora

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

## [9.2.0] — 2026-10-17

Release de cierre de la línea 9. Las fases 9.0 y 9.1 se desarrollaron sin tag
intermedio; se publican juntas aquí para que el CDN tenga una sola foto coherente.

### Añadido

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
