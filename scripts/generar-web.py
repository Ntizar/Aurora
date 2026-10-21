# -*- coding: utf-8 -*-
"""De un brief a una página Aurora: el modelo rellena la plantilla, el repo la verifica.

Cadena completa:

  brief.json ──modelo (NaN)──► programa .openui ──valida──► página .html ──auditar-uso──► receipt

Nada se da por bueno sin medirlo: si el modelo devuelve algo que no valida, se le da una
segunda oportunidad con los errores delante; si vuelve a fallar, se usa la plantilla con los
datos del brief y **se dice** (nunca se entrega un programa roto en silencio).

El prompt no se escribe aquí: se lee `openui/PROMPT.md` (fuente única, la misma que usa el
resto del sistema). El modelo y la clave salen de `~/.hermes/config.yaml` y `~/.hermes/.env`;
nunca se hardcodean.

Uso:
  python3 scripts/generar-web.py --brief briefs/panel.json
  python3 scripts/generar-web.py --brief briefs/panel.json --dry-run        # sin red
  python3 scripts/generar-web.py --brief briefs/panel.json --sin-modelo     # solo plantilla
  python3 scripts/generar-web.py --brief b.json --arquetipo informe --marca ntizar --tema dark
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPENUI = ROOT / "openui"
CONFIG = pathlib.Path(os.path.expanduser("~/.hermes/config.yaml"))
ENV = pathlib.Path(os.path.expanduser("~/.hermes/.env"))
RE_CERCA = re.compile(r"```(?:openui-lang|openui|text)?\s*\n(.*?)```", re.S)
RE_SENTENCIA = re.compile(r"^\s*[A-Za-z_$][\w$]*\s*=", re.M)


# ---------------------------------------------------------------- módulos del repo
def cargar(nombre, ruta):
    import importlib.util
    spec = importlib.util.spec_from_file_location(nombre, ROOT / "scripts" / ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def leer_config():
    """modelo y endpoint, de config.yaml (sin valores hardcodeados)."""
    texto = CONFIG.read_text(encoding="utf-8")
    modelo = "deepseek-v4-flash"
    m = re.search(r"^model:\s*\n(?:\s+.*\n)*?\s+default:\s*([\w.\-]+)", texto, re.M)
    if m:
        modelo = m.group(1)
    api = "https://api.nan.builders/v1"
    m = re.search(r"^\s{4}api:\s*(\S+)", texto, re.M)
    if m:
        api = m.group(1)
    clave = ""
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8").splitlines():
            if linea.startswith("OPENAI_API_KEY="):
                clave = linea.split("=", 1)[1].strip()
    return {"modelo": modelo, "api": api.rstrip("/"), "clave": clave}


# ---------------------------------------------------------------- modelo
def llamar_modelo(cfg, sistema, usuario, temperatura=0.2, max_tokens=1600, reasoning=None):
    cuerpo = {
        "model": cfg["modelo"],
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
        "temperature": temperatura,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if reasoning:
        cuerpo["reasoning_effort"] = reasoning
    datos = json.dumps(cuerpo).encode("utf-8")
    req = urllib.request.Request(
        cfg["api"] + "/chat/completions", data=datos, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + cfg["clave"],
            # la API de NaN responde 403 sin User-Agent de navegador
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        respuesta = json.loads(r.read().decode("utf-8"))
    texto = respuesta["choices"][0]["message"]["content"]
    uso = respuesta.get("usage", {})
    return texto, uso


def extraer_programa(texto):
    m = RE_CERCA.search(texto)
    candidato = m.group(1) if m else texto
    lineas = [l for l in candidato.splitlines() if RE_SENTENCIA.match(l) or not l.strip()]
    return "\n".join(lineas).strip()


# ---------------------------------------------------------------- validación
def validar(programa, fuente, auditor):
    componentes = {c["nombre"]: c for c in fuente["componentes"]}
    try:
        llamadas, _ = auditor.analizar(programa)
    except ValueError as exc:
        return ["no parsea: %s" % exc]
    problemas = []
    if "root" not in llamadas:
        problemas.append("no define root")
    for nombre, expr in llamadas.items():
        if expr.get("k") != "call":
            continue
        comp = componentes.get(expr["nombre"])
        if not comp:
            problemas.append("«%s» no existe en la biblioteca" % expr["nombre"])
            continue
        if len(expr["args"]) > len(comp["props"]):
            problemas.append("%s recibe %d argumentos y admite %d"
                             % (expr["nombre"], len(expr["args"]), len(comp["props"])))
        for i, prop in enumerate(comp["props"][:len(expr["args"])]):
            mal = auditor.tipar(prop, expr["args"][i])
            if mal:
                problemas.append("%s.%s → %s" % (nombre, prop["nombre"], mal))
    return problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--arquetipo")
    ap.add_argument("--marca")
    ap.add_argument("--tema", default="light", choices=["light", "dark"])
    ap.add_argument("--canal", default="vivo", choices=["vivo", "congelado", "local"])
    ap.add_argument("--modelo")
    ap.add_argument("--salida", "-o", default="dist")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sin-modelo", action="store_true")
    args = ap.parse_args()

    brief = json.loads(pathlib.Path(args.brief).read_text(encoding="utf-8"))
    plantilla_mod = cargar("plantilla", "plantilla.py")
    auditor = cargar("auditar_openui", "auditar-openui.py")
    fuente = json.loads((OPENUI / "componentes.json").read_text(encoding="utf-8"))

    arquetipo = args.arquetipo or brief.get("arquetipo") or "panel-operativo"
    plantillas = {p["nombre"]: p for p in plantilla_mod.cargar_plantillas()}
    if arquetipo not in plantillas:
        print("No existe el arquetipo %r. Disponibles: %s" % (arquetipo, ", ".join(sorted(plantillas))))
        return 2
    plantilla = plantillas[arquetipo]

    valores = {k: v for k, v in brief.items() if isinstance(v, (str, int, float))}
    programa_base = plantilla_mod.sustituir(plantilla, valores)
    marca = args.marca or brief.get("marca") or plantilla.get("marca", "aurora")
    slug = brief.get("salida") or ("%s-%s" % (arquetipo, marca))
    slug = re.sub(r"[^a-z0-9\-]+", "-", slug.lower()).strip("-")

    prompt_sistema = (OPENUI / "PROMPT.md").read_text(encoding="utf-8")
    prompt_sistema += (
        "\n\n## Tu tarea ahora\n\n"
        "Parte de esta plantilla del arquetipo «%s» y ajústala a los datos del encargo. "
        "Puedes añadir o quitar bloques si el encargo lo pide, pero **no cambies los componentes "
        "por otros que no existan** ni el orden de los argumentos. Devuelve SOLO el programa "
        "completo, sin explicaciones ni markdown.\n\nPlantilla:\n```\n%s\n```\n" % (arquetipo, programa_base)
    )
    prompt_usuario = "Encargo:\n" + json.dumps(brief, ensure_ascii=False, indent=1)

    salida = pathlib.Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("arquetipo: %s · marca: %s · tema: %s · canal: %s" % (arquetipo, marca, args.tema, args.canal))
        print("system prompt: %d chars · user: %d chars" % (len(prompt_sistema), len(prompt_usuario)))
        print("plantilla base: %d líneas → %s.openui" % (len(programa_base.splitlines()), slug))
        print("\n--- plantilla con los valores del brief ---\n" + programa_base)
        return 0

    cfg = leer_config()
    if args.modelo:
        cfg["modelo"] = args.modelo
    programa, origen, uso, intentos = programa_base, "plantilla", {}, 0
    problemas = validar(programa_base, fuente, auditor)
    if problemas:
        print("La plantilla con los datos del brief no valida:")
        for p in problemas:
            print("  ✗", p)
        return 1

    if not args.sin_modelo:
        if not cfg["clave"]:
            print("No hay OPENAI_API_KEY en ~/.hermes/.env: no puedo llamar al modelo.")
            print("(usa --sin-modelo para generar la página desde la plantilla)")
            return 2
        print("modelo: %s · %s" % (cfg["modelo"], cfg["api"]))
        sistema = prompt_sistema
        for intento in range(2):
            intentos += 1
            try:
                texto, uso = llamar_modelo(cfg, sistema, prompt_usuario,
                                           reasoning="minimal" if intento == 0 else None)
            except urllib.error.HTTPError as exc:
                detalle = exc.read().decode("utf-8", "replace")[:300]
                print("  ✗ la API respondió %s: %s" % (exc.code, detalle))
                break
            except Exception as exc:  # noqa: BLE001 — red o timeout
                print("  ✗ no se pudo llamar al modelo: %s" % exc)
                break
            candidato = extraer_programa(texto)
            problemas = validar(candidato, fuente, auditor)
            if not problemas:
                programa, origen = candidato, "modelo"
                break
            print("  · intento %d no valida (%d problemas); se reintenta con los errores delante"
                  % (intento + 1, len(problemas)))
            sistema = prompt_sistema + (
                "\n\n## Tu respuesta anterior NO validaba\n\n" +
                "\n".join("- " + p for p in problemas) +
                "\n\nCorrige solo eso y devuelve el programa completo.\n\nTu respuesta era:\n```\n" +
                candidato + "\n```\n"
            )

    if origen == "plantilla" and not args.sin_modelo:
        print("  ! el modelo no produjo un programa válido: se usa la plantilla con los datos del brief")

    ruta_openui = salida / ("%s.openui" % slug)
    ruta_openui.write_text(programa + "\n", encoding="utf-8")

    html = salida / ("%s.html" % slug)
    cmd = [sys.executable, str(ROOT / "scripts" / "programa-a-html.py"), str(ruta_openui),
           "--salida", str(html), "--marca", marca, "--tema", args.tema, "--canal", args.canal,
           "--titulo", brief.get("titulo") or brief.get("encargo", slug)[:60]]
    salida_html = subprocess.run(cmd, capture_output=True, text=True)
    print(salida_html.stdout.strip())
    if salida_html.returncode != 0:
        print(salida_html.stderr.strip())
        return 1

    lint = subprocess.run([sys.executable, str(ROOT / "scripts" / "auditar-uso.py"), str(html)],
                          capture_output=True, text=True)
    resumen_lint = [l for l in lint.stdout.splitlines() if l.strip().startswith("→") or "TOTAL" in l]
    for l in resumen_lint:
        print(l.strip())

    print("\nRECIBO")
    print("  arquetipo   %s" % arquetipo)
    print("  origen      %s%s" % (origen, "" if intentos == 0 else " (%d intento(s))" % intentos))
    if uso:
        print("  tokens      %s entrada · %s salida" % (uso.get("prompt_tokens", "?"), uso.get("completion_tokens", "?")))
    print("  programa    %s (%d líneas)" % (ruta_openui, len(programa.splitlines())))
    print("  página      %s" % html)
    print("  lint        %s" % ("0 fallos" if lint.returncode == 0 else "CON FALLOS — no entregar"))
    return 0 if lint.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
