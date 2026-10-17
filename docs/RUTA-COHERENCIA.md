# Ruta de coherencia — Aurora 10

> **Objetivo:** que Aurora se vea y se comporte igual de bien en móvil y en PC,
> sin excepciones por página: los mismos iconos, el mismo tema, los mismos
> patrones y los mismos detalles de buen gusto en las 18 categorías, las 7
> recetas, los 5 ejemplos y el catálogo.
>
> **Autor:** Mastermind · **Fecha:** 2026-10-17 · **Estado:** Fase 1 cerrada.

---

## 0. Qué significa «coherente» aquí

No es una opinión: son siete comprobaciones que se pueden falsar.

1. **Un icono es SVG `.nz-icon`**, nunca un símbolo de texto (`▦`, `⚙`, `⌕`, `✎`).
   Un símbolo cambia de forma según la fuente del sistema y rompe la paridad.
2. **Una receta no fuerza un tema.** Light por defecto; el dark es un modo.
   Un bloque `--profundo` puede ser oscuro, pero redefine sus tokens de texto.
3. **Una versión.** Todo CDN apunta al tag vigente; nada de `@v8.3.0` en un repo 9.2.
4. **Un footer exacto:** `Hecho con ❤️ por David Antizar`, sin `text-transform`.
5. **Una fuente por tema.** El valor se lee del JSON/`components.json`, no se copia.
6. **Cero desbordes** a 320/360/390/768/1024/1440/1920: `scrollWidth == clientWidth`.
7. **Un patrón, un comportamiento.** La sidebar, la toolbar, la tabla apilable, el
   kanban y el chart se comportan igual en admin, dashboard, ajustes y estrés.

---

## 1. Fase 1 — Coherencia de superficie ✅ (cerrada 2026-10-17)

**Qué se hizo**

- Se creó `scripts/auditar-coherencia.py` y se midió el baseline: **211 incoherencias**.
- Se migraron **60 bloques de demos** de 12 specs a SVG `.nz-icon`; también el shell
  del catálogo (`paginas/*.html`) y `examples/login.html`.
- La receta `charla.html` dejó de estar forzada a dark: ahora es light con un solo
  beat `--profundo`, y ese bloque redefine sus tokens de texto (antes el contraste
  solo funcionaba por casualidad en dark).
- Los 5 `examples/` dejaron de enlazar `@v8.3.0` y usan `@v9.2.0`.
- El footer de la charla volvió a la atribución exacta.
- `auditar-coherencia.py --check` entra en la CI.

**Puerta**

```bash
python3 scripts/auditar-coherencia.py --check   # 0 fallos
python3 scripts/auditar-uso.py base.html stress-test.html
```

**Resultado:** 211 → **0 fallos**. Quedan 14 avisos de estilos inline de geometría
en demos (no rompen; se revisan en la fase 3).

---

## 2. Fase 2 — Full responsive real (siguiente)

La fase 1 arregló la coherencia de superficie; esta mide la página, no el CSS.

**Matriz mínima:** 8 anchos × 12 patrones.

| Anchos | 320 · 360 · 390 · 414 · 768 · 1024 · 1440 · 1920 |
|---|---|

| Patrones | navbar · sidebar · tabs · toolbar · tabla apilable · kanban · chart · chat · modal/drawer · formularios · checkout · escenario |
|---|---|

**Qué se mide**

- `document.scrollingElement.scrollWidth == clientWidth` en cada combinación.
- Objetivos táctiles ≥ 44×44 px.
- Ningún texto de interfaz < 13 px (12 px solo datos).
- Ningún solapamiento de `position: sticky` (el bug de admin: sidebar pegada
  tapando la toolbar).
- Ningún contenido cortado por `overflow: hidden` sin alternativa.
- La misma página en 320 y 1920 conserva jerarquía, no solo «cabe».

**Herramientas**

```bash
python3 scripts/auditar-responsive.py        # estático: container queries y escalones
python3 scripts/auditar-movil.py             # real: abre Chromium (PC)
```

La VM de NaN no puede lanzar Chromium (falta `libatk`): la medición real se hace
en el PC de David. El resultado se pega en `audit/RESPONSIVE.md` y la CI solo
exige la parte estática.

**Puerta**

- Matriz completa sin un solo desborde.
- `audit/RESPONSIVE.md` generado y firmado.
- `stress-test.html` ampliado con un bloque por patrón crítico.

---

## 3. Fase 3 — Detalles de buen gusto

Lo que hace que un sistema parezca diseñado y no generado.

**Checklist por página**

- Una sola densidad (compact / normal / spacious), no tres en la misma vista.
- Máximo 4 tamaños tipográficos y 5 momentos de color saturado.
- Alineación óptica: títulos, cifras y acciones comparten eje; los iconos no
  bailan entre filas.
- Ritmo vertical: secciones con `--nz-rh-seccion`, no con aire inventado.
- Estados completos: vacío, carga, error, hover, focus visible, disabled.
- Microinteracciones ≤ 300 ms y `prefers-reduced-motion` respetado.
- Sin sombras, radios ni bordes ad-hoc: todo token.
- Un detalle por página (un borde, una cifra en acento, una transición), no
  decoración en todas.

**Herramienta nueva:** `auditar-buen-gusto.py` (conteos medibles: tamaños,
acentos, sombras, radios, duración de animaciones) + revisión visual en el PC.

**Puerta:** 0 avisos de presupuesto y una revisión visual página a página.

---

## 4. Fase 4 — Cierre

- CI completa en verde con las puertas nuevas.
- `README.md`, `AGENTS.md`, `COMPOSICION.md`, `LLM.md` y la skill sincronizados.
- Tag **v10.0.0** en el último commit verde y push del tag.
- Verificación del CDN y de Pages.

**No se hace en esta ruta:** renombrar clases, romper la API de `components.json`,
introducir glass como base o duplicar patrones entre packs.

---

## Deuda conocida (honesta)

- **Medición real:** la VM no puede Chromium; la fase 2 se cierra en el PC.
- **Estilos inline:** 14 avisos de geometría/color en demos (`style="height:…"`).
  Se revisan en la fase 3; algunos son datos del gráfico, no diseño.
- **`href="#"` en recetas:** admin tiene enlaces de menú muertos; se convierten
  a páginas reales en la fase 1.5.
- **`examples/`:** no están en el lint de la CI; se añaden en la fase 4.

Hecho con ❤️ por David Antizar
