# Contrato de versiones y canales

> Cómo se propaga un cambio de Aurora a todas las webs, qué se rompe y qué no.
> Este documento manda sobre cualquier costumbre: si algo aquí no se cumple, es un fallo.

## 1. La idea en una frase

Un cambio de **piel** (tokens, CSS) llega a todas las webs sin tocarlas. Un cambio de
**esqueleto** (componentes, props, programas) se propaga re-emitiendo el programa, y solo
si el cambio es compatible o hay migración.

## 2. Dos canales, un sistema

| Canal | Referencia CDN | Quién lo usa | Qué implica |
|---|---|---|---|
| **vivo** | `@v9` (rango de major) | webs y paneles propios, catálogo, demos | se mueve con cada release 9.x: un cambio llega solo |
| **congelado** | `@v9.6.0` (tag exacto) | entregas a cliente, auditorías, informes congelados | no cambia hasta que se sube a propósito |

```html
<!-- web propia: sigue el canal vivo -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9/tokens.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9/packs/p1-layout.css">

<!-- entrega a cliente: congelada -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v9.6.0/tokens.css">
```

El rango cubre **solo el major**: `@v9` nunca saltará a una v10 que rompa contrato.

Resolución y comprobación, sin adivinar:

```bash
python3 scripts/canal.py            # vivo → tag resuelto · congelado
python3 scripts/canal.py --tag      # el tag exacto, para scripts
python3 scripts/canal.py --check    # puerta de CI (offline); --online añade el CDN
```

## 3. Un tag publicado es inmutable

Nunca se reescribe, nunca se mueve, nunca se borra. Si algo estaba mal, se publica otra
versión. Lo que se mueve es **a dónde apunta el rango**, no el tag.

## 4. Qué propaga solo y qué no

| Cambio | ¿Llega solo por el canal vivo? |
|---|---|
| Token (color, espacio, tipografía, radio, sombra) | **Sí.** Todas las webs a la vez. |
| Estilo de un objeto existente (misma clase, misma API) | **Sí.** |
| Nuevo componente o nueva demo (aditivo) | **Sí**, y no rompe nada: nadie lo estaba usando. |
| Renombrar o quitar una clase, un componente o una prop | **No.** Rompe en silencio → exige **major** + migración. |
| Estructura de la página (otra jerarquía) | **No.** Hay que re-emitir el programa con un modelo. |
| Contenido y datos | **No.** Nunca. |

## 5. Semántica de versiones

- **patch** (`9.5.0 → 9.5.1`): corrección sin cambio de API. Se puede subir en caliente.
- **minor** (`9.5.0 → 9.6.0`): aditivo. El canal vivo lo recibe solo.
- **major** (`9.x → 10.0.0`): renombrar o quitar algo del contrato. Exige:
  1. fichero de migración en `openui/migraciones/`,
  2. `python3 scripts/migrar-programas.py` sobre los programas,
  3. un major nuevo en `data/canales.json` (el canal vivo cambia de rango),
  4. nota en `CHANGELOG.md` con «qué deja de existir».

## 6. El lock de cada web

Cada producto guarda `aurora.lock` en su raíz:

```json
{
  "canal": "vivo",
  "rango": "v9",
  "resuelto": "v9.6.0",
  "spec": "1.0.0",
  "generado": "2026-10-21"
}
```

- `python3 scripts/canal.py --lock aurora.lock` lo escribe con el tag resuelto hoy.
- `python3 scripts/canal.py --verificar aurora.lock` comprueba que sigue siendo coherente
  (canal, major y versión de spec). Es la puerta que se pone en la CI de cada web.
- El lock **no** congela la web: documenta qué está comiendo y permite auditar el salto.

## 7. Rollback sin tocar 30 repos

Si una release sale mal con el canal vivo:

1. Cambia el rango del lock a tag exacto (`"canal": "congelado", "resuelto": "v9.6.0"`), o
2. publica un patch (`9.5.1`) con la corrección — preferible, porque el rango sigue vivo.

Un cambio malo en el canal vivo llega a todas las webs **a la vez**: por eso el orden es
CI verde → canario (una web) → 48 h → resto. Nunca al revés.

## 8. Del programa a la página

```bash
# el modelo escribe el programa; esto lo convierte en página
python3 scripts/programa-a-html.py pagina.openui --salida dist/pagina.html \
        --marca ntizar --tema light --canal vivo

# y esto verifica que no se ha salido del censo
python3 scripts/auditar-uso.py dist/pagina.html
```

`programa-a-html.py` resuelve los packs que el programa necesita, aplica el canal y deja
la página lista. No inventa clases: el programa solo puede usar componentes de la
biblioteca, y el runtime emite markup del censo.

## 9. Regenerar muchas webs a la vez

```
briefs/*.json ──modelo──► pagina.openui ──programa-a-html──► pagina.html ──auditar-uso──► PR
```

El modelo no reescribe CSS: re-emite entre 8 y 40 líneas por página. Por eso 30 webs son
30 llamadas cortas y el resultado es coherente por construcción. Lo que se versiona en el
repo de cada web es el **programa** y el **lock**, no el HTML a mano.

## 10. Lo que este contrato impide

- Pinear `@master` en producción (jsDelivr cachea por edge: te sirve CSS viejo).
- Reutilizar un tag para «arreglar» algo.
- Subir un major sin migrador ni nota.
- Tocar el HTML generado a mano: el siguiente render lo pisa. Se toca el programa.

Hecho con ❤️ por David Antizar
