#!/usr/bin/env python3
"""Servidor MCP de Aurora — que cualquier agente (Claude Code, Cursor, VS Code,
Codex…) consulte el sistema sin bajar medio megabyte ni adivinar versiones.

Filosofía afectUI ("agent-ready") aplicada a Aurora: una línea de conexión y el
agente tiene el censo VIVO, el juez de lint y el compilador del lenguaje.

  claude mcp add aurora -- python C:/Users/d_ant/Projects/Aurora-7/scripts/mcp-aurora.py
  cursor:  "mcpServers": {"aurora": {"command": "python", "args": ["…/scripts/mcp-aurora.py"]}}

Transporte: stdio con mensajes JSON-RPC por línea (NDJSON), sin dependencias
externas — solo la stdlib. La fuente de verdad es el repo: los datos se leen de
components.json y datos/base-diseno.json en cada arranque (nunca de memoria).

Herramientas:
  estado_del_sistema    → PASO 0 automático: versión, cifras y canales vigentes
  buscar_por_necesidad  → índice de base-diseno.json: «tabla apilable», «chat»…
  leer_componente       → API exacta de una familia: clases, markup, tokens, noUsar
  validar_html          → auditar-uso.py sobre TU html (el juez del repo)
  compilar_programa     → programa OpenUI Lang → HTML con marca/packs/firma resueltos

Autochequeo (para CI, sin red):  python scripts/mcp-aurora.py --test
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTOCOLOS_SOPORTADOS = ("2025-06-18", "2025-03-26", "2024-11-05")


# ---------------------------------------------------------------- datos ----
def cargar_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def estado():
    comp = cargar_json("components.json")
    canales = cargar_json("datos/canales.json")
    return comp, canales


def indice_base():
    return cargar_json("datos/base-diseno.json")


class Aurora:
    """Carga los datos una vez y resuelve las herramientas."""

    def __init__(self):
        self.comp, self.canales = estado()
        self.base = indice_base()
        self.familias = self.comp.get("objetos", {})
        # índice de búsqueda: texto normalizado por familia
        self._indice = {}
        for nombre, f in self.familias.items():
            blob = " ".join([
                nombre,
                " ".join(f.get("alias", [])),
                " ".join(f.get("clases", [])),
                f.get("pack", ""),
                (f.get("markup", {}) or {}).get("markup", ""),
                " ".join(f.get("noUsar", []) if isinstance(f.get("noUsar"), list)
                         else [str(f.get("noUsar", ""))]),
            ]).lower()
            self._indice[nombre] = blob
        self.familias_base = {}
        for f in self.base.get("familias", []):
            self.familias_base[f.get("nombre", "")] = f

    # --- herramientas ------------------------------------------------------
    def estado_del_sistema(self, _args):
        can = self.canales["canales"]
        n = len(self.familias)
        return json.dumps({
            "version": self.comp.get("version"),
            "cdn": self.comp.get("cdn"),
            "cifras": {"familias": n,
                       "clases": self.comp.get("totalClases"),
                       "componentesGenerativos": 36},
            "canalVivo": can["vivo"]["rango"],
            "canalCongelado": can["congelado"]["tag"],
            "regla": "Para leer: @master/llms.txt. Para publicar: tag exacto pineado. "
                     "Nunca @master en producción. Resuelve la versión aquí, nunca de memoria.",
            "documentos": {
                "guia": self.comp.get("cdn", "") + "LLM.md",
                "api": self.comp.get("cdn", "") + "components.json",
                "indice": self.comp.get("cdn", "") + "llms-full.txt",
            },
        }, ensure_ascii=False, indent=2)

    def buscar_por_necesidad(self, args):
        consulta = str(args.get("consulta", "")).lower().split()
        if not consulta:
            return "Indica una necesidad, p.ej. «tabla apilable», «chat con composer», «kpi con delta»."
        puntuados = []
        for nombre, blob in self._indice.items():
            score = sum(blob.count(p) * (3 if p in nombre.lower() else 1)
                        for p in consulta if len(p) > 2)
            if score:
                puntuados.append((score, nombre))
        puntuados.sort(reverse=True)
        if not puntuados:
            # sin coincidencia textual: sugiere por familias de la base de diseño
            return ("Sin coincidencia textual. Prueba con términos del léxico: "
                    "tabla, kpi, chat, formulario, navbar, alerta, grafico, modal, "
                    "campo, boton, ficha… o pide `leer_componente` por nombre.")
        sal = []
        for score, nombre in puntuados[:8]:
            f = self.familias[nombre]
            sal.append({
                "familia": nombre,
                "pack": "packs/" + f.get("pack", ""),
                "clases": f.get("clases", [])[:8],
                "alias": f.get("alias", []),
                "demo": "https://ntizar.github.io/Aurora/paginas/",
                "puntaje": score,
            })
        return json.dumps({"resultados": sal, "consejo":
                           "lee el componente con leer_componente antes de escribir markup; "
                           "si algo no está en components.json, no existe."}, ensure_ascii=False, indent=2)

    def leer_componente(self, args):
        nombre = str(args.get("familia", "")).strip()
        f = self.familias.get(nombre)
        if not f:
            # tolerancia: acepta alias o clase suelta
            for k, v in self.familias.items():
                if nombre in v.get("clases", []) or nombre in v.get("alias", []):
                    f, nombre = v, k
                    break
        if not f:
            return "Familia «%s» no está en el censo (si no está en components.json, no existe)." % nombre
        m = f.get("markup") or {}
        return json.dumps({
            "familia": nombre,
            "packAEnlazar": "packs/" + f.get("pack", ""),
            "clases": f.get("clases", []),
            "markup": m.get("markup", ""),
            "tokens": f.get("tokens", []),
            "antiPatrones": f.get("noUsar", []),
            "aliasEN": f.get("alias", []),
        }, ensure_ascii=False, indent=2)

    def validar_html(self, args):
        html = str(args.get("html", ""))
        if not html.strip():
            return "Pásame el HTML completo en el argumento `html`."
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(html)
            ruta = fh.name
        r = subprocess.run([sys.executable, str(ROOT / "scripts/auditar-uso.py"), ruta],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        salida = (r.stdout + r.stderr).strip()
        pathlib.Path(ruta).unlink(missing_ok=True)
        veredicto = "PASA (0 fallos)" if r.returncode == 0 else "FALLA"
        return "«auditar-uso.py» del repo → %s\n\n%s" % (veredicto, salida[:6000])

    def compilar_programa(self, args):
        programa = str(args.get("programa", ""))
        if "root = Pagina(" not in programa:
            return ("El programa debe empezar por `root = Pagina([...])` con argumentos "
                    "posicionales (ver openui/PROMPT.md, 36 firmas).")
        with tempfile.NamedTemporaryFile("w", suffix=".openui", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(programa)
            src = fh.name
        out = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                          encoding="utf-8").name
        cmd = [sys.executable, str(ROOT / "scripts/programa-a-html.py"), src,
               "--salida", out,
               "--marca", str(args.get("marca", "ntizar")),
               "--tema", str(args.get("tema", "light"))]
        if args.get("firma"):
            cmd += ["--firma", str(args["firma"])]
        if args.get("inicio"):
            cmd += ["--inicio", str(args["inicio"]), "--modo", "producto"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        pathlib.Path(src).unlink(missing_ok=True)
        if r.returncode != 0:
            return "El compilador rechazó el programa (esto es good: falla antes de pintar):\n" + (
                r.stdout + r.stderr)[:4000]
        html = pathlib.Path(out).read_text(encoding="utf-8")
        pathlib.Path(out).unlink(missing_ok=True)
        packs = next((l for l in r.stdout.splitlines() if "packs:" in l), "")
        return json.dumps({
            "compilado": True,
            "resumen": r.stdout.splitlines()[0] if r.stdout else "",
            "packs": packs,
            "siguiente": "validar el HTML con validar_html y medir en navegador si es entrega.",
            "html": html,
        }, ensure_ascii=False)


HERRAMIENTAS = [
    {"name": "estado_del_sistema",
     "description": "PASO 0 automático de Aurora: versión vigente, canal vivo/congelado "
                    "y cifras del censo. Úsalo ANTES de citar cualquier versión o URL de CDN.",
     "inputSchema": {"type": "object", "properties": {}, "required": []},
     "fn": "estado_del_sistema"},
    {"name": "buscar_por_necesidad",
     "description": "Busca familias del censo por una necesidad en castellano "
                    "(«tabla apilable», «chat con composer», «kpi con delta»). "
                    "Devuelve familias con su pack y demo.",
     "inputSchema": {"type": "object",
                     "properties": {"consulta": {"type": "string",
                                                 "description": "Necesidad en castellano"}},
                     "required": ["consulta"]},
     "fn": "buscar_por_necesidad"},
    {"name": "leer_componente",
     "description": "API exacta de una familia del censo: clases, markup real, tokens, "
                    "anti-patrón y pack a enlazar. Si no existe aquí, no existe en Aurora.",
     "inputSchema": {"type": "object",
                     "properties": {"familia": {"type": "string",
                                                "description": "Nombre de familia o clase, p.ej. nz-table"}},
                     "required": ["familia"]},
     "fn": "leer_componente"},
    {"name": "validar_html",
     "description": "Ejecuta el auditar-uso.py del repo sobre un HTML: clases inventadas, "
                    "packs que faltan, gradientes, colores a mano, jerarquía, firma. "
                    "0 fallos o no está terminado.",
     "inputSchema": {"type": "object",
                     "properties": {"html": {"type": "string", "description": "HTML completo"}},
                     "required": ["html"]},
     "fn": "validar_html"},
    {"name": "compilar_programa",
     "description": "Compila un programa OpenUI Lang (root = Pagina([...]), argumentos "
                    " posicionales) a HTML con marca, tema, packs y firma resueltos. "
                    "Falla con diagnóstico si el programa es inválido.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "programa": {"type": "string", "description": "Programa .openui"},
                         "marca": {"type": "string", "description": "aurora|indigo|esmeralda|violeta|carmesi|ntizar"},
                         "tema": {"type": "string", "description": "light|dark"},
                         "firma": {"type": "string", "description": "full|subtle|none"},
                         "inicio": {"type": "string", "description": "Ruta de inicio (homeRoute); añade --modo producto"},
                     },
                     "required": ["programa"]},
     "fn": "compilar_programa"},
]


# ----------------------------------------------------------- protocolo ----
def responder(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def atender(linea, aurora):
    try:
        req = json.loads(linea)
    except json.JSONDecodeError:
        return
    metodo = req.get("method")
    id_ = req.get("id")
    if id_ is None:          # notificación: sin respuesta
        return
    if metodo == "initialize":
        proto = req.get("params", {}).get("protocolVersion", "2024-11-05")
        if proto not in PROTOCOLOS_SOPORTADOS:
            proto = "2024-11-05"
        responder({"jsonrpc": "2.0", "id": id_, "result": {
            "protocolVersion": proto,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "aurora", "version": aurora.comp.get("version", "?")},
            "instructions": "Aurora: design system de Ntizar. Empieza por estado_del_sistema. "
                            "Si no está en components.json, no existe.",
        }})
    elif metodo == "tools/list":
        responder({"jsonrpc": "2.0", "id": id_, "result": {
            "tools": [{k: v for k, v in h.items() if k != "fn"} for h in HERRAMIENTAS]}})
    elif metodo == "tools/call":
        params = req.get("params", {})
        nombre = params.get("name")
        args = params.get("arguments") or {}
        h = next((x for x in HERRAMIENTAS if x["name"] == nombre), None)
        if not h:
            responder({"jsonrpc": "2.0", "id": id_,
                       "error": {"code": -32602, "message": "herramienta desconocida: %s" % nombre}})
            return
        try:
            texto = getattr(aurora, h["fn"])(args)
            responder({"jsonrpc": "2.0", "id": id_,
                       "result": {"content": [{"type": "text", "text": texto}],
                                  "isError": False}})
        except Exception as e:  # el agente debe ver el error, no un cuelgue
            responder({"jsonrpc": "2.0", "id": id_,
                       "result": {"content": [{"type": "text",
                                               "text": "Error de Aurora: %s" % e}],
                                  "isError": True}})
    elif metodo == "ping":
        responder({"jsonrpc": "2.0", "id": id_, "result": {}})
    else:
        responder({"jsonrpc": "2.0", "id": id_,
                   "error": {"code": -32601, "message": "método no soportado: %s" % metodo}})


def test():
    """Autochequeo sin red: arranca, habla el protocolo y consulta sus 5 herramientas."""
    aurora = Aurora()
    pasos = []
    init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-03-26",
                                  "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}})
    lineas = [
        init,
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
        json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "estado_del_sistema", "arguments": {}}}),
        json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                    "params": {"name": "buscar_por_necesidad",
                               "arguments": {"consulta": "tabla apilable"}}}),
        json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                    "params": {"name": "leer_componente",
                               "arguments": {"familia": "nz-table"}}}),
        json.dumps({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                    "params": {"name": "validar_html",
                               "arguments": {"html": "<html><body class=\"nz\"><h1>hola</h1></body></html>"}}}),
        json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                    "params": {"name": "compilar_programa",
                               "arguments": {"programa": "root = Pagina([t], \"contenido\")\nt = Titular(\"Prueba\", \"1\")",
                                             "marca": "ntizar"}}}),
    ]
    r = subprocess.run([sys.executable, str(ROOT / "scripts/mcp-aurora.py")],
                       input="\n".join(lineas) + "\n",
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    respuestas = [json.loads(l) for l in r.stdout.splitlines() if l.strip().startswith("{")]
    por_id = {m.get("id"): m for m in respuestas if "id" in m}
    ok = lambda c, m: pasos.append(("✓ " if c else "✗ ") + m)
    ok(por_id.get(1, {}).get("result", {}).get("serverInfo", {}).get("name") == "aurora",
       "initialize → serverInfo aurora v%s" % aurora.comp.get("version"))
    ok(len(por_id.get(2, {}).get("result", {}).get("tools", [])) == 5,
       "tools/list → 5 herramientas")
    estado_txt = por_id.get(3, {}).get("result", {}).get("content", [{}])[0].get("text", "")
    ok(aurora.comp.get("version", "x") in estado_txt, "estado_del_sistema → versión viva")
    busq = por_id.get(4, {}).get("result", {}).get("content", [{}])[0].get("text", "")
    ok("nz-table" in busq, "buscar_por_necesidad(«tabla apilable») → nz-table")
    comp = por_id.get(5, {}).get("result", {}).get("content", [{}])[0].get("text", "")
    ok("packAEnlazar" in comp, "leer_componente(nz-table) → markup + pack")
    val = por_id.get(6, {}).get("result", {}).get("content", [{}])[0].get("text", "")
    ok("auditar-uso" in val, "validar_html → veredicto del juez")
    comp = por_id.get(7, {}).get("result", {}).get("content", [{}])[0].get("text", "")
    ok('"compilado": true' in comp, "compilar_programa(.openui) → HTML con packs")
    print("\n".join(pasos))
    malos = [p for p in pasos if p.startswith("✗")]
    if malos or r.returncode != 0:
        print("STDERR:", (r.stderr or "")[:800])
        sys.exit(1)
    print("\nRESULTADO: MCP de Aurora operativo — 5/5 herramientas ✅")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--test", action="store_true", help="autochequeo del protocolo (CI)")
    ns = ap.parse_args()
    if ns.test:
        test()
        return
    aurora = Aurora()  # carga de datos al arranque; stderr para no ensuciar el canal
    print("Aurora MCP v%s listo (5 herramientas) — escuchando en stdio" %
          aurora.comp.get("version"), file=sys.stderr)
    for linea in sys.stdin:
        if linea.strip():
            atender(linea, aurora)


if __name__ == "__main__":
    main()
