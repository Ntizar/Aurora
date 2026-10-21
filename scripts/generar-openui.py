# -*- coding: utf-8 -*-
"""Genera la capa OpenUI de Aurora desde `openui/componentes.json`.

Fuente única (a mano):  openui/componentes.json  +  openui/ejemplos.json
Salidas (generadas):
  · openui/aurora.schema.json  — JSON Schema de la biblioteca (lo consume el parser)
  · openui/aurora.spec.json    — firma + descripción + grupos + schema (lo consume el runtime y el prompt)
  · openui/PROMPT.md           — system prompt para el LLM (formato lang-core 1.0.1)

Nada de esto se edita a mano: `auditar-openui.py --check` compara el disco con
lo que este generador produciría ahora mismo.

Uso:
  python3 scripts/generar-openui.py
  python3 scripts/generar-openui.py --check     # solo comprueba, no escribe
"""
import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPENUI = ROOT / "openui"

# tipo lógico → (fragmento JSON Schema, anotación de firma)
TIPOS = {
    "nodos":   ({"type": "array", "items": {}}, "any[]"),
    "texto":   ({"type": "string"}, "string"),
    "numero":  ({"type": "number"}, "number"),
    "booleano": ({"type": "boolean"}, "boolean"),
    "lista":   ({"type": "array", "items": {"type": "string"}}, "string[]"),
    "numeros": ({"type": "array", "items": {"type": "number"}}, "number[]"),
    "filas":   ({"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "string[][]"),
}


def ann(prop):
    tipo = prop["tipo"]
    if tipo == "enum":
        return " | ".join('"%s"' % v for v in prop["valores"])
    if tipo not in TIPOS:
        raise SystemExit("Tipo desconocido %r en %s" % (tipo, prop.get("nombre")))
    return TIPOS[tipo][1]


def schema_prop(prop):
    tipo = prop["tipo"]
    if tipo == "enum":
        return {"type": "string", "enum": list(prop["valores"])}
    if tipo not in TIPOS:
        raise SystemExit("Tipo desconocido %r en %s" % (tipo, prop.get("nombre")))
    return json.loads(json.dumps(TIPOS[tipo][0]))


def firma(c):
    partes = []
    for p in c["props"]:
        marca = "?" if p.get("opcional") else ""
        partes.append("%s%s: %s" % (p["nombre"], marca, ann(p)))
    return "%s(%s)" % (c["nombre"], ", ".join(partes))


def construir_schema(fuente):
    defs, props, required = {}, {}, []
    for c in fuente["componentes"]:
        p, req = {}, []
        for prop in c["props"]:
            p[prop["nombre"]] = schema_prop(prop)
            if not prop.get("opcional"):
                req.append(prop["nombre"])
        defs[c["nombre"]] = {
            "type": "object",
            "properties": p,
            "required": req,
            "additionalProperties": False,
            "description": c["descripcion"],
        }
        props[c["nombre"]] = {"$ref": "#/$defs/%s" % c["nombre"]}
        required.append(c["nombre"])
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": props,
        "required": required,
        "additionalProperties": False,
        "$defs": defs,
    }


def construir_spec(fuente):
    return {
        "generado": "scripts/generar-openui.py — no editar a mano",
        "version": fuente["version"],
        "root": fuente["root"],
        "idioma": fuente.get("idioma", "es"),
        "componentGroups": [
            {"name": g["nombre"], "components": list(g["componentes"])}
            for g in fuente["grupos"]
        ],
        "components": {
            c["nombre"]: {"signature": firma(c), "description": c["descripcion"]}
            for c in fuente["componentes"]
        },
        "schema": construir_schema(fuente),
    }


def construir_prompt(fuente, ejemplos):
    total = len(fuente["componentes"])
    L = []
    L.append("# System prompt · Aurora Generative UI (OpenUI Lang)")
    L.append("")
    L.append("Eres un generador de interfaces para **Aurora**, el design system de Ntizar.")
    L.append("Respondes EXCLUSIVAMENTE con openui-lang: una línea por sentencia, sin markdown,")
    L.append("sin explicaciones y sin HTML. Aurora pone el CSS; tú solo eliges componentes y datos.")
    L.append("")
    L.append("## Reglas de sintaxis")
    L.append("")
    L.append("1. Cada sentencia va en su línea: `identificador = Expresión`.")
    L.append("2. `root` es la entrada: todo programa empieza por `root = Pagina([...])`.")
    L.append("3. Las expresiones son cadenas (\"...\"), números, booleanos (true/false), arrays ([...]),")
    L.append("   objetos ({...}) o llamadas a componente `Nombre(arg1, arg2, ...)`.")
    L.append("4. Usa referencias para leer mejor: define `kpis = Rejilla([...])` y úsalo después.")
    L.append("5. TODA variable (menos root) debe estar referenciada por otra; si no, no se pinta.")
    L.append("6. Los argumentos son POSICIONALES: `Kpi(\"Ventas\", \"1.240\", \"+12%\", \"sube\", \"acento\")`.")
    L.append("   La sintaxis con nombre (`Kpi(etiqueta: \"Ventas\")`) NO existe y rompe el programa.")
    L.append("7. Los opcionales se omiten desde el final.")
    L.append("")
    L.append("## Firmas de componentes (%d)" % total)
    L.append("")
    L.append("Los argumentos con `?` son opcionales. Los sub-componentes pueden ir en línea o por referencia")
    L.append("(mejor por referencia: el streaming se ve antes).")
    L.append("")
    por_nombre = {c["nombre"]: c for c in fuente["componentes"]}
    for g in fuente["grupos"]:
        L.append("### %s" % g["nombre"])
        for nombre in g["componentes"]:
            c = por_nombre[nombre]
            L.append("%s — %s" % (firma(c), c["descripcion"]))
        L.append("")
    L.append("## Reglas de diseño de Aurora (obligatorias)")
    L.append("")
    L.append("- El acento marca **el dato que importa** y la acción secundaria; la marca hace la estructura.")
    L.append("  Un panel entero en azul está mal; un KPI en acento está bien.")
    L.append("- Un solo `Titular(..., \"1\")` por página. Después nivel 2 y 3.")
    L.append("- `Tabla` con `apilable = true` cuando la tabla tiene más de 3 columnas (móvil la convierte")
    L.append("  en tarjetas). `numericas` recibe los nombres de columna separados por coma.")
    L.append("- Magnitudes muy dispares → `TablaBarras`, nunca `Barras` de una sola escala.")
    L.append("- **Las figuras no van a sangre.** `Barras` mide 5 rem por defecto y `Anillo` 5 rem:")
    L.append("  `lg` solo para el gráfico protagonista de la página. Un gráfico dentro de una rejilla de")
    L.append("  4 columnas se ve enorme y no aporta más dato.")
    L.append("- **No anides superficies.** Dentro de `Tarjeta` o `Seccion` no repitas contenedor:")
    L.append("  `Barras`, `Tabla`, `Lista` y `Objetivo` ya son contenido, no tarjetas.")
    L.append("- **Botones y chips van en `Fila`** (mide lo que mide y envuelve en móvil). `Rejilla` y")
    L.append("  `Formulario` son para bloques y campos; nunca para un grupo de botones.")
    L.append("- Etiqueta de botón corta: verbo + objeto, dos o tres palabras («Asignar», «Ver histórico»).")
    L.append("- Real frente a meta → `Objetivo` (la barra es el real, la línea el objetivo).")
    L.append("- Importes, fechas y porcentajes en castellano: `1.240,50 €`, `oct 2026`, `+12,4 %`.")
    L.append("- Texto real del dominio, nunca «Lorem ipsum» ni «ejemplo».")
    L.append("- No inventes componentes. Si algo no está en la lista, compón con lo que hay.")
    L.append("")
    L.append("## Hoisting y streaming (CRÍTICO)")
    L.append("")
    L.append("openui-lang permite usar una referencia ANTES de definirla: el parser resuelve al final.")
    L.append("Durante el streaming el programa se re-parsea en cada trozo, así que revela de arriba abajo.")
    L.append("Orden recomendado: 1) `root = Pagina([...])` para que el marco aparezca ya;")
    L.append("2) los bloques; 3) los datos hoja al final.")
    L.append("")
    if ejemplos:
        L.append("## Ejemplos")
        L.append("")
        for ej in ejemplos:
            L.append("### %s" % ej["titulo"])
            L.append("")
            L.append("```")
            L.append(ej["programa"].strip())
            L.append("```")
            L.append("")
    L.append("## Verificación antes de terminar")
    L.append("")
    L.append("- ¿`root` es un `Pagina(...)` y está en la primera línea?")
    L.append("- ¿Todas las variables están referenciadas y los argumentos en el orden de la firma?")
    L.append("- ¿Hay un solo titular nivel 1 y el acento está donde importa?")
    L.append("- ¿Los números están formateados en castellano?")
    return "\n".join(L) + "\n"


def huella(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="comprueba sin escribir")
    args = ap.parse_args()

    fuente = json.loads((OPENUI / "componentes.json").read_text(encoding="utf-8"))
    ejemplos = json.loads((OPENUI / "ejemplos.json").read_text(encoding="utf-8"))

    spec = construir_spec(fuente)
    spec_txt = json.dumps(spec, ensure_ascii=False, indent=1) + "\n"
    schema_txt = json.dumps(spec["schema"], ensure_ascii=False, indent=1) + "\n"
    prompt = construir_prompt(fuente, ejemplos)
    prompt += "\n<!-- aurora-openui · spec %s · %d componentes · generado por scripts/generar-openui.py -->\n" % (
        huella(spec_txt), len(fuente["componentes"]))

    salidas = {
        OPENUI / "aurora.spec.json": spec_txt,
        OPENUI / "aurora.schema.json": schema_txt,
        OPENUI / "PROMPT.md": prompt,
    }
    if args.check:
        mal = 0
        for ruta, contenido in salidas.items():
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
            if actual != contenido:
                print("DESFASADO: %s" % ruta.relative_to(ROOT))
                mal += 1
        if mal:
            print("RESULTADO: DESFASADO (%d ficheros). Ejecuta python3 scripts/generar-openui.py" % mal)
            return 1
        print("RESULTADO: AL DÍA (%d componentes)" % len(fuente["componentes"]))
        return 0

    for ruta, contenido in salidas.items():
        ruta.write_text(contenido, encoding="utf-8")
        print("escrito %-28s %5d bytes" % (ruta.relative_to(ROOT), len(contenido)))
    print("RESULTADO: GENERADO (%d componentes, %d ejemplos)" % (len(fuente["componentes"]), len(ejemplos)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
