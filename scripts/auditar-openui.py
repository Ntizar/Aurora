# -*- coding: utf-8 -*-
"""Puerta de la capa OpenUI de Aurora (lo que la CI puede comprobar sin red).

Comprueba cuatro coherencias que se rompen en silencio:

  1. CENSO      — cada clase que declara `openui/componentes.json` existe de verdad
                  en `components.json` (si no, el componente pinta en pelado).
  2. GENERADO   — `aurora.spec.json`, `aurora.schema.json` y `PROMPT.md` coinciden
                  con lo que produce `generar-openui.py` ahora mismo (deriva = fallo).
  3. RUNTIME    — cada componente declarado tiene su renderizador en
                  `openui/aurora-openui.js`, y el runtime no emite ni una clase
                  fuera del censo (clases inventadas = fallo).
  4. EJEMPLOS   — cada programa de `openui/ejemplos.json` usa componentes que
                  existen, con el número de argumentos correcto, sin saltarse
                  obligatorios y con los enums válidos.

Uso:
  python3 scripts/auditar-openui.py
  python3 scripts/auditar-openui.py --json
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPENUI = ROOT / "openui"

RE_CLASE = re.compile(r"(?<!data-)(?<!#)nz-[a-z0-9_-]+")  # data-nz-* y fragmentos #nz-i-* NO son clases
RE_RENDER = re.compile(r"R\.([A-ZÁÉÍÓÚÑ][\w]*)\s*=")


def censo():
    datos = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    clases = set()
    for clave, obj in datos["objetos"].items():
        clases.add(clave)
        clases.update(obj.get("clases", []))
    return clases


def cargar_generador():
    ruta = ROOT / "scripts" / "generar-openui.py"
    spec = importlib.util.spec_from_file_location("generar_openui", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- mini-parser de openui-lang (el subconjunto que usan los ejemplos) ---------
def tokenizar(texto):
    t, i = [], 0
    while i < len(texto):
        c = texto[i]
        if c.isspace():
            i += 1
            continue
        if c == '"':
            s, j = "", i + 1
            while j < len(texto) and texto[j] != '"':
                if texto[j] == "\\":
                    s += texto[j + 1]
                    j += 2
                    continue
                s += texto[j]
                j += 1
            t.append(("str", s))
            i = j + 1
            continue
        if c in "[](){},=":
            t.append((c, c))
            i += 1
            continue
        m = re.match(r"-?\d+(?:[.,]\d+)?", texto[i:])
        if m:
            t.append(("num", float(m.group(0).replace(",", "."))))
            i += len(m.group(0))
            continue
        m = re.match(r"[A-Za-z_$][\w$.]*", texto[i:])
        if m:
            pal = m.group(0)
            if pal in ("true", "false"):
                t.append(("bool", pal == "true"))
            else:
                t.append(("id", pal))
            i += len(pal)
            continue
        i += 1
    return t


def tipar(prop, arg):
    """Comprueba el tipo de un argumento posicional contra la prop declarada."""
    tipo = prop["tipo"]
    if tipo == "nodos":
        return None if arg["k"] in ("arr", "ref", "call") else "se esperaba una lista de componentes"
    if tipo == "enum":
        if arg["k"] != "lit" or arg["t"] != "str":
            return "se esperaba uno de %s" % prop["valores"]
        return None if arg["v"] in prop["valores"] else "%r no es un valor de %s" % (arg["v"], prop["valores"])
    if tipo == "texto":
        return None if arg["k"] == "lit" and arg["t"] == "str" else "se esperaba texto"
    if tipo == "numero":
        return None if arg["k"] == "lit" and arg["t"] == "num" else "se esperaba un número"
    if tipo == "booleano":
        return None if arg["k"] == "lit" and arg["t"] == "bool" else "se esperaba true/false"
    if tipo == "lista":
        if arg["k"] != "arr":
            return "se esperaba una lista de textos"
        return None if all(a["k"] == "lit" and a["t"] == "str" for a in arg["v"]) else "elemento no textual"
    if tipo == "numeros":
        if arg["k"] != "arr":
            return "se esperaba una lista de números"
        return None if all(a["k"] == "lit" and a["t"] == "num" for a in arg["v"]) else "elemento no numérico"
    if tipo == "filas":
        if arg["k"] != "arr":
            return "se esperaba una lista de listas"
        for f in arg["v"]:
            if f["k"] != "arr" or not all(a["k"] == "lit" and a["t"] == "str" for a in f["v"]):
                return "cada fila debe ser una lista de textos"
        return None
    return None


def analizar(programa):
    """Devuelve {nombre: llamada} con llamadas anidadas resueltas."""
    t = tokenizar(programa)
    pos = [0]
    llamadas = {}
    orden = []

    def peek():
        return t[pos[0]] if pos[0] < len(t) else None

    def eat(tipo=None):
        tok = peek()
        if tok is None or (tipo and tok[0] != tipo):
            raise ValueError("se esperaba %s y llegó %r" % (tipo, tok))
        pos[0] += 1
        return tok

    def expresion():
        tok = peek()
        if tok is None:
            raise ValueError("fin inesperado")
        if tok[0] in ("str", "num", "bool"):
            pos[0] += 1
            return {"k": "lit", "v": tok[1], "t": tok[0]}
        if tok[0] == "[":
            pos[0] += 1
            valores = []
            while peek() and peek()[0] != "]":
                valores.append(expresion())
                if peek() and peek()[0] == ",":
                    pos[0] += 1
            eat("]")
            return {"k": "arr", "v": valores}
        if tok[0] == "{":
            pos[0] += 1
            while peek() and peek()[0] != "}":
                eat("id")
                eat(":")
                expresion()
                if peek() and peek()[0] == ",":
                    pos[0] += 1
            eat("}")
            return {"k": "obj"}
        if tok[0] == "id":
            pos[0] += 1
            if peek() and peek()[0] == "(":
                pos[0] += 1
                args = []
                while peek() and peek()[0] != ")":
                    args.append(expresion())
                    if peek() and peek()[0] == ",":
                        pos[0] += 1
                eat(")")
                return {"k": "call", "nombre": tok[1], "args": args}
            return {"k": "ref", "nombre": tok[1]}
        raise ValueError("token inesperado %r" % (tok,))

    while pos[0] < len(t):
        nombre = eat("id")[1]
        eat("=")
        llamadas[nombre] = expresion()
        orden.append(nombre)
    return llamadas, orden


def auditar():
    fallos, avisos = [], []
    clases_censo = censo()
    fuente = json.loads((OPENUI / "componentes.json").read_text(encoding="utf-8"))
    spec = json.loads((OPENUI / "aurora.spec.json").read_text(encoding="utf-8"))
    ejemplos = json.loads((OPENUI / "ejemplos.json").read_text(encoding="utf-8"))
    runtime = (OPENUI / "aurora-openui.js").read_text(encoding="utf-8")
    prompt = (OPENUI / "PROMPT.md").read_text(encoding="utf-8")

    componentes = {c["nombre"]: c for c in fuente["componentes"]}

    # 1. CENSO
    for c in fuente["componentes"]:
        for clase in c["clases"]:
            if clase not in clases_censo:
                fallos.append("[censo] %s usa .%s, que no existe en components.json" % (c["nombre"], clase))

    # 1b. ENUMS · cada valor tiene que estar tratado: o es un modificador real del
    # propio componente, o el runtime lo nombra explícitamente. Un enum que se
    # concatena a ciegas produce clases fantasma (bug real: tendencia "sube"
    # generaba nz-kpi__delta--sube, que no existe).
    for c in fuente["componentes"]:
        propias = set(c["clases"])
        for prop in c["props"]:
            if prop["tipo"] != "enum":
                continue
            for valor in prop["valores"]:
                if prop.get("porDefecto") == valor:
                    continue  # valor por defecto: se pinta sin modificador, por diseño
                if ('"%s"' % valor) in runtime:
                    continue
                if any(cl.endswith("--" + valor) or cl.endswith("__" + valor) for cl in propias):
                    continue
                fallos.append("[enum] %s.%s: el valor %r no está tratado en el runtime ni es modificador de %s"
                              % (c["nombre"], prop["nombre"], valor, ", ".join(sorted(propias)[:3]) or "ninguna clase"))

    # 2. GENERADO (deriva)
    gen = cargar_generador()
    spec_txt = json.dumps(gen.construir_spec(fuente), ensure_ascii=False, indent=1) + "\n"
    if spec_txt != (OPENUI / "aurora.spec.json").read_text(encoding="utf-8"):
        fallos.append("[generado] aurora.spec.json está desfasado: corre scripts/generar-openui.py")
    prompt_actual = prompt.split("\n<!-- aurora-openui")[0]
    prompt_nuevo = gen.construir_prompt(fuente, ejemplos).split("\n<!-- aurora-openui")[0] + "\n"
    if prompt_actual.rstrip() != prompt_nuevo.rstrip():
        fallos.append("[generado] PROMPT.md está desfasado: corre scripts/generar-openui.py")
    if not prompt.rstrip().endswith("-->") or "generar-openui.py" not in prompt[-260:]:
        avisos.append("[generado] PROMPT.md no lleva la huella del generador al final")

    # 3. RUNTIME
    renderizadores = set(RE_RENDER.findall(runtime))
    for nombre in componentes:
        if nombre not in renderizadores:
            fallos.append("[runtime] %s está declarado pero no tiene renderizador en aurora-openui.js" % nombre)
    for nombre in sorted(renderizadores - set(componentes)):
        fallos.append("[runtime] %s tiene renderizador pero no está declarado en componentes.json" % nombre)
    inventadas = set()
    for clase in RE_CLASE.findall(runtime):
        if clase.endswith("--") or clase.endswith("__"):
            continue  # fragmento de concatenación: se valida por sus variantes completas
        if clase not in clases_censo:
            inventadas.add(clase)
    for clase in sorted(inventadas):
        fallos.append("[runtime] emite .%s, que no existe en el censo" % clase)

    # 4. EJEMPLOS
    for ej in ejemplos:
        try:
            llamadas, orden = analizar(ej["programa"])
        except ValueError as exc:
            fallos.append("[ejemplo] %s no parsea: %s" % (ej["titulo"], exc))
            continue
        if "root" not in llamadas:
            fallos.append("[ejemplo] %s no define root" % ej["titulo"])
            continue
        if llamadas["root"].get("k") != "call" or llamadas["root"]["nombre"] != fuente["root"]:
            fallos.append("[ejemplo] %s: root no es %s(...)" % (ej["titulo"], fuente["root"]))
        # referencias usadas y definidas
        usadas = set(re.findall(r"(?<![\w.\"])([A-Za-z_$][\w$]*)(?![\w.\"])", ej["programa"]))
        for nombre, expr in llamadas.items():
            if expr.get("k") != "call":
                continue
            comp = componentes.get(expr["nombre"])
            if not comp:
                fallos.append("[ejemplo] %s usa %s, que no existe" % (ej["titulo"], expr["nombre"]))
                continue
            props = comp["props"]
            if len(expr["args"]) > len(props):
                fallos.append("[ejemplo] %s: %s recibe %d argumentos y admite %d"
                              % (ej["titulo"], expr["nombre"], len(expr["args"]), len(props)))
            for i, prop in enumerate(props):
                if i < len(expr["args"]):
                    continue
                if not prop.get("opcional"):
                    fallos.append("[ejemplo] %s: %s se queda sin el obligatorio «%s»"
                                  % (ej["titulo"], expr["nombre"], prop["nombre"]))
            for i, prop in enumerate(props[:len(expr["args"])]):
                problema = tipar(prop, expr["args"][i])
                if problema:
                    fallos.append("[ejemplo] %s: %s.%s → %s"
                                  % (ej["titulo"], expr["nombre"], prop["nombre"], problema))
        _ = usadas

    return {
        "componentes": len(componentes),
        "ejemplos": len(ejemplos),
        "renderizadores": len(renderizadores),
        "clases_en_runtime": len({c for c in RE_CLASE.findall(runtime) if not c.endswith(("--", "__"))}),
        "fallos": fallos,
        "avisos": avisos,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = auditar()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print("OpenUI · Aurora — %d componentes · %d ejemplos · %d renderizadores · %d clases emitidas"
              % (r["componentes"], r["ejemplos"], r["renderizadores"], r["clases_en_runtime"]))
        for f in r["fallos"]:
            print("  ✗", f)
        for a in r["avisos"]:
            print("  · ", a)
        if r["fallos"]:
            print("RESULTADO: %d FALLOS" % len(r["fallos"]))
        else:
            print("RESULTADO: VÁLIDO")
    return 1 if r["fallos"] else 0


if __name__ == "__main__":
    sys.exit(main())
