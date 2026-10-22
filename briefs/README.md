# briefs/

Un brief es el encargo en JSON: qué hay que construir y con qué datos. `generar-web.py` elige
la plantilla del arquetipo, se la pasa al modelo con el prompt del sistema y verifica el
resultado antes de escribir nada.

```bash
python3 scripts/generar-web.py --brief briefs/panel-ferroviaria.json
python3 scripts/generar-web.py --brief briefs/panel-ferroviaria.json --dry-run     # sin red
python3 scripts/generar-web.py --brief briefs/panel-ferroviaria.json --sin-modelo  # solo plantilla
```

Claves que entiende: `encargo` (obligatoria), `arquetipo`, `marca`, `tema`, `titulo`, `datos`
(los hechos que el modelo debe usar) y `salida` (nombre del fichero). Cualquier otra clave de
texto se pasa como variable de la plantilla.

`--prompt breve` (por defecto) omite los tres ejemplos largos de `openui/PROMPT.md`: cuando la
generación parte de una plantilla de arquetipo, el modelo ya tiene delante un programa completo
y las firmas siguen en el prompt. Son ~1.040 tokens menos de entrada por generación.

## La portada: `portada.openui` (una sola fuente)

La portada del sistema no se escribe a mano. Se compila y se hornea:

```bash
# 1) el programa es la fuente (briefs/portada.openui). 2) se hornea: el runtime pinta en
#    Chrome headless y se extrae el <main> ya pintado, sin JS en el resultado.
python3 scripts/hornear.py briefs/portada.openui --salida briefs/portada.tmpl.html --plantilla-base

# 3) build-catalog clava las cifras reales del censo ({{OBJETOS}}, {{FAMILIAS}}, {{PACKS}},
#    {{MARCAS}}) y el programa entero en el <pre> de la sección «Transparencia» → index.html
python3 scripts/build-catalog.py
python3 scripts/auditar-uso.py index.html
```

`--plantilla-base` deja los `{{...}}` sin sustituir; sin esa bandera, `hornear.py` escribe un
HTML cerrado y listo para servir (útil para cualquier programa que no sea la portada).

El horneado necesita Chrome o Edge instalado (o `--navegador RUTA`). Sirve el repo por HTTP
local a propósito: el runtime carga la spec con `fetch`, que en `file://` falla por CORS.

