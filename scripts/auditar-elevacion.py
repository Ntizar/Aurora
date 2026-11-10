#!/usr/bin/env python3
"""Audita la LEY A de elevación (editorial de archivo).

Reglas que comprueba:
  1. tokens: --nz-shadow-xs/sm/md/lg y los glows brand/accent valen `none`;
     existe --nz-shadow-xl y vale algo (es el ÚNICO nivel de elevación).
  2. packs: ninguna sombra proyectada fuera de un overlay. Se admiten
     `none`, `inset ...` (líneas y anillos), `var(--nz-focus-ring*)` y
     `var(--nz-shadow-xl)`/`--nz-shadow-float` solo en selectores que flotan.
Salida: VEREDICTO + lista de infracciones. Exit 1 si hay infracciones.
"""
import re, sys, pathlib

R = pathlib.Path(__file__).resolve().parent.parent

FLOTA = re.compile(
    r"(modal|drawer__panel|sheet__panel|cmd__panel|confirm|offcanvas|popover__body|menu-pop__list|"
    r"menu__drop|dropdown__list|toast|alert--floating|lightbox__(close|nav)|compare-bar|__quick|"
    r"chart-tip|modelpick__list|nz-window|nz-dock|sysnotif|sysdialog|spotlight|tray__menu|"
    r"is-dragging|region-cookies|region-toolbar--flotante|region-chat--sm|nz-fab|menu-cuenta|"
    r"img--shadow|cristal)"
)
MUDOS = ("xs", "sm", "md", "lg", "brand", "accent")

errores, avisos = [], []

tok = (R / "tokens.css").read_text()
for nivel in MUDOS:
    for m in re.finditer(rf"--nz-shadow-{nivel}:\s*([^;]+);", tok):
        if m.group(1).strip() != "none":
            errores.append(f"tokens.css: --nz-shadow-{nivel} debería ser none (es {m.group(1).strip()[:40]})")
if not re.search(r"--nz-shadow-xl:\s*(?!none)", tok):
    errores.append("tokens.css: falta --nz-shadow-xl con valor real (único nivel permitido)")

flotantes = 0
for p in sorted((R / "packs").glob("*.css")):
    if p.name == "p16-cristal.css":
        continue
    for m in re.finditer(r"(?m)^([^\n{}]+)\{([^}]*)\}", p.read_text()):
        sel, body = m.group(1).strip(), m.group(2)
        if sel.startswith("@"):
            continue
        sh = re.search(r"box-shadow:\s*([^;]+);", body)
        if not sh:
            continue
        val = sh.group(1).strip()
        if val == "none" or val.startswith(("inset", "var(--nz-focus-ring")):
            continue
        if re.fullmatch(r"0 0 0 [\d.]+px var\(--nz-[a-z0-9-]+\)(, ?0 0 0 [\d.]+px var\(--nz-[a-z0-9-]+\))?", val):
            avisos.append(f"{p.name}: anillo sin token de anillo sobre {sel} (usa --nz-focus-ring-*)")
            continue
        if re.fullmatch(r"0 1px 0 var\(--nz-[a-z0-9-]+\)", val):
            avisos.append(f"{p.name}: bisel de 1px sobre {sel} (excepción documentada)")
            continue
        if val.startswith(("var(--nz-shadow-xl)", "var(--nz-shadow-float)")):
            if not FLOTA.search(sel):
                errores.append(f"{p.name}: {sel} flota pero no es un overlay")
            else:
                flotantes += 1
            continue
        errores.append(f"{p.name}: {sel} proyecta sombra fuera de la ley ({val[:44]})")

print("LEY A · ELEVACIÓN")
print(f"  niveles de elevación: 1 (--nz-shadow-xl) · usos en overlays: {flotantes}")
print(f"  avisos: {len(avisos)} · infracciones: {len(errores)}")
for a in avisos[:6]:
    print("  ·", a)
for e in errores[:20]:
    print("  ✗", e)
print("\nRESULTADO:", "VÁLIDO ✅" if not errores else "NO VÁLIDO ❌")
sys.exit(0 if not errores else 1)
