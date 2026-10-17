# Plan Aurora — Coherencia y modernidad del sistema de diseño

> **Objetivo:** que Aurora deje de producir webs que "no pegan" (tamaños raros, colores
> sueltos, emojis a mansalva) y pase a ser un sistema **coherente, con opinión y moderno**,
> que se vea bien por defecto — no por suerte del agente que lo usa.
>
> **Alcance:** `Ntizar/Aurora` (v7.2.2, el vigente) y sus consumidores (NtizarKey, kit72h,
> farosspain, espanatlas…). `Ntizar-Aurora` (v6, glass/mesh) queda **jubilado**, no se toca.
>
> **Fecha:** 2026-10-04 · Autor: Mastermind · Estado: **propuesta, pendiente de ✅**

---

## 0. Resumen para David (solo esto y ya)

El sistema **no está roto: está desbalanceado y sin contrato de composición**.

Lo que se ve feo en las webs generadas casi nunca es el CSS de los 15 packs. Es lo que el
agente compone encima. La prueba:

| Hecho medido | Dato |
|---|---|
| Emojis en las **576 demos** del sistema | **0** |
| Emojis en NtizarKey (generado con `@v7.2.2`) | **97**, en 6 ficheros |
| Regla de "presupuesto de acento" (máx 5 colores) en v7 | **no existe** (se perdió respecto a v6) |
| Escala tipográfica: pasos duplicados | **`--nz-text-2xs` == `--nz-text-xs` == 12px** |
| Uso real de tamaños micro (12/12/13px) | **464 usos** frente a 70 de tamaño normal |
| Familias de objeto sin ninguna variante | **116 de 349** |
| Árbol de git | **sucio**: 8 packs modificados sin commitear + ~15 scripts sueltos |

Traducción: el agente genera a 12px, con 4 colores saturados a la vez, en columna estrecha y
con un emoji por título — **y nada en el repo se lo prohíbe**. Arreglar los packs sin arreglar
eso no cambia nada de lo que ves.

**La jugada:** 8 fases. El **70% del impacto visible llega en los 3 primeros días** (limpieza →
tokens → contrato de composición). El repaso fino de los 349 objetos viene después y en lotes.

---

## 1. Diagnóstico (medido, no opinado)

Todo sale de scripts sobre el repo, no de mirar capturas.

### 1.1 La capa de generación — el culpable nº1
- `specs/*.json` (demos): **0 emojis**. `examples/`: 1-2 (solo el ❤️ del pie). El sistema es sobrio.
- `app/*.js` de NtizarKey: **97 emojis** (🔑⚙️🔒👁️✏️🗑️👥⚡✅📊…). El agente los mete por costumbre.
- `AGENTS.md` y `LLM.md` de v7 documentan **objetos** («qué clase uso»), no **composición**
  («cómo se monta una página»). No hay una sola regla sobre jerarquía, densidad, anchos ni color.
- La regla v6 «máx 5 momentos de color saturado por página» **desapareció** en v7 → hoy conviven
  azul (títulos) + naranja (avatar) + verde (checks) + rojo (badge) en la misma pantalla.

### 1.2 Escala tipográfica rota
- **Duplicado exacto:** `--nz-text-2xs: 0.75rem` y `--nz-text-xs: 0.75rem` → **el mismo valor**.
  Peor: en escritorio `2xs` baja a 11px y `xs` se queda en 12 → el orden se invierte.
- **Dos "bases":** `--nz-text-base` (15px) y `--nz-text-md` (16px); el `<body>` usa `md`. Ambiguo.
- **Solapes en las `clamp`:** `xl` termina en 24px justo donde empieza `2xl`; `2xl` termina en 30px
  justo donde empieza `3xl`. Una escala que se solapa no es una escala.
- **Efecto real:** `sm`(164) + `2xs`(154) + `xs`(146) = **464 usos micro** vs `md`(38) + `lg`(32).
  La interfaz entera vive a 12-13px; las jerarquías se distinguen por 1px. De ahí «tamaños rarísimos».

### 1.3 Color sin jerarquía
- Paleta = **Tailwind por defecto** (blue-600 `#2563eb`, orange-500 `#f97316`, grises Tailwind +
  un `gray-950 #030712` huérfano). No hay rol, hay *colores sueltos*.
- **5 tokens de fondo** (`bg`, `bg-soft`, `bg-inset`, `surface`, `surface-2`) que valen casi lo
  mismo: no hay escala de elevación de superficies que se lea.
- **Dark mode = otro sistema**: solo 43 de 145 tokens sobrescritos, y con `rgba()` inventados
  fuera de la escala. No es "el mismo sistema en oscuro".

### 1.4 Geometría y densidad
- **`height: 44px` hardcodeado 121 veces** (y `width/min-width: 44px` 50 veces más): el objetivo
  táctil no es un token, es copia-pega.
- Alturas de control sueltas: 22 / 28 / 32 / 36 / 40 / 52 / 56 / 64 px sin escala.
- Radios `4 / 6 / 10 / 14 / 20` con saltos irregulares (+2, +4, +4, +6).
- Escala de espacio (4px) correcta, pero **no hay ritmo vertical** (cuánto separa una sección de
  otra) ni modos de densidad → cada página inventa su aire.

### 1.5 Objetos: mucho pero desigual
- **1.900 objetos / 349 familias / 576 demos / 15 packs**. Para un sistema personal es un
  *catálogo acumulativo*, no un sistema. La coherencia muere en el volumen.
- **116 familias sin ninguna variante** (mapa exacto de "dónde faltan opciones").
- Familias que solapan concepto: `lbl` / `badge` / `chip` / `eyebrow` / `caps` / `kbd` — cuatro
  formas de decir «etiqueta». Igual con `h` / `display` / `--nz-text-*`.
- **No hay iconografía**: ni `.nz-icon` ni sprite. El hueco lo llena el emoji del agente.

---

## 2. Norte: qué significa aquí «coherente y moderno»

Diez principios operativos (cada uno se convierte en regla verificable en la F5):

| # | Principio | Regla medible |
|---|---|---|
| P1 | **Menos y mejor** | Un sistema de ~1.200 objetos defendidos, no 1.900 acumulados |
| P2 | **Una escala es una escala** | Tipografía monótona estricta, sin duplicados ni solapes |
| P3 | **Escala modular** | 6-7 pasos con ratio 1.2-1.25; base 16px |
| P4 | **El color tiene dueño** | ≤5 momentos saturados por página; un protagonista por sección |
| P5 | **Superficies con profundidad** | 3 niveles de superficie legibles (page / card / inset) |
| P6 | **Ritmo vertical** | Espaciado entre secciones/bloques sale de tokens, no del aire |
| P7 | **Densidad decidida** | Uno de 2-3 modos por página (`compact`/`normal`/`spacious`) |
| P8 | **Cero decoración prestada** | Sin emoji como icono, sin gradiente, sin glass (v6 jubilada) |
| P9 | **Iconografía propia** | `.nz-icon` (SVG inline) reemplaza al emoji; trazo y tamaño unificados |
| P10 | **Composición con opinión** | Plantillas canónicas: cada tipo de página tiene su forma correcta |

---

## 3. Decisiones que necesito de ti (D1-D3)

### D1 — Alcance: ¿v8 mayor o v7.3 evolutivo?
- **Recomendado: v8 mayor (breaking) + script de migración.** La tipografía y el color cambian de
  raíz; fingir compatibilidad es arrastrar la deuda otros dos años.
- Alternativa: v7.3 evolutivo, sin romper nada — más lento y con dos escalas conviviendo.

### D2 — Dirección estética
- **Recomendado: (a)+(c)** → disciplina de estudio (tipografía, aire, densidad, jerarquía) tipo
  Linear/Vercel/Stripe, **conservando azul + naranja como firma** de marca. Sobrio, no frío.
- Alternativas: (b) SaaS "amable" tipo Notion; (d) rehacer la marca entera.

### D3 — Por dónde empezamos
- **Recomendado: F0 → F1 → F2 en una sola tacada.** Limpieza + tokens + contrato = el "cómo
  genera las webs" arreglado antes de tocar objeto alguno.
- Alternativa: F3 (repaso de objetos) primero, si prefieres profundidad antes que impacto visible.

---

## 4. Las 8 fases

Cada fase: **objetivo · entregable · verificación (receipt)**. Sin receipt no se declara Listo.

### F0 · Limpieza y red de seguridad — 0,5 día
- **Objetivo:** partir de un árbol limpio y con línea base reproducible.
- **Entregable:** los 8 packs modificados cerrados (commit o descarte revisado); scripts de
  exploración (`biseca-*`, `caza-*`, `inspeccion-*`, `sonda-*`) movidos a `scripts/trasfondo/`;
  `audit/base-7.2.2.json` como foto de partida.
- **Verificación:** `git status` limpio + `python scripts/validar-css.py` → `RESULTADO: VÁLIDO`.

### F1 · Tokens v8: la base — 1-2 días
- **Objetivo:** una base sana. Aquí vive el 50% del "look".
- **Entregable:**
  - **Tipografía:** escala modular de 6-7 pasos sin duplicados ni solapes (≈ 13 / 14 / 16 / 18-20 /
    24 / 30 / 38 / 48); base 16px; `2xs/xs` redefinidos o retirados; mínimo 13px en móvil.
  - **Color:** paleta con **roles** (brand/accent/neutral), 3 niveles de superficie legibles y
    presupuesto de acento; dark mode al 100% de tokens semánticos, sin `rgba()` inventados.
  - **Geometría:** token `--nz-tactil: 44px` (hoy hardcode ×121); escala de radios `4/8/12/16/24`;
    alturas de control tokenizadas (`--nz-control-sm/md/lg`).
  - **Espacio:** escala 4px + ritmo vertical (`--nz-rh-seccion`, `--nz-rh-bloque`) + densidad.
  - Tabla de equivalencias v7→v8.
- **Verificación:** script que comprueba monotonía de la escala, 0 valores duplicados y 100% de
  cobertura dark.

### F1b · Motor de temas: 2-3 colores al principio y todo cambia ⭐⭐ — 1-2 días
- **Objetivo (petición de David):** que al arrancar un proyecto se elijan **2 colores** (marca +
  acento) y el sistema entero se rehaga para ese proyecto: marca, acentos, foco, sombras de color,
  dark mode. Una base modificable de verdad, no un puñado de sitios que hay que tocar a mano.
- **Cómo (3 piezas):**
  1. **Presets de marca** (`marcas/<nombre>.css`): cada uno redefine solo las rampas
     `--nz-marca-50…900` y `--nz-acento-50…700`. Se activa con `data-nz-marca="indigo"` en el
     `<html>` (junto a `data-nz-theme="light|dark"`). **No resucita `data-nz-skin` de v6**: son
     rampas de color, no glass/mesh.
  2. **Generador de paletas** (`scripts/generar-marca.py`): das dos hex y genera la rampa completa
     en **OKLCH** (pasos de luminosidad uniformes, croma mapeado a gamut sRGB) + validación de
     **contraste AA** de cada paso. Cualquier marca entra en el sistema en un comando.
  3. **Derivación automática:** en dark, `soft`/`tint` se calculan con `color-mix()` sobre la rampa
     → un preset nuevo funciona en claro y oscuro sin tocar nada más.
- **Presets iniciales:** `aurora` (azul+naranja, por defecto), `indigo` (índigo+cian),
  `esmeralda` (verde+ámbar), `violeta` (violeta+rosa), `carmesí` (rojo+cian).
- **Entregable:** `tokens.css` v8 con las rampas por rol + `marcas/*.css` + `scripts/generar-marca.py`
  + `marcas/index.html` (selector visual) + documentación en `LLM.md`.
- **Verificación:** cada preset pasa la auditoría de contraste AA; captura de la misma página con
  los 5 presets; `data-nz-marca` inexistente cae siempre en `aurora` (sin romper).

### F2 · Contrato de composición — 1 día ⭐ (el que arregla «cómo genera las webs»)
- **Objetivo:** que el agente (y tú) sepa **cómo se compone**, no solo qué clases hay.
- **Entregable:** `COMPOSICION.md` nuevo + `AGENTS.md` v8 + `LLM.md` v8, con reglas duras:
  0 emoji en UI (whitelist: ❤️ solo en el pie), ≤5 acentos, un protagonista por sección, ancho de
  composición por tipo de página, mínimo tipográfico, ritmo vertical, densidad, icono≠emoji.
- **Verificación:** checklist de 10 reglas + un «antes/después» de una página real (NtizarKey).

### F3 · Repaso objeto a objeto — 3-5 días, en lotes
- **Objetivo:** revisar **las 349 familias** con método (ver §5), no a ojo.
- **Prioridad:** (a) las 116 sin variantes, (b) las ~30 más usadas, (c) las que solapan concepto
  (`lbl`/`badge`/`chip`/`eyebrow`; `h`/`display`).
- **Entregable:** `audit/familias.csv` (veredicto por familia) + packs v8 + objeto nuevo `.nz-icon`.
- **Verificación:** `validar-css.py` en 0 fantasmas / 0 sin demo / 0 duplicados; catálogo regenerado.

### F4 · Recetas canónicas — 2-3 días ⭐
- **Objetivo:** que "así se ve bien" exista como archivo copiable, no como idea.
- **Entregable:** `recetas/` con login, dashboard, **admin** (caso NtizarKey), settings,
  tabla-detalle, landing, informe y formulario denso. Cada una: 0 emojis, presupuesto de color,
  anchos correctos, densidad decidida.
- **Verificación:** cada receta pasa el arnés (F5) con 0 fallos + captura visual.

### F5 · Arnés de verificación — 1-2 días
- **Objetivo:** que la coherencia no dependa de la voluntad. Se blinda en CI.
- **Entregable:** reglas nuevas en `auditar-uso.py` + `validar-css.py`: 0 emoji en UI, presupuesto
  de acento, un protagonista por sección, mínimo tipográfico, ancho de contenedor, ritmo vertical,
  densidad, contraste AA, táctil 44px, `scrollWidth == clientWidth`.
- **Verificación:** meter a propósito una violación y comprobar que la CI se pone **roja**.

### F6 · Catálogo y docs — 1 día
- **Objetivo:** que el catálogo enseñe criterio, no solo objetos.
- **Entregable:** `paginas/anatomia.html` + `paginas/do-dont.html`; cifras **generadas**, nunca escritas.
- **Verificación:** portada, cabecera y README con el mismo número (hoy dan tres distintos).

### F7 · Migración y adopción — 1-2 días + por proyecto
- **Objetivo:** que los consumidores hereden el sistema bueno.
- **Entregable:** `scripts/migrar-v7-v8.py` + migración de **NtizarKey** (los 97 emojis fuera) como
  prueba reina, y luego kit72h / farosspain / espanatlas.
- **Verificación:** URL viva + captura antes/después.

---

## 5. Repaso objeto a objeto: el método (349 familias)

Una ficha por familia, 8 comprobaciones, un veredicto. Automatizable en `scripts/auditar-familias.py`.

| # | Comprobación |
|---|---|
| 1 | ¿Tiene demo viva? |
| 2 | ¿Tiene variantes del léxico cerrado? |
| 3 | ¿Solapa concepto con otra familia? |
| 4 | ¿Usa solo tokens (0 valores crudos)? |
| 5 | ¿Aporta a la composición o es adorno? |
| 6 | ¿Aparece en alguna receta canónica? |
| 7 | ¿Nombra bien (castellano / alias documentado)? |
| 8 | ¿Es moderno o es deuda de v6? |

**Veredictos:** ✅ mantener · ➕ ampliar variantes · ✏️ renombrar · 🔀 fusionar · 🗑️ retirar ·
🆕 añadir (siempre con demo).

Salida: `audit/familias.csv` + informe navegable. **Regla de oro:** cada clase retirada se
comprueba antes con `search_files` sobre todos los packs y consumidores.

---

## 6. Arnés: las reglas que hoy NO existen (y que lo arreglan)

1. **0 emoji como icono de UI** (whitelist: `❤️` en el pie).
2. **≤5 momentos de color saturado por página.**
3. **Un protagonista cromático por sección** (azul y naranja nunca de igual a igual).
4. **Ningún texto de UI por debajo de 13px en móvil.**
5. **Ancho de composición por tipo de página** (app/dashboard ≥ 72rem en escritorio; columna
   estrecha solo para prosa/reporte).
6. **Ritmo vertical** entre secciones desde tokens.
7. **Una densidad por página.**
8. **Contraste AA**, **táctil 44px**, **`scrollWidth == clientWidth`** (ya existen; se mantienen).

---

## 6b. Motor de temas: el contrato de marca (resumen operativo)

```html
<html lang="es" data-nz-theme="light" data-nz-marca="indigo">
```

| Token | Qué cambia | Quién lo toca |
|---|---|---|
| `--nz-marca-50…900` | Rampa de la marca (primario) | preset |
| `--nz-acento-50…700` | Rampa del acento | preset |
| `--nz-brand`, `--nz-accent`, `--nz-*-soft/tint`, `--nz-focus-ring`, `--nz-shadow-brand/accent` | **Derivados** de las rampas | nadie: se derivan solos |

**Regla:** un proyecto **no redefine colores a mano**; elige un preset o genera el suyo con
`scripts/generar-marca.py`. Preset desconocido ⇒ cae en `aurora` (nunca rompe).

## 7. Iconografía (matar el emoji)

Añadir `.nz-icon` (SVG inline, `currentColor`, 3 tamaños, trazo 1.5-2px) con un set base de
~40-60 iconos en `nz-icono-<nombre>`. Es lo que sustituye a los 97 emojis de forma **coherente y
multiplataforma**. Va en el pack 09 (media e iconografía) y entra en el léxico.

---

## 8. Riesgos, no-objetivos e hitos

**Riesgos**
- *Repaso eterno:* 349 familias pueden comerse semanas → lotes + priorizar por uso real.
- *Romper consumidores:* v8 con tabla de equivalencias + script + migrar NtizarKey primero.
- *«Moderno» es subjetivo:* se fija con 2-3 referencias aprobadas antes de tocar tokens (D2).

**No-objetivos (fuera de alcance a propósito)**
- No se recupera glass/gradientes/3D (v6 sigue jubilada).
- No se reescribe a React/TypeScript: el valor de Aurora es CSS puro, sin build.
- No se rediseña la marca (logo/tipografía propia) salvo que lo pidas.

**Hitos**
| Semana | Fases | Resultado visible |
|---|---|---|
| 1 | F0 · F1 · F2 | Las webs nuevas ya salen **sin emojis, con tipos y colores coherentes** |
| 2 | F3 · F4 | Objetos saneados + recetas canónicas (incluida admin) |
| 3 | F5 · F6 · F7 | Coherencia blindada en CI + catálogo con criterio + NtizarKey migrado |

---

Hecho con ❤️ por David Antizar
