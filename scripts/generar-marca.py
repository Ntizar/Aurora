#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurora — generador de marcas (presets de color)
=================================================

Das 1-2 colores (hex) y saca la rampa completa del sistema en OKLCH: pasos de
luminosidad perceptualmente uniformes, croma mapeado a gamut sRGB y validacion de
contraste WCAG. Es la pieza que hace que "elegir 2 colores al principio" cambie
TODO (marca, acento, foco, sombras de color, dark mode) sin tocar una linea a mano.

Uso:
    python scripts/generar-marca.py --todas                  # regenera los presets del registro
    python scripts/generar-marca.py miweb "#0ea5e9" "#f43f5e" # crea marcas/miweb.css

Hecho con ❤️ por David Antizar
"""
from __future__ import annotations
import json
import math
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_MARCAS = RAIZ / "marcas"

# ---- Desplazamiento de luminosidad RELATIVO al color de entrada.
#      La rampa se ancla al color que das: tu hex cae exactamente en el escalon
#      primario (marca->600, acento->500) y el resto se reparte con los mismos
#      saltos de luz que la escala de Tailwind (probada en millones de interfaces).
L = {50: 0.425, 100: 0.390, 200: 0.339, 300: 0.262, 400: 0.158,
     500: 0.077, 600: 0.0, 700: -0.058, 800: -0.122, 900: -0.167}
OFF_MARCA = dict(L)                                             # ancla en 600
OFF_ACENTO = {50: 0.348, 100: 0.313, 200: 0.262, 300: 0.185,
              400: 0.081, 500: 0.0, 600: -0.077, 700: -0.135}   # ancla en 500
ESCALONES = list(OFF_MARCA)

# ---- Presets del sistema: (marca, acento) ----
PRESETS = {
    "aurora":    ("#2563eb", "#f97316"),  # azul + naranja (el clasico)
    "indigo":    ("#4f46e5", "#06b6d4"),  # indigo + cian
    "esmeralda": ("#059669", "#f59e0b"),  # verde + ambar
    "violeta":   ("#7c3aed", "#ec4899"),  # violeta + rosa
    "carmesi":   ("#dc2626", "#0891b2"),  # rojo + cian
}


# ---------------------------------------------------------------- color: sRGB <-> OKLCH
def _srgb_a_lineal(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lineal_a_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_a_rgb(hx: str) -> tuple[int, int, int]:
    hx = hx.strip().lstrip("#")
    if len(hx) == 3:
        hx = "".join(ch * 2 for ch in hx)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", hx):
        raise ValueError(f"hex invalido: {hx!r}")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore


def hex_a_oklch(hx: str) -> tuple[float, float, float]:
    r, g, b = (_srgb_a_lineal(v) for v in hex_a_rgb(hx))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def oklch_a_hex(L: float, C: float, H: float) -> str:
    """OKLCH -> sRGB con mapeo a gamut: baja el croma hasta que entra en [0,1]."""
    a = math.radians(H)
    ca, sa = math.cos(a), math.sin(a)

    def a_lineal(Cv: float) -> tuple[float, float, float]:
        A, B = Cv * ca, Cv * sa
        l_ = L + 0.3963377774 * A + 0.2158037573 * B
        m_ = L - 0.1055613458 * A - 0.0638541728 * B
        s_ = L - 0.0894841775 * A - 1.2914855480 * B
        l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
        return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

    lo, hi = 0.0, C
    for _ in range(34):
        mid = (lo + hi) / 2
        if all(-1e-4 <= v <= 1 + 1e-4 for v in a_lineal(mid)):
            lo = mid
        else:
            hi = mid
    r, g, b = a_lineal(lo)
    return "#%02x%02x%02x" % tuple(round(_lineal_a_srgb(v) * 255) for v in (r, g, b))


# ---------------------------------------------------------------- contraste WCAG
def _luminancia(hx: str) -> float:
    r, g, b = (_srgb_a_lineal(v) for v in hex_a_rgb(hx))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    l1, l2 = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# ---------------------------------------------------------------- rampa
def luz_de(luz_fuente: float, off: float) -> float:
    """Luz destino de un paso, comprimida al espacio real disponible.

    Sin esto, un color claro (naranja, L≈0.70) topa en el techo y sus pasos 50/100
    salen **identicos**; y un color oscuro machaca el suelo. Se reparte el offset
    en la habitacion que hay por encima/debajo, tomando el azul-600 (L=0.546) como
    referencia de escala 1.0.
    """
    REF, TECHO, SUELO = 0.546, 0.97, 0.10
    if off > 0:
        escala = min(1.0, max(0.05, TECHO - luz_fuente) / (TECHO - REF))
    elif off < 0:
        escala = max(0.05, luz_fuente - SUELO) / (REF - SUELO)
    else:
        return luz_fuente
    return min(TECHO, max(SUELO, luz_fuente + off * escala))


def rampa(hex_base: str, offsets: dict[int, float], ancla: int) -> dict[int, str]:
    """Rampa a partir de UN color, anclada al escalon primario.

    - **Ancla:** `hex_base` cae EXACTAMENTE en el escalon `ancla` (marca→600,
      acento→500). Tu color es el primario, no una aproximacion generada.
    - **Taper de croma:** en los pasos alejados se baja el croma, que es lo que
      hace que una rampa se vea natural y no "chillona" en los extremos.
    """
    luz_fuente, croma_fuente, tono = hex_a_oklch(hex_base)
    orden = list(offsets)                       # [50, 100, … 900] en orden
    i_ancla = orden.index(ancla)
    salida: dict[int, str] = {}
    for i, (paso, off) in enumerate(offsets.items()):
        if paso == ancla:
            salida[paso] = hex_base.lower()
            continue
        d = abs(i - i_ancla)                    # distancia en POSICION, no en etiqueta
        croma = croma_fuente * (1.0 if d <= 1 else 0.85 if d == 2 else
                                0.62 if d == 3 else 0.4)
        salida[paso] = oklch_a_hex(luz_de(luz_fuente, off), croma, tono)
    return salida


def verificar_tokens(datos_aurora: dict) -> bool:
    """Los defaults de tokens.css deben ser EXACTAMENTE la marca aurora (fuente unica)."""
    ruta = RAIZ / "tokens.css"
    if not ruta.exists():
        return True
    css = ruta.read_text(encoding="utf-8")
    fallos = []
    for rama, clave in (("marca_rampa", "--nz-marca-"), ("acento_rampa", "--nz-acento-")):
        for paso, valor in datos_aurora[rama].items():
            m = re.search(rf"{clave}{paso}\s*:\s*(#[0-9a-fA-F]{{6}})", css)
            if not m:
                fallos.append(f"tokens.css no define {clave}{paso}")
            elif m.group(1).lower() != valor.lower():
                fallos.append(f"{clave}{paso}: tokens.css={m.group(1)} ≠ aurora={valor}")
    if fallos:
        print("\n⚠️  tokens.css y la marca «aurora» no coinciden:")
        for f in fallos[:12]:
            print("   -", f)
        return False
    print("   tokens.css ≡ marca «aurora» ✅")
    return True


def bloque_css(nombre: str, marca: str, acento: str) -> tuple[str, dict]:
    rm = rampa(marca, OFF_MARCA, 600)
    ra = rampa(acento, OFF_ACENTO, 500)
    lineas = [f"[data-nz-marca=\"{nombre}\"] {{"]
    lineas.append("  /* rampa de marca (primario) */")
    lineas += [f"  --nz-marca-{k}: {v};" for k, v in rm.items()]
    lineas.append("  /* rampa de acento (secundario) */")
    lineas += [f"  --nz-acento-{k}: {v};" for k, v in ra.items()]
    lineas.append("}")
    css = "\n".join(lineas) + "\n"
    datos = {"nombre": nombre, "marca": marca, "acento": acento,
             "marca_rampa": {str(k): v for k, v in rm.items()},
             "acento_rampa": {str(k): v for k, v in ra.items()}}
    return css, datos


def ajustar_aa(hex_base: str, objetivo: float = 4.5, contra: str = "#ffffff") -> tuple[str, float, bool]:
    """Si el color no llega a AA contra `contra`, lo oscurece lo justo y lo avisa.

    Es la diferencia entre un sistema "bonito" y uno **usable**: un boton con texto
    blanco que no llega a 4.5:1 es un fallo de accesibilidad, no un detalle estetico.
    """
    if contraste(hex_base, contra) >= objetivo:
        return hex_base, contraste(hex_base, contra), False
    luz, croma, tono = hex_a_oklch(hex_base)
    for _ in range(90):
        luz -= 0.004
        if luz < 0.15:
            break
        cand = oklch_a_hex(luz, croma, tono)
        if contraste(cand, contra) >= objetivo:
            return cand, contraste(cand, contra), True
    return hex_base, contraste(hex_base, contra), False


def informe_contraste(nombre: str, datos: dict) -> tuple[list[str], bool]:
    rm, ra = datos["marca_rampa"], datos["acento_rampa"]
    filas, ok = [], True
    BLANCO, TINTA = "#ffffff", "#111827"

    def check(etiqueta: str, c: float, objetivo: float = 4.5) -> None:
        nonlocal ok
        bien = c >= objetivo
        ok &= bien
        filas.append(f"   {etiqueta}: {c:5.2f}  {'✅' if bien else '❌'} (AA ≥ {objetivo})")

    # Texto blanco sobre la marca solida (boton primario) y sobre su strong.
    check("blanco sobre marca-600", contraste(rm["600"], BLANCO))
    check("blanco sobre marca-700", contraste(rm["700"], BLANCO))
    # Texto oscuro sobre el acento y sobre sus fondos suaves (nunca blanco: el
    # acento es claro por diseno; el texto va en tinta).
    check("tinta sobre acento-500", contraste(ra["500"], TINTA))
    check("tinta sobre acento-100", contraste(ra["100"], TINTA))
    check("tinta sobre marca-100", contraste(rm["100"], TINTA))
    return filas, ok


def generar(nombre: str, marca: str, acento: str, verboso: bool = True) -> dict:
    marca_original = marca.lower()
    marca_ajustada, contraste_marca, ajustada = ajustar_aa(marca)
    css, datos = bloque_css(nombre, marca_ajustada, acento)
    datos["marca_original"] = marca_original
    datos["marca_ajustada_aa"] = ajustada
    datos["contraste_marca_600"] = round(contraste_marca, 2)
    aviso = (f"   (marca ajustada de {marca_original} a {marca_ajustada} para cumplir AA)"
             if ajustada else "")
    cabecera = (
        f"/* Aurora · marca «{nombre}» — generado por scripts/generar-marca.py\n"
        f"   marca {marca_ajustada} · acento {acento} · rampas OKLCH de luz uniforme\n"
        f"   {aviso.strip() or 'marca y acento tal cual se pidieron'}\n"
        f"   Activa con: <html data-nz-marca=\"{nombre}\">\n"
        f"   Hecho con ❤️ por David Antizar */\n\n"
    )
    DIR_MARCAS.mkdir(exist_ok=True)
    (DIR_MARCAS / f"{nombre}.css").write_text(cabecera + css, encoding="utf-8")
    filas, ok = informe_contraste(nombre, datos)
    datos["contraste_ok"] = ok
    if verboso:
        print(f"\n■ {nombre}  (marca {marca_ajustada} · acento {acento})  → marcas/{nombre}.css")
        if ajustada:
            print(f"   ⚠️  marca ajustada para AA: {marca_original} → {marca_ajustada}")
        for f in filas:
            print(f)
    return datos


def main(argv: list[str]) -> int:
    if "--todas" in argv:
        registro = [generar(n, m, a) for n, (m, a) in PRESETS.items()]
        (DIR_MARCAS / "registro.json").write_text(
            json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        fallos = [r["nombre"] for r in registro if not r["contraste_ok"]]
        print(f"\n{len(registro)} marcas generadas · registro: marcas/registro.json")
        ok_tokens = verificar_tokens(next(r for r in registro if r["nombre"] == "aurora"))
        if fallos:
            print(f"⚠️  contraste insuficiente en: {', '.join(fallos)}")
        if fallos or not ok_tokens:
            return 1
        print("RESULTADO: VÁLIDO — todas las marcas pasan contraste AA ✅")
        return 0

    args = [a for a in argv if not a.startswith("-")]
    if len(args) == 3:
        d = generar(args[0], args[1], args[2])
        return 0 if d["contraste_ok"] else 1

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
