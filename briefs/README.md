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
