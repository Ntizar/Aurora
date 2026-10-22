# Iconos numerados de Aurora

Cada icono tiene un **número estable** —`nz-i-001`, `nz-i-042`— que **no se reutiliza
nunca**. El número es la referencia pública: un diseño, un ticket o un agente pueden decir
«el icono 042» y todos hablan del mismo dibujo. El nombre castellano es la comodidad; el
número es el contrato.

- Colecciones: **Lucide** (ISC, trazo preciso, [lucide.dev](https://lucide.dev)) y
  **Solar** (CC BY 4.0, trazo 1,5, más expresivo, 480 Design). El número es único entre las
  dos: `nz-i-001` es siempre el mismo dibujo, venga de donde venga.
- Formato: SVG plano de 24×24, `fill="none"`, `stroke="currentColor"`,
  `stroke-width` heredado de `--nz-icon-stroke`. Ni un color a mano: el icono se pinta con
  el color del texto y por eso funciona igual en claro y en oscuro.
- Clase: `.nz-icon` (pack `p9-media.css`). No hay CSS propio de iconos: el sistema ya lo
  tenía; lo que faltaba era el **repositorio**.

## Qué hay aquí

| Fichero | Qué es | ¿Se edita a mano? |
|---|---|---|
| `iconos.json` | Manifiesto: número, id de Lucide, nombre, grupo, licencia, hash | **No** — lo escribe `scripts/iconos.py` |
| `NNN-nombre.svg` | Un fichero por icono, con su número en el nombre y en `data-icono` | **No** — se genera |
| `sprite.svg` | Todos los iconos como `<symbol id="nz-i-NNN">` para usar con `<use>` | **No** — se genera |
| `index.html` | Catálogo navegable por número, nombre o id de Lucide | **No** — se genera |
| `README.md` | Este documento (doctrina) | Sí |

Cifras vivas: **338 iconos (288 Lucide + 50 Solar) · 13 grupos**. El número no se escribe aquí porque caduca:
`python3 scripts/iconos.py listar | tail -1` o el propio `iconos.json`.

## Cómo se consume

En línea, cuando quieres cero peticiones extra (el consumidor copia el SVG del fichero):

```html
<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true">
  <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
</svg>
```

Por sprite, una sola petición para todos los iconos de la página:

```html
<svg class="nz-icon" aria-hidden="true"><use href="iconos/sprite.svg#nz-i-001"/></svg>
```

Consultando el manifiesto (agentes, generadores, scripts):

```bash
python3 -c "import json;m=json.load(open('iconos/iconos.json'));print([i for i in m['iconos'] if i['numero']==42][0])"
```

### El color lo pone el texto; se cambia con un modificador

El trazo es `currentColor`: no hay una versión «en naranja» de cada icono — hay una sola
versión y obedece. Tono: `.nz-icon--accent`, `--brand`, `--success`, `--warning`, `--danger`,
`--info`, `--invert` (y en las cajas, `.nz-icon-tile--accent`). Grosor: `--fino` (1,5) y
`--grueso` (2,25), para cuando el 1,75 de serie no basta a ese tamaño.

El catálogo trae selector de tono; con `?tono=acento` se abre ya en naranja.

## Cómo se amplía

```bash
python3 scripts/iconos.py anadir lucide:pill --grupo estados        # asigna el siguiente número
python3 scripts/iconos.py anadir solar:magic-stick-3 --nombre varita # otra colección, mismo número
python3 scripts/iconos.py listar --grupo mapas                      # qué hay y con qué número
python3 scripts/iconos.py retirar 042                               # lo retira y deja el hueco declarado
python3 scripts/iconos.py todo                                      # sprite + catálogo
python3 scripts/auditar-iconos.py --check                           # la puerta: 0 fallos o no está hecho
```

`anadir` compone el nombre castellano con el glosario de `scripts/iconos.py`. Si un token
no está traducido, **no inventa**: lo dice y para. Se añade al glosario (o se pasa
`--nombre`), porque un icono con nombre en inglés es deuda silenciosa.

## Reglas duras

1. **Un número no se reutiliza.** Retirar un icono deja su número en `numerosRetirados`;
   el siguiente icono coge el siguiente número libre, no el hueco.
2. **Un id de Lucide entra una sola vez.** El manifiesto no admite el mismo dibujo dos veces.
3. **Nada de color a mano, ni `stroke-width` fijo, ni `<text>`.** El icono hereda color y
   grosor; si no, rompe el tema oscuro y la paridad entre móvil, PC y capturas.
4. **El nombre es castellano** (los préstamos asentados —menú, kanban, vídeo, radio,
   terminal, wifi, bluetooth, bot, webhook— ya lo son). Las marcas conservan su nombre.
5. **El fichero se llama `NNN-nombre.svg`** y el número va también dentro (`data-icono`).
6. **El catálogo y el sprite no se editan a mano**: `iconos.py --check` compara bytes y caza
   cualquier retoque.
7. **Atribución obligatoria.** Lucide es ISC y Solar es **CC BY 4.0**: si un producto sirve
   iconos de Solar, mantiene la mención a **480 Design** (y a Lucide, si usa los suyos). El
   manifiesto guarda la licencia de cada icono y `scripts/auditar-iconos.py` falla si falta.
   El icono no viaja sin su licencia.
8. **Un estilo por colección.** De Solar entra solo el peso **lineal**: `bold`, `outline`,
   `broken` y `duotone` son otro dibujo, no otra versión, y mezclarlos rompería la unidad
   visual del sistema. Si algún día hace falta duotono, será un objeto aparte, no un icono más.

## Por qué numerar y no solo nombrar

Porque los nombres cambian y los números no. Lucide renombra sin piedad
(`home` → `house`, `check-circle` → `circle-check`) y el set crece; si la referencia es el
nombre, cada renombrado rompe diseños, tickets y prompts de agentes. Con número estable,
renombrar es cosmético: el 042 sigue siendo el 042. Es la misma idea que ya usan las
páginas del catálogo (`01`…`18`): un índice que no se mueve.

Hecho con ❤️ por David Antizar
