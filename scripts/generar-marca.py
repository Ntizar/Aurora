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
    python scripts/generar-marca.py --mono monocromo         # marca monocroma (escala de grises)

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

# ---- Marca monocroma: escaleras acromaticas FIJAS. No salen de un hex ancla:
#      luz_de() comprime el reparto alrededor del ancla y una tinta oscura
#      (#111) no llega nunca a los grises claros. Tinta = estructura (botones,
#      enlaces), resalte = el dato que importa (el momento blanco/negro de un
#      panel ZeroLeaks). Grises tipo Tailwind neutral, sin croma.
MONO_MARCA = {"50": "#fafafa", "100": "#f0f0f0", "200": "#e0e0e0", "300": "#c2c2c2",
              "400": "#969696", "500": "#5c5c5c", "600": "#111111", "700": "#0b0b0b",
              "800": "#070707", "900": "#040404"}
MONO_ACENTO = {"50": "#f5f5f5", "100": "#e5e5e5", "200": "#c9c9c9", "300": "#c4c4c4",
               "400": "#ababab", "500": "#a3a3a3", "600": "#5c5c5c", "700": "#454545"}
# Estados en grises: la jerarquia la da la luminancia (critico = mas oscuro en
# claro; en oscuro el peligro se INVERTE a blanco, el chip ZeroLeaks). Los
# softs/tints acompanan a cada tono para que badges/alertas sigan legibles y
# cada estado con su par AA comprobado (medido: 5.97 a 15.57:1).
MONO_SEMANTICOS = {
    "claro": {"success": "#444444", "success-soft": "#ececec", "success-tint": "#dcdcdc",
              "danger": "#0a0a0a", "danger-soft": "#e4e4e4", "danger-tint": "#d4d4d4",
              "warning": "#5c5c5c", "warning-soft": "#f2f2f2", "warning-tint": "#e2e2e2"},
    "oscuro": {"success": "#d9d9d9", "success-soft": "#2b2b2b", "success-tint": "#383838",
               "danger": "#ffffff", "danger-soft": "#2e2e2e", "danger-tint": "#3a3a3a",
               "warning": "#b5b5b5", "warning-soft": "#262626", "warning-tint": "#333333"},
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
    # Garantia AA del par texto-acento s/ fondo-acento-suave (700 sobre 50):
    # con tonos muy claros el escalon 700 puede quedarse corto (medido: esmeralda
    # 3.82, indigo 4.13). Se oscurece lo justo manteniendo matiz y croma; los
    # presets nunca se retocan a mano.
    if contraste(ra[700], ra[50]) < 4.5:
        luz, croma, tono = hex_a_oklch(ra[700])
        for _ in range(90):
            luz -= 0.004
            if luz < 0.25:
                break
            cand = oklch_a_hex(luz, croma, tono)
            ra[700] = cand
            if contraste(cand, ra[50]) >= 4.5:
                break
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
    check("acento-700 sobre acento-50", contraste(ra["700"], ra["50"]))
    return filas, ok


def generar_mono(nombre: str, verboso: bool = True) -> dict:
    """Marca monocroma: escaleras fijas + estados grises en claro y oscuro.

    El informe de contraste es el MISMO que el de las marcas cromáticas
    (informe_contraste): con estas escaleras todos los pares pasan AA.
    """
    lineas = [
        f"/* Aurora · marca «{nombre}» — monocroma, generada por scripts/generar-marca.py --mono",
        f"   tinta {MONO_MARCA['600']} (estructura) · resalte {MONO_ACENTO['500']} (el dato que importa)",
        "   Estados (success/danger/warning) en escala de grises: la jerarquia la da la",
        "   luminancia y en oscuro el peligro se INVERTE a blanco (chip ZeroLeaks).",
        f"   Activa con: <html data-nz-marca=\"{nombre}\">",
        "   Hecho con ❤️ por David Antizar */",
        "",
        f"[data-nz-marca=\"{nombre}\"] {{",
        "  /* rampa de marca (tinta) */",
    ]
    lineas += [f"  --nz-marca-{k}: {v};" for k, v in MONO_MARCA.items()]
    lineas.append("  /* rampa de acento (resalte) */")
    lineas += [f"  --nz-acento-{k}: {v};" for k, v in MONO_ACENTO.items()]
    lineas.append("  /* estados en grises (claro) */")
    lineas += [f"  --nz-{k}: {v};" for k, v in MONO_SEMANTICOS["claro"].items()]
    lineas.append("}")
    lineas.append("")
    lineas.append(f"[data-nz-theme=\"dark\"][data-nz-marca=\"{nombre}\"] {{")
    lineas.append("  /* estados en grises (oscuro): el peligro se invierte a blanco */")
    lineas += [f"  --nz-{k}: {v};" for k, v in MONO_SEMANTICOS["oscuro"].items()]
    lineas.append("}")
    (DIR_MARCAS / f"{nombre}.css").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    datos = {"nombre": nombre, "marca": MONO_MARCA["600"], "acento": MONO_ACENTO["500"],
             "marca_rampa": dict(MONO_MARCA), "acento_rampa": dict(MONO_ACENTO),
             "marca_original": MONO_MARCA["600"], "marca_ajustada_aa": False,
             "contraste_marca_600": round(contraste(MONO_MARCA["600"], "#ffffff"), 2)}
    filas, ok = informe_contraste(nombre, datos)
    datos["contraste_ok"] = ok
    if verboso:
        print(f"\n■ {nombre}  (monocroma · tinta {MONO_MARCA['600']} · resalte {MONO_ACENTO['500']})  → marcas/{nombre}.css")
        for f in filas:
            print(f)
    return datos


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
        # Las marcas fuera de PRESETS (ntizar, monocromo, ...) NO se pierden:
        # --todas regenera los presets y preserva las registradas a mano.
        ruta_registro = DIR_MARCAS / "registro.json"
        previas = json.loads(ruta_registro.read_text(encoding="utf-8")) if ruta_registro.exists() else []
        preset_nombres = {r["nombre"] for r in registro}
        registro += [e for e in previas if e.get("nombre") not in preset_nombres]
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

    if "--mono" in argv:
        args = [a for a in argv if not a.startswith("-")]
        if len(args) != 1:
            print("Uso: python scripts/generar-marca.py --mono <nombre>")
            return 2
        d = generar_mono(args[0])
        # Registrar en registro.json (añade o reemplaza la entrada de este nombre).
        ruta = DIR_MARCAS / "registro.json"
        lista = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []
        lista = [e for e in lista if e.get("nombre") != d["nombre"]]
        lista.append(d)
        ruta.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if d["contraste_ok"] else 1

    args = [a for a in argv if not a.startswith("-")]
    if len(args) == 3:
        d = generar(args[0], args[1], args[2])
        # Registrar en registro.json (añade o reemplaza la entrada de este nombre):
        # una marca que existe en marcas/ pero no en el registro se pierde con --todas.
        ruta = DIR_MARCAS / "registro.json"
        lista = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []
        lista = [e for e in lista if e.get("nombre") != d["nombre"]]
        lista.append(d)
        ruta.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if d["contraste_ok"] else 1

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
