# PLAN-AURORA-v10 — «calma, bloques, idiomas y modelos»

> Aprobado por David el 2026-10-22. Aurora v10: el sistema que un modelo quiere usar.
> Cuatro frentes, en orden. Cada cambio se entrega con recibo (lint + medición + URL).

## Diagnóstico medido (no de vista)

Arnés de elegancia sobre las páginas vivas (2026-10-22, viewport 1280):

| Página | Elementos visibles | Superficies (caja) | Anidadas | Con sombra | Combos de padding |
|---|---|---|---|---|---|
| Portada actual | 492 | **104 (21 %)** | **17** | **67** | 10 |
| receta dashboard | 236 | 37 | 4 | 18 | 8 |
| receta admin | 153 | 33 | 4 | 12 | 8 |

Conclusión: **el ruido vive en la portada y en su shell a mano** (232 usos de `cat-*`,
45 líneas de CSS propio, 42 estilos inline), no en los packs. Las recetas van razonables.
La portada es la única página del repo que no come su propia cocina: se pintó a mano
cuando ya existía OpenUI. «Cajas grandes que se pisan» = superficie dentro de superficie
dentro de superficie, todas con sombra, sin presupuesto de elevación.

Prueba del arreglo: parche «calma» inyectado (un solo cambio: sombras → presupuesto)
bajó la portada de **67 elementos con sombra a 15** sin tocar nada más. El ruido es
presupuesto, no gusto.

## Frente 1 · Reglas de calma (v10.0)

Lo que hoy es consejo de prompt pasa a ser **construcción del sistema**:

1. **Presupuesto de sombra**: máximo 1 elemento elevado por región visible. Las cajas
   base pasan a `plano + filete` (borde capilar); la elevación es opt-in (`--raised`).
   Cambio en packs + regla nueva en `auditar-uso.py` (`sombra-budget`).
2. **Tope de anidación**: superficie dentro de superficie dentro de superficie = error
   de lint (`anidacion-max=2`), no nota del PROMPT. El runtime OpenUI ya no anida
   superficies dentro de `Tarjeta`; el shell de portada tampoco podrá.
3. **Densidad por defecto**: el modo `compacta` (padding 12/16, el más usado hoy) pasa a
   default en paneles y figuras; `amplia` solo en documento/prosa. Una fila de tokens:
   `--nz-densidad` con 3 pasos; nada de paddings sueltos (hoy: 10 combos).
4. **Rejilla que encaja**: `Rejilla` emite `auto-fit + minmax(16rem, 1fr)` en vez de
   columnas fijas; las piezas encajan al ancho real y dejan de pisarse en anchos medios.
5. **Ritmo vertical único**: separación entre bloques sale de un solo token
   (`--nz-ritmo`), no de márgenes a mano. Esto mata el «no encajan las piezas».

Recibo de cada regla: antes/después medido con el arnés de este plan (superficies,
anidadas, sombras, combos de padding) + `auditar-uso.py` en verde.

## Frente 2 · La portada se genera con Aurora (v10.1)

- Portada = **programa `.openui` compilado** (`programa-a-html.py`), cero `cat-*` propios,
  cero estilos inline. Proof de concepto ya compilada: 55 líneas → lint 0 fallos, render
  medido sin desbordes (commit de la demo en este repo, carpeta `briefs/`).
- Narrativa de historia, no de inventario: héroe «El diseño lo escribe un modelo. Aurora
  impide que quede mal» → demo interactiva → el mismo encargo con y sin sistema → marca
  tuya → mapa → cómo empezar. Las cifras de inventario (2.194 objetos…) bajan a una franja.
- El **editor del playground es el primer CTA**: entrar, escribir 4 líneas, ver un panel.
- Sección marca como prueba de «no es mi azul»: 3 presets no azules pintados en vivo.
- Pre-render en CI para el marketing (SEO, `cero JS obligatorio` intacto); el editor sigue
  en cliente.
- Nuevas primitivas que el vocabulario necesita para una web sobre sí misma:
  `Codigo`, `Marco`, `Demo`, `Mapa`, `Pie` (36 → 41). Cada una con spec, demo y migrador.

## Frente 3 · Bloques que cualquiera instala (v10.2)

La magia de consumo de ObsidianUI, en clave Aurora (sin React, sin build):

1. **Registro `/r/<bloque>.json`**: cada bloque completo (dashboard-shell, tabla viva,
   panel operativo, chat de agente, landing, login) expone su HTML íntegro + los `<link>`
   pineados. Copiar y pegar real, como ellos.
2. **`npx aurora add panel-operativo --marca carmesi`**: paquete mínimo (sin dependencias)
   que escribe el fichero con marca y canal resueltos. Lo que en ObsidianUI es
   `shadcn add URL`; aquí es dos líneas y un CDN, porque Aurora no necesita node_modules.
3. **Licencia MIT** (aplicada en este plan): legalmente usable por cualquiera; la
   atribución «Hecho con ❤️ por David Antizar» sigue siendo contrato de composición,
   no restricción de licencia.
4. **Bastidor de mapa de primera clase** (`p19-mapa` + `Mapa` en vocabulario): marco,
   leyenda, controles y ficha dentro del censo; motor de tiles libre (MapLibre/Leaflet).
   Diferencial que ninguna librería de componentes tiene.

## Frente 4 · Idiomas y agentes (v10.3)

- **ES canónico, EN espejo** de las páginas de narrativa (portada, openui, contrato,
  README) con el patrón `data-i18n` ya probado en PeleAurora (skill
  `traduccion-bilingue-web`). El catálogo de 655 demos NO se traduce entero: se traduce
  el chrome (nav, filtros, etiquetas) y cada demo gana un párrafo EN en su ficha.
- `llms.txt` pasa a inglés (convención de agentes) con espejo ES; `PROMPT.md` añade
  alias EN del vocabulario (`Page`, `Section`, `Kpi`…) resueltos por el parser — el
  programa puede escribirse en el idioma del modelo, el censo sigue siendo único.
- **SKILL.md = imán**: portada del skill en 40 líneas (enlazar CDN → pegar bloque →
  validar), enlace a `LLM.md`/`components.json`/`openui/aurora.spec.json`. Un agente
  nuevo debe poder usar Aurora en menos de 30 segundos y 12 KB de contexto.
- Todo lo generado por modelo para i18n se valida antes de pegar (claves JSON exactas,
  sin comas sueltas) y se batchea con `delegate_task`.

## Limpieza del repo (transversal, con cada frente)

- `data/` (canales) y `datos/` (base de diseño) fusionados en `datos/` — dos carpetas con
  nombre casi idéntico es ruido puro.
- `combos/` + `examples/` + `recetas/` → un solo concepto: **`bloques/`** con índice
  generado (cada bloque: HTML completo + su programa `.openui` + su ficha en el registro).
- Raíz: queda `index.html` compilado + `tokens.css` + packs + `openui/` + `datos/` +
  `bloques/` + `scripts/` + docs. La maquinaria (specs, generadores) sigue en `scripts/`.
- Se mantiene la regla de oro: nada se borra sin sustituto funcionando; el migrador y
  `canal.py` cubren los enlaces viejos con redirecciones durante un major.

## Orden de ejecución

| Versión | Entrega | Recibo |
|---|---|---|
| 10.0 | Reglas de calma en packs + lint | arnés antes/después en 3 recetas + portada |
| 10.1 | Portada generada + primitivas Codigo/Demo/Marco/Pie | programa compilado, lint 0, SEO prerender |
| 10.2 | Registro `/r/` + `npx aurora add` + bastidor de mapa | 1 bloque instalado desde cero en proyecto limpio |
| 10.3 | i18n ES/EN + PROMPT con alias EN + SKILL imán | 0 claves sin traducir; agente de prueba monta un panel en EN |
| 10.4 | Limpieza de carpetas + CONTRIBUIR.md | CI verde con rutas nuevas |

```

Additional information:
Do NOT use the write_file tool to rewrite the whole file. Use a targeted patch/edit tool (e.g. edit_file, sed -i) to make partial edits — see cache/EDIT_TOOL_POLICY.md.