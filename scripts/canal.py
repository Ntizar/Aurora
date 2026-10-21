# -*- coding: utf-8 -*-
"""Canales de Aurora: qué versión come cada web y cómo se comprueba.

Dos canales, un solo sistema:

  · vivo      → `@v9` (rango de major). Se mueve con cada release 9.x.
                Para webs y paneles propios: un cambio en Aurora llega solo.
  · congelado → `@v9.5.0` (tag exacto). Entregas a cliente: reproducible.

Un tag publicado es **inmutable**: nunca se reescribe ni se mueve. Lo que cambia es a
dónde apunta el rango, no el tag.

Uso:
  python3 scripts/canal.py                     # estado de los dos canales
  python3 scripts/canal.py --tag               # solo el tag exacto del canal vivo
  python3 scripts/canal.py --check             # puerta de CI (offline)
  python3 scripts/canal.py --lock aurora.lock  # escribe el lock de una web
  python3 scripts/canal.py --verificar aurora.lock
  python3 scripts/canal.py --check --online    # además, comprueba el CDN (red)
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANALES = ROOT / "data" / "canales.json"


def leer_canales():
    return json.loads(CANALES.read_text(encoding="utf-8"))


def tags_locales():
    r = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=ROOT,
                       capture_output=True, text=True)
    ultimo = r.stdout.strip() if r.returncode == 0 else ""
    r = subprocess.run(["git", "tag", "--list", "v*"], cwd=ROOT,
                       capture_output=True, text=True)
    todos = [t.strip() for t in r.stdout.splitlines() if t.strip()]
    return ultimo, todos


def version_de(tag):
    return tag.lstrip("v").split("-")[0]


def major(tag):
    return version_de(tag).split(".")[0]


def resolver_vivo(canales, tags, ultimo):
    """El rango (v9) resuelve al tag más alto que case con él."""
    rango = canales["canales"]["vivo"]["rango"].lstrip("v")
    candidatos = []
    for t in tags:
        if t.startswith("v" + rango + "."):
            partes = version_de(t).split(".")
            if all(p.isdigit() for p in partes[:3]):
                candidatos.append(tuple(int(p) for p in partes[:3]) + (t,))
    if not candidatos:
        return None
    return max(candidatos)[-1]


def cdn_ok(ref, fichero="tokens.css"):
    url = "https://cdn.jsdelivr.net/gh/Ntizar/Aurora@%s/%s" % (ref, fichero)
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200, url
    except Exception as exc:  # noqa: BLE001 — red caída o 404, da igual el motivo
        return False, "%s (%s)" % (url, exc)


def estado():
    canales = leer_canales()
    ultimo, tags = tags_locales()
    vivo = canales["canales"]["vivo"]
    cong = canales["canales"]["congelado"]
    resuelto = resolver_vivo(canales, tags, ultimo)
    return {
        "registro": canales,
        "ultimo_tag": ultimo,
        "vivo_rango": vivo["rango"],
        "vivo_resuelto": resuelto,
        "congelado": cong["tag"],
        "version_spec": json.loads((ROOT / "openui" / "aurora.spec.json").read_text(encoding="utf-8"))["version"]
        if (ROOT / "openui" / "aurora.spec.json").exists() else None,
    }


def check(online=False):
    fallos, avisos = [], []
    e = estado()
    if not e["ultimo_tag"]:
        fallos.append("git no tiene tags: no hay canal que resolver")
    if not e["vivo_resuelto"]:
        fallos.append("el rango %s no casa con ningún tag publicado" % e["vivo_rango"])
    elif e["vivo_resuelto"] != e["ultimo_tag"]:
        fallos.append("el canal vivo resuelve %s pero el último tag es %s: el rango se quedó atrás"
                      % (e["vivo_resuelto"], e["ultimo_tag"]))
    if e["congelado"] != e["ultimo_tag"]:
        fallos.append("el canal congelado apunta a %s y el último tag es %s (actualízalo a propósito)"
                      % (e["congelado"], e["ultimo_tag"]))
    if major(e["ultimo_tag"]) != e["vivo_rango"].lstrip("v"):
        fallos.append("el rango vivo (v%s) no cubre el major del último tag (%s)"
                      % (e["vivo_rango"], e["ultimo_tag"]))
    if online:
        for ref in (e["vivo_rango"], e["congelado"]):
            ok, url = cdn_ok(ref)
            if not ok:
                fallos.append("el CDN no sirve @%s: %s" % (ref, url))
    return {"estado": e, "fallos": fallos, "avisos": avisos}


def lock(ruta):
    e = estado()
    datos = {
        "canal": "vivo",
        "rango": e["vivo_rango"],
        "resuelto": e["vivo_resuelto"],
        "spec": e["version_spec"],
        "generado": datetime.date.today().isoformat(),
    }
    pathlib.Path(ruta).write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("lock escrito en %s → %s (canal %s)" % (ruta, datos["resuelto"], datos["rango"]))
    return 0


def verificar_lock(ruta):
    fallos = []
    datos = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    e = estado()
    for clave in ("canal", "rango", "resuelto", "spec"):
        if clave not in datos:
            fallos.append("el lock no declara «%s»" % clave)
    if datos.get("canal") == "vivo":
        if datos.get("rango") != e["vivo_rango"]:
            fallos.append("el lock usa el rango %s y el canal vivo es %s"
                          % (datos.get("rango"), e["vivo_rango"]))
        if major(datos.get("resuelto", "v0.0.0")) != e["vivo_rango"].lstrip("v"):
            fallos.append("el tag del lock (%s) no pertenece al major del canal (%s)"
                          % (datos.get("resuelto"), e["vivo_rango"]))
    if datos.get("spec") and e["version_spec"] and datos["spec"] != e["version_spec"]:
        fallos.append("el lock declara spec %s y la spec es %s: revisa si el programa es compatible"
                      % (datos["spec"], e["version_spec"]))
    for f in fallos:
        print("  ✗", f)
    print("RESULTADO:", "VÁLIDO" if not fallos else "%d FALLOS" % len(fallos))
    return 1 if fallos else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="imprime el tag exacto del canal vivo")
    ap.add_argument("--check", action="store_true", help="puerta de CI")
    ap.add_argument("--online", action="store_true", help="comprueba también el CDN")
    ap.add_argument("--lock", metavar="RUTA", help="escribe un lock con la versión resuelta")
    ap.add_argument("--verificar", metavar="RUTA", help="verifica un lock existente")
    args = ap.parse_args()

    if args.tag:
        e = estado()
        print(e["vivo_resuelto"] or "")
        return 0 if e["vivo_resuelto"] else 1
    if args.lock:
        return lock(args.lock)
    if args.verificar:
        return verificar_lock(args.verificar)
    if args.check:
        r = check(online=args.online)
        e = r["estado"]
        print("canales · vivo @%s → %s · congelado @%s · spec %s"
              % (e["vivo_rango"], e["vivo_resuelto"], e["congelado"], e["version_spec"]))
        for f in r["fallos"]:
            print("  ✗", f)
        for a in r["avisos"]:
            print("  · ", a)
        print("RESULTADO:", "VÁLIDO" if not r["fallos"] else "%d FALLOS" % len(r["fallos"]))
        return 1 if r["fallos"] else 0

    e = estado()
    print("Aurora · canales")
    print("  vivo      @%-6s → %s   (webs propias)" % (e["vivo_rango"], e["vivo_resuelto"]))
    print("  congelado @%-6s   (entregas a cliente)" % e["congelado"])
    print("  último tag: %s · spec %s" % (e["ultimo_tag"], e["version_spec"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
