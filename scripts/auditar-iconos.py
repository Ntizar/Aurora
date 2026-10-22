#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita el repositorio de iconos numerados de Aurora.

Un repositorio de iconos se corrompe en silencio: un número repetido, un SVG sin
ficha, una ficha sin SVG, un color a mano que rompe el tema oscuro o un catálogo
editado a mano que ya no cuenta lo que hay. Esto lo comprueba mecánicamente.

Uso:
  python3 scripts/auditar-iconos.py            # informe + código 1 si hay fallos
  python3 scripts/auditar-iconos.py --check    # además exige salidas regeneradas

Lo que se comprueba:
  1. manifiesto legible, con licencia y convención
  2. numeración: única, correlativa y sin huecos salvo retirados declarados
  3. cada icono activo tiene su fichero `NNN-nombre.svg` y el nombre del fichero cuadra
  4. cada .svg de iconos/ tiene su ficha (nada suelto, nada huérfano)
  5. el SVG es del sistema: viewBox 24×24, fill=none, stroke=currentColor, sin color a mano
  6. nombre castellano (no deja el id de Lucide sin traducir, salvo marcas)
  7. el hash del manifiesto coincide con el fichero (deriva = fallo)
  8. sprite.svg: un símbolo por icono activo, ids únicos y sin sobrantes
  9. index.html: una ficha por icono, ni una más ni una menos
 10. salidas regeneradas (con --check): sprite e índice son lo que genera el script
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "iconos"
MANIFIESTO = DIR / "iconos.json"
SPRITE = DIR / "sprite.svg"
CATALOGO = DIR / "index.html"

# Palabras que en castellano se escriben igual que en inglés: no son una fuga
# de idioma, son préstamos asentados. Cualquier otra coincidencia es un fallo.
PRESTAMOS = {"menu", "kanban", "video", "radio", "terminal", "wifi", "bluetooth",
             "bot", "webhook", "podcast", "email"}

fallos: list[str] = []
avisos: list[str] = []


def fallo(t: str) -> None:
    fallos.append(t)


def aviso(t: str) -> None:
    avisos.append(t)


def cuerpo_de(svg: str) -> str:
    m = re.search(r">\s*(?:<!--.*?-->\s*)?(.*)</svg>", svg, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main(argv) -> int:
    if not MANIFIESTO.exists():
        print("FALLO falta iconos/iconos.json: ejecuta python3 scripts/iconos.py sembrar")
        return 1
    m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))

    # 1. estructura del manifiesto
    for clave in ("coleccion", "fuente", "licencia", "convencion", "total", "siguiente", "iconos"):
        if clave not in m:
            fallo(f"manifiesto sin «{clave}»")
    lic = m.get("licencia", {})
    for clave in ("spdx", "url", "atribucion"):
        if not lic.get(clave):
            fallo(f"licencia sin «{clave}»: sin atribución no se puede servir el icono")
    if m.get("convencion", {}).get("prefijo") != "nz-i-":
        fallo("la convención debe usar el prefijo nz-i-")

    iconos = m.get("iconos", [])
    activos = [i for i in iconos if i.get("estado", "activo") == "activo"]
    retirados = [i for i in iconos if i.get("estado") == "retirado"]

    # 2. numeración
    numeros = [i["numero"] for i in iconos]
    if len(numeros) != len(set(numeros)):
        repetidos = sorted({n for n in numeros if numeros.count(n) > 1})
        fallo(f"números repetidos: {repetidos} — un número no se reutiliza nunca")
    if numeros and sorted(numeros) != list(range(1, max(numeros) + 1)):
        huecos = sorted(set(range(1, max(numeros) + 1)) - set(numeros))
        fallo(f"huecos no declarados en la numeración: {huecos}")
    esperado_siguiente = (max(numeros) if numeros else 0) + 1
    if m.get("siguiente") != esperado_siguiente:
        fallo(f"«siguiente»={m.get('siguiente')} pero toca {esperado_siguiente}")
    if m.get("total") != len(activos):
        fallo(f"«total»={m.get('total')} pero hay {len(activos)} activos")

    ids = [i["id"] for i in iconos]
    if len(ids) != len(set(ids)):
        fallo("ids repetidos en el manifiesto")

    lucides = [i["lucide"] for i in activos]
    dup_lucide = sorted({x for x in lucides if lucides.count(x) > 1})
    if dup_lucide:
        fallo(f"el mismo icono de Lucide entra dos veces: {dup_lucide}")

    # 3 y 5. fichas ↔ ficheros, higiene del SVG
    en_disco = {p.name for p in DIR.glob("*.svg")} - {"sprite.svg"}
    for i in activos:
        archivo = i.get("archivo") or ""
        if not archivo:
            fallo(f"{i['id']}: ficha sin archivo")
            continue
        ruta = DIR / archivo
        if not ruta.exists():
            fallo(f"{i['id']}: falta el fichero {archivo}")
            continue
        esperado = f"{i['numero']:03d}-{i['nombre']}.svg"
        if archivo != esperado:
            fallo(f"{i['id']}: el fichero debería llamarse {esperado}, no {archivo}")
        if not i.get("licencia"):
            fallo(f"{i['id']}: ficha sin licencia")
        if not archivo.startswith(f"{i['numero']:03d}-"):
            fallo(f"{i['id']}: el prefijo del fichero no es su número")

        texto = ruta.read_text(encoding="utf-8")
        cabecera = texto.split(">", 1)[0]
        if 'viewBox="0 0 24 24"' not in cabecera:
            fallo(f"{archivo}: sin viewBox 0 0 24 24")
        if 'stroke="currentColor"' not in cabecera or 'fill="none"' not in cabecera:
            fallo(f"{archivo}: el trazo debe ser currentColor y el relleno none")
        if re.search(r'#[0-9a-fA-F]{3,8}', texto):
            fallo(f"{archivo}: color a mano (un icono hereda el color del texto)")
        if "stroke-width=\"2\"" in texto:
            fallo(f"{archivo}: grosor fijo de Lucide; el grosor lo pone --nz-icon-stroke")
        if "<text" in texto:
            fallo(f"{archivo}: lleva texto dentro; no es un icono")
        if re.search(r"<svg[^>]*\bwidth=\"\d+px\"", texto):
            fallo(f"{archivo}: tamaño en píxeles de diseño")
        if 'data-icono="' not in cabecera:
            fallo(f"{archivo}: sin data-icono (el número debe ir en el fichero)")

        cuerpo = cuerpo_de(texto)
        import hashlib
        h = "sha256:" + hashlib.sha256(cuerpo.encode("utf-8")).hexdigest()[:16]
        if i.get("hash") and i["hash"] != h:
            fallo(f"{archivo}: el fichero cambió y el manifiesto no (hash distinto)")

        # 6. nombre castellano
        if (i.get("grupo") != "marcas" and i["nombre"] == i["lucide"]
                and i["nombre"] not in PRESTAMOS):
            fallo(f"{i['id']}: el nombre sigue en inglés ({i['lucide']})")

    # 4. nada huérfano
    referenciados = {i["archivo"] for i in activos if i.get("archivo")}
    huerfanos = sorted(en_disco - referenciados)
    if huerfanos:
        fallo(f"{len(huerfanos)} SVG sin ficha: {huerfanos[:5]}{' …' if len(huerfanos) > 5 else ''}")

    # 8. sprite
    if not SPRITE.exists():
        fallo("falta iconos/sprite.svg: ejecuta python3 scripts/iconos.py sprite")
    else:
        txt = SPRITE.read_text(encoding="utf-8")
        symbol_ids = re.findall(r'<symbol id="([^"]+)"', txt)
        if len(symbol_ids) != len(activos):
            fallo(f"sprite con {len(symbol_ids)} símbolos y {len(activos)} iconos activos")
        repetidos = sorted({s for s in symbol_ids if symbol_ids.count(s) > 1})
        if repetidos:
            fallo(f"ids repetidos en el sprite: {repetidos}")
        faltan = {i["id"] for i in activos} - set(symbol_ids)
        if faltan:
            fallo(f"iconos sin símbolo en el sprite: {sorted(faltan)[:5]}")
        for i in activos:
            mm = re.search(rf'<symbol id="{re.escape(i["id"])}"[^>]*>(.*?)</symbol>', txt, re.S)
            if mm and re.sub(r"\s+", " ", mm.group(1)).strip() != cuerpo_de(
                    (DIR / i["archivo"]).read_text(encoding="utf-8")):
                fallo(f"{i['id']}: el símbolo del sprite no coincide con el fichero")

    # 9. catálogo
    if not CATALOGO.exists():
        fallo("falta iconos/index.html: ejecuta python3 scripts/iconos.py catalogo")
    else:
        html = CATALOGO.read_text(encoding="utf-8")
        fichas = re.findall(r'data-icono="(nz-i-\d+)"', html)
        if len(fichas) != len(activos):
            fallo(f"el catálogo enseña {len(fichas)} fichas y hay {len(activos)} iconos activos")
        faltan = {i["id"] for i in activos} - set(fichas)
        if faltan:
            fallo(f"iconos fuera del catálogo: {sorted(faltan)[:5]}")
        if "Hecho con ❤️ por David Antizar" not in html:
            fallo("el catálogo perdió la atribución")
        if 'data-nz-theme=' not in html.split(">", 2)[0] + html[:400]:
            aviso("el catálogo no declara data-nz-theme en <html>")

    # 10. salidas regeneradas
    if "--check" in argv:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "iconos.py"), "--check"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            for linea in (r.stdout + r.stderr).strip().splitlines():
                if linea.strip():
                    fallo(linea.strip())

    print(f"== iconos numerados · {len(activos)} activos · {len(retirados)} retirados · "
          f"grupos {len({i['grupo'] for i in activos})}")
    for a in avisos:
        print(f"  · aviso: {a}")
    for f in fallos:
        print(f"  ✗ {f}")
    if fallos:
        print(f"\nRESULTADO: {len(fallos)} FALLOS")
        return 1
    print("\nRESULTADO: VÁLIDO — numeración, ficheros, sprite y catálogo en orden")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
