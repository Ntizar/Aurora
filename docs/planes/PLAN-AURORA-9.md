# Plan Aurora 9 — Responsive multifunción y API de consulta LLM

> **Objetivo:** que Aurora sea un **sistema de diseño global y multifunción**: los objetos
> se adaptan a su contenedor (no solo al viewport) y un agente LLM resuelve dudas de uso
> sin leer jamás los 340 KB de packs.
>
> **Alcance:** `Ntizar/Aurora` (v8.4.2). Es el plan que sigue a PLAN-AURORA.md (v7.2.2 →
> v8.4.2, ejecutado): no repite tipografía/color/marcas/composición, que ya están resueltos.
>
> **Fecha:** 2026-10-15 · Autor: Mastermind · Estado: **propuesta, pendiente de ✅**

---

## 0. Resumen para David

El sistema está fuerte donde el plan anterior llegó (tokens, pesos, marcas, acento,
escritorio). Quedan dos huecos que ese plan no cubría:

| Hueco | Prueba medida (2026-10-15) |
|---|---|
| Responsive desequilibrado | 56 escalones @640 y 45 @960, pero **1 solo @1200** (p1-layout) y **0 @1440**. 17 de 18 packs sin escalón de escritorio ancho |
| Objetos que no se adaptan a su sitio | **0 container queries en los packs** (solo 10 en tokens.css). Un chart en un sidebar se comporta igual que a página completa |
| API LLM a medias | `components.json` da por familia solo CONTEOS (`objetos: 7`), no las clases, partes ni tokens. Para usarlo bien hay que leer los packs (lo que la doctrina prohíbe pegar en un prompt) |
| Deuda táctil en demos | `audit/MOVIL.md` (25-09): chips/ctas <44px en 10+ páginas. OJO: el override a 36px del shell desde 960px es intencional y documentado; el audit probablemente caducó — RE-EMITIR antes de tocar nada |

## 1. Fases

### A · Motor responsive multifunción (v9.0)
1. **Escalones anchos generalizados**: `@1200`/`@1440` en los packs que los necesiten
   (p1-layout, p13-charts, p15-apps, p8-data). Escala de contenedores `--nz-ancho-*`.
2. **Container queries en objetos compuestos**: charts, tablas apilables, kanban, chat,
   bento, taskplan. Regla nueva de léxico: el objeto reacciona a su contenedor
   (`container-type` en wrapper del objeto). Mobile-first se mantiene: la base SIEMPRE es
   la de móvil; los escalones de contenedor suman, nunca sustituyen.
3. **`--nz-fluid-slope`** (aprendido de mkdir.directory): escala fluida por clamp calculada
   del viewport, en tokens. La letra apenas crece; el lienzo sí (ya doctrina v8.4).
4. **Deuda táctil**: re-emitir `auditar-movil.py` (en PC de David: la VM no puede lanzar
   Chromium, faltan librerías sin sudo). Lo que salga real se arregla; lo que sea falso
   positivo del audit viejo se corrige en el audit.
5. **Auditor nuevo `auditar-contenedores.py`**: mide objetos dentro de contenedores de
   320/480/768px y a viewport 320/390/768/1200/1920. Si no se mide, se rompe en silencio.

### B · API de consulta LLM de primera (v9.1)
1. **`components.json` enriquecido** (lo genera `generar-llm-docs.py`, a mano no se escribe):
   por familia → clases completas, partes `__`, modificadores válidos, tokens que consume
   y markup mínimo de ejemplo. Un agente deja de necesitar los packs PARA SIEMPRE.
2. **Alias ampliados** (de 32 al vocabulario natural de un LLM): stepper, toast, breadcrumb,
   empty-state, skeleton, pagination, drawer, popover, timeline, tree… con alias ES↔EN.
3. **Anti-patrones por familia** ("cuándo NO usarlo"): hoy viven esparcidos en la skill;
   pasan a la API. Ej.: `nz-chart-bar` no para magnitudes dispares → `nz-chart-tablebar`.
4. **`llms.txt`** en la raíz (estándar que los crawlers de LLMs ya respetan) apuntando a
   LLM.md + components.json + examples.
5. **`combos/` ampliado** con el markup esqueleto de cada combo (hoy solo lista packs).

### C · Cierre y prueba viva (v9.2)
1. Cadena CI completa en verde + tag v9.x + skill local sincronizada (contrato de sincronía §2).
2. Página demo `stress-test.html`: el MISMO dashboard renderizado en 4 anchos de contenedor
   (sidebar 320 / drawer 480 / columna 768 / página completa) — la prueba visual del título
   "multifunción".
3. Verificación en navegador real en el PC de David (la VM no puede).

## 2. Riesgos y no-objetivos

- **Container queries no son refresco gratis**: cada objeto que las recibe se mide; el
  auditor nuevo manda. Nada se declara listo sin medición.
- **No se toca** lo resuelto en v8 (tokens, pesos, marcas, acento, composición).
- **No se rompen consumidores**: v9 es aditivo (escalones y API nuevos); nada de renombres.
- La verificación navegador-real necesita el PC (RTX 3060 no hace falta; sí un Chromium sano).

## 3. Estimación

| Fase | Esfuerzo | Nota |
|---|---|---|
| A | 2-3 sesiones | La gruesa: tocar 4-6 packs + auditor nuevo |
| B | 1 sesión | Casi todo es ampliar el generador que ya existe |
| C | 0,5 sesión | Verde + tag + stress-test |

## 4. Referencias aprendidas (2026-10-15)

- mkdir.directory: fluid slope, mono tabular para datos, un momento de espectáculo en un
  sitio silencioso (→ nota `notes/2026-10-15-anatomia-mkdir-directory-aurora.md` en MasterMind).
- Codrops Hub / Relighting: el aderezo progresivo exige base estática perfecta — doctrina
  que Aurora ya cumple y debe defender en los objetos nuevos (→ nota `-fuentes-creativas-…`).

---

Hecho con ❤️ por David Antizar
