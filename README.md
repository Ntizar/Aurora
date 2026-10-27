<div align="center">

# Aurora

**El design system de Ntizar.** Un solo CSS para montar cualquier web: catálogo verificado,
marcas por preset y una capa generativa para que el diseño lo escriba el modelo — sin salirse
nunca del sistema.

2.201 objetos · 413 familias · 661 demos en vivo · 18 categorías · 40 componentes generativos · 338 iconos numerados

[![CI](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/validar.yml)
[![Pages](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml/badge.svg)](https://github.com/Ntizar/Aurora/actions/workflows/pages.yml)
![versión](https://img.shields.io/badge/versi%C3%B3n-10.8.0-2563eb)

**[Catálogo](https://ntizar.github.io/Aurora/)** · **[Base de datos](https://ntizar.github.io/Aurora/base.html)** · **[Generative UI](https://ntizar.github.io/Aurora/openui/)** · **[Iconos](https://ntizar.github.io/Aurora/iconos/)** · **[Contrato](CONTRATO.md)**

</div>

---

Aurora no es una colección de snippets. Es un sistema con contrato: un objeto existe si está
demostrado en vivo, cada clase tiene un solo dueño y una CI lo verifica en cada push. Si el
catálogo lo enseña, funciona; si algo se rompe, el push se pone en rojo antes de publicarse.

## Empezar en diez segundos

```html
<html lang="es" data-nz-theme="light" data-nz-marca="aurora">
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/tokens.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/packs/p1-layout.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/packs/p3-typography.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10/packs/p4-actions.css">
</head>
<body class="nz">
  <main class="nz-container">
    <h1 class="nz-h1">Hola, Aurora</h1>
    <p class="nz-lead">Un sistema, todas las webs.</p>
    <button class="nz-btn nz-btn--primary">Empezar</button>
  </main>
</body>
</html>
```

`@v10` es el **canal vivo**: se mueve con cada release 10.x, así que un cambio en Aurora llega
solo a todas las webs que lo usan. Para una entrega congelada, el tag exacto (`@v10.2.0`).
Los consumidores fijados en `@v9` o en un tag exacto de la serie 9 no cambian: `@v9` sigue
resolviendo su major para siempre.
El detalle completo está en **[CONTRATO.md](CONTRATO.md)**.

## Las cuatro capas

```
L0  marcas/      presets de tokens: identidad (datos, no código)
L1  packs/       18 hojas CSS: la implementación
L2  openui/      40 componentes: el vocabulario que usa el modelo
L3  (plantillas) arquetipos: panel, informe, landing, ajustes, agente, presentación
```

El modelo trabaja en **L2** y elige **L0** por nombre. Nunca escribe en L1.

## Tres formas de consumirlo

**Persona** — abre el [catálogo](https://ntizar.github.io/Aurora/): una demo viva por objeto,
con su markup copiable. Si dudas, la [base de datos de diseño](https://ntizar.github.io/Aurora/base.html)
busca por lo que quieres construir («tabla apilable», «dashboard», «acento»).

**Agente** — con una línea lo conectas por **MCP** y consulta el censo vivo, valida y
compila sin bajar medio megabyte:

```bash
claude mcp add aurora -- python scripts/mcp-aurora.py   # Claude Code
# cursor / VS Code: "mcpServers": {"aurora": {"command": "python", "args": ["…/scripts/mcp-aurora.py"]}}
```

Cinco herramientas: `estado_del_sistema` (versión y canales, nunca de memoria),
`buscar_por_necesidad`, `leer_componente`, `validar_html` y `compilar_programa`.
Autochequeo: `python scripts/mcp-aurora.py --test`. Sin MCP a mano, la vía clásica es
`LLM.md` (guía) + `components.json` (API) + `llms-full.txt` (las 411 familias con su
markup) y el juez:

```bash
python3 scripts/auditar-uso.py mi-pagina.html   # clases inventadas, packs, composición
```

**Modelo, en caliente** — `openui/PROMPT.md` + `openui/aurora.spec.json`, y el modelo emite
openui-lang; `openui/aurora-openui.js` lo pinta con clases del censo. Cero clases inventadas
posibles, y ~52 % menos tokens que JSON:

```
root = Pagina([titulo, kpis], "contenido")
titulo = Titular("Operaciones de la flota", "1")
kpis = Rejilla([Kpi("Puntualidad", "94,2 %", "+2,1 pp", "sube", "acento")], "4")
```

Pruébalo en **[la demo](https://ntizar.github.io/Aurora/openui/)** y mira el HTML que sale.
Si el encargo encaja con un arquetipo, parte de su **[plantilla](openui/plantillas/)**:
panel, informe, landing, ajustes o agente.

```bash
# de un encargo a una página, con el modelo y con el lint delante
python3 scripts/generar-web.py --brief briefs/panel-ferroviaria.json
# → dist/ferroviaria-panel.openui + .html, validado y auditado (0 fallos o no se entrega)

# o sin modelo, partiendo de la plantilla
python3 scripts/plantilla.py panel-operativo --var titulo="Octubre" -o p.openui
python3 scripts/programa-a-html.py p.openui -o dist/panel.html --marca ntizar

# publicar una versión (canal vivo)
python3 scripts/canal.py --check && python3 scripts/canal.py --purgar
```

## Pantallas completas, no solo piezas

Nadie quiere una web de piezas sueltas: el sistema entrega la página COMPLETA en tres
capas, ya auditada y con su estructura revisada.

| Nivel | Qué hay | Dónde |
|---|---|---|
| Plantilla por arquetipo | panel, informe, landing, ajustes, agente y presentación — variables y estructura fija | `openui/plantillas/` |
| Esqueleto por tipo | 9 combos: landing, dashboard, chat-ia, login-form, e-commerce, escritorio-app, charla-beats, prototipo, presentación | `bloques/combos/` |
| Producto de muestra | landing + ficha bajo subruta, modo producto, medidas en navegador (18 comprobaciones) | `examples/golden/` |

Encaja tu dato en la plantilla del arquetipo: la jerarquía, el responsive, los estados y
el presupuesto de color ya vienen resueltos — el modelo pone contenido, no arquitectura.

## Qué hay dentro

| Pieza | Qué es |
|---|---|
| `tokens.css` | 234 tokens (más 61 en oscuro) con gemela OKLch y contraste auditado |
| `packs/p1…p18.css` | Los 18 packs, uno por categoría (recuento vivo en `components.json` y `audit/AUDITORIA.md`; una sola fuente) |
| `marcas/` | 6 presets (aurora, indigo, esmeralda, violeta, carmesí, ntizar) + generador OKLCH |
| `specs/NN.json` | **Fuente de verdad** de las demos: el catálogo se genera de aquí |
| `base.html` + `datos/base-diseno.json` | Base de datos consultable: familias, tokens, recetas, combos, marcas y leyes |
| `bloques/recetas/` · `bloques/ejemplos/` · `bloques/combos/` | Recetas canónicas, páginas completas y esqueletos por tipo, listos para copiar |
| `examples/golden/` | Producto de muestra (landing + ficha) generado desde `.openui` con `hornear-golden.py` |
| `llms.txt` · `llms-full.txt` | Guía corta y referencia completa por componente para agentes |
| `scripts/mcp-aurora.py` | Servidor MCP (5 herramientas, stdlib pura): censo vivo, lint y compilador para Claude/Cursor |
| `openui/` | Capa generativa: componentes, prompt, spec, runtime vanilla, **plantillas por arquetipo** y probador |
| `AGENTS.md` · `COMPOSICION.md` · `LLM.md` | Reglas duras, contrato de composición y guía de decisión |

Una marca son dos colores y sus rampas: `<html data-nz-marca="ntizar">` y todo el sistema
cambia de identidad sin tocar una clase.

## Garantías (lo que la CI no deja pasar)

```bash
python3 scripts/validar-css.py           # manifiesto, cobertura, literales, versión y tag
python3 scripts/audit-catalog.py         # campo a campo contra las specs
python3 scripts/audit-a11y.py            # etiquetas, teclado y foco
python3 scripts/audit-tema.py            # todo sobrevive al modo oscuro
python3 scripts/auditar-base.py --check  # la base de datos no se edita a mano
python3 scripts/auditar-responsive.py    # container queries y escalones no se debilitan
python3 scripts/auditar-contraste.py     # pares WCAG por tema y marca + paridad oklch
python3 scripts/auditar-openui.py        # censo, deriva, runtime, enums y ejemplos
python3 scripts/canal.py --check         # canales y versiones en orden
python3 scripts/auditar-uso.py --selftest
```

Cero gradientes, cero `backdrop-filter`, cero `!important`, cero colores a mano: todo valor
es un token. El pie de toda página: **Hecho con ❤️ por David Antizar**.

## Estructura

```
Aurora/
├── tokens.css · packs/ · fuentes/     # el sistema: tokens y 18 packs (Inter self-hosted)
├── marcas/                            # presets de color con generador OKLCH
├── specs/ → paginas/ · index.html     # las demos son la fuente; el catálogo se genera
├── base.html · datos/                 # base de datos de diseño (vista + JSON)
├── bloques/recetas/ · bloques/ejemplos/ · bloques/combos/     # páginas completas y esqueletos por tipo
├── openui/                            # capa generativa: componentes, prompt, spec, runtime
├── scripts/                           # generadores y auditores (lo que corre la CI)
├── docs/                              # RUTA-COHERENCIA y planes archivados
├── LLM.md · COMPOSICION.md · CONTRATO.md · AGENTS.md · SKILL.md
└── CHANGELOG.md · llms.txt · components.json
```

## Trabajar en el sistema

1. Declara las clases en el pack que les toque (una familia, un pack).
2. Añade la demo en `specs/NN.json` (una línea, contenido real, sin JS).
3. Regenera y valida con la cadena de arriba: si `validar-css.py` no dice **VÁLIDO**, no está.
4. Si a un proyecto le falta un patrón, **se sube al repo**: el siguiente lo hereda.
5. Si cambias algo que otros usan, mira **[CONTRATO.md](CONTRATO.md)** antes de mover el tag.

## Atribución

Hecho con ❤️ por David Antizar
