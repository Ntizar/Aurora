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

## La portada: `portada.tmpl.html` (HTML escrito a mano)

La portada del sistema (`index.html`) se escribe a mano en `briefs/portada.tmpl.html`, con
marcadores (`{{OBJETOS}}`, `{{FAMILIAS}}`, `{{PACKS}}`, `{{MARCAS}}`) que `build-catalog.py`
clava con las cifras reales del censo. La portada nunca inventa un número.

```bash
# build-catalog clava las cifras reales del censo → index.html
python3 scripts/build-catalog.py
python3 scripts/auditar-uso.py index.html
```

El pipeline `briefs/portada.openui` → `hornear.py` se jubiló cuando la portada pasó a HTML
legible: la transparencia del programa dejó paso a la claridad. La capa openui-lang sigue
viva en `openui/` (componentes, runtime y probador) y en `openui/plantillas/`.

Para hornear cualquier otro programa `.openui` a HTML estático (sin JS), `hornear.py` sigue
siendo la herramienta: `--plantilla-base` deja los `{{...}}` sin sustituir; sin esa bandera
escribe un HTML cerrado y listo para servir.
