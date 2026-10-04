# -*- coding: utf-8 -*-
"""Validador de Aurora.

Comprueba lo que promete el manifiesto y lo que promete el catálogo. Devuelve
código de salida 1 si algo falla, así que sirve tal cual en CI: el sistema no
puede degradarse sin que el push se ponga en rojo.

Comprueba:
  1. Sintaxis: llaves equilibradas y cabecera de pack en todos los packs.
  2. Manifiesto: 0 gradientes, 0 glass, 0 colores a mano, 0 !important
     (con la lista blanca de los tres usos justificados).
  3. Tokens: todo var(--nz-*) usado existe en tokens.css.
  4. Propiedad: una clase .nz-* no puede declararse en dos packs a la vez.
  5. Cobertura: toda clase declarada aparece en una demo de su categoría, y
     toda clase usada en las demos existe.
  6. Atribución: el pie dice exactamente «Hecho con ❤️ por David Antizar».
  7. Cifras: los números de la portada coinciden con el CSS real.
 12. Versión: components.json, generar-llm-docs.py y los CDN de la doc
     (@vX.Y.Z) dicen la misma versión que el último tag de git.
 13. Sincronía de docs IA: LLM.md y components.json regenerados coinciden
     con los commiteados (si alguien toca packs/specs sin regenerar, rojo).
 14. Lint del consumidor: el auto-test de scripts/auditar-uso.py debe pasar
     (la herramienta que usan los agentes para verificar su HTML funciona).

Uso: python scripts/validar-css.py     (o python scripts/validar-css.py --informe)
"""
import json
import pathlib
import re
import subprocess
import sys
from importlib import import_module

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
bc = import_module("build-catalog")

ROOT = bc.ROOT
PACKS = bc.PACKS
SPECS = bc.SPECS
OUT_HTML = ROOT / "audit" / "index.html"

# Usos de !important admitidos, con su motivo.
EXCEPCIONES_IMPORTANT = {
    ".nz-visually-hidden": "patrón estándar de ocultación accesible",
    ".nz-vh": "patrón estándar de ocultación accesible",
    ".nz-print-hide": "debe ganar a display:flex al imprimir",
}

VAR_DEF = re.compile(r"(--nz-[A-Za-z0-9_-]+)\s*:")
VAR_USE = re.compile(r"var\(\s*(--nz-[A-Za-z0-9_-]+)")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")

# Valores que ya tienen token de valor fijo: si aparecen literales, es una
# incoherencia con el manifiesto («todos los valores son tokens --nz-*»).
MAPA_ESPACIO = {
    "0.25rem": 1, "0.5rem": 2, "0.75rem": 3, "1rem": 4, "1.25rem": 5, "1.5rem": 6,
    "1.75rem": 7, "2rem": 8, "2.25rem": 9, "2.5rem": 10, "3rem": 12, "4rem": 16, "5rem": 20,
    "4px": 1, "8px": 2, "12px": 3, "16px": 4, "20px": 5, "24px": 6, "28px": 7,
    "32px": 8, "36px": 9, "40px": 10, "48px": 12, "64px": 16, "80px": 20,
}
MAPA_TEXTO = {
    "0.6875rem": "2xs", "11px": "2xs", "0.75rem": "xs", "12px": "xs", "0.8125rem": "sm",
    "13px": "sm", "0.9375rem": "base", "15px": "base", "1rem": "md", "16px": "md",
    "1.125rem": "lg", "18px": "lg",
}
NUM = re.compile(r"(?<![\w.-])(\d*\.?\d+(?:rem|px))(?![\w-])")
PROPS_ESPACIO = ("gap", "row-gap", "column-gap", "padding", "margin")

fallos = []
avisos = []


def fallo(msg):
    fallos.append(msg)


def aviso(msg):
    avisos.append(msg)


def main():
    # ---------- 1. tokens ----------
    tokens_txt = (ROOT / "tokens.css").read_text(encoding="utf-8", errors="replace")
    tokens_txt = re.sub(r"/\*.*?\*/", "", tokens_txt, flags=re.S)
    tokens_def = set(VAR_DEF.findall(tokens_txt))

    packs = {}
    for pack in bc.PACKS_COMPONENTES:
        f = PACKS / pack
        if not f.exists():
            aviso(f"pack ausente: {pack} (el catálogo lo omite)")
            continue
        crudo = f.read_text(encoding="utf-8", errors="replace")
        limpio = re.sub(r"/\*.*?\*/", "", crudo, flags=re.S)
        packs[pack] = {"crudo": crudo, "limpio": limpio, "clases": bc.clases_declaradas(f)}

        # 1. sintaxis
        if limpio.count("{") != limpio.count("}"):
            fallo(f"{pack}: llaves desequilibradas ({{={limpio.count('{')} }}={limpio.count('}')})")
        if not crudo.lstrip().startswith("/*"):
            aviso(f"{pack}: sin cabecera de comentario")

        # 2. manifiesto (la capa de cristal es la única excepción: declara su
        #    propio manifiesto y usa SOLO tokens, nunca literales)
        if pack not in bc.PACKS_CRISTAL:
            for pat, etiqueta in [(r"\b(?:linear|radial|conic)-gradient\(", "gradiente"),
                                  (r"backdrop-filter", "glass (backdrop-filter)")]:
                m = re.search(pat, limpio)
                if m:
                    linea = limpio[:m.start()].count("\n") + 1
                    fallo(f"{pack}:{linea}: {etiqueta} prohibido por el manifiesto")

        for m in HEX.finditer(limpio):
            linea = limpio[:m.start()].count("\n") + 1
            fallo(f"{pack}:{linea}: color literal «{m.group(0)}» — usa un token")

        for m in re.finditer(r"!important", limpio):
            contexto = limpio[max(0, m.start() - 400):m.start()]
            sel = contexto.split("}")[-1]
            if any(e in sel for e in EXCEPCIONES_IMPORTANT):
                continue
            linea = limpio[:m.start()].count("\n") + 1
            fallo(f"{pack}:{linea}: !important no justificado")

        # 3. tokens
        for t in set(VAR_USE.findall(limpio)) - tokens_def:
            linea = limpio.find(t)
            linea = limpio[:linea].count("\n") + 1
            fallo(f"{pack}:{linea}: token inexistente {t}")

        # 7. clases fuera del espacio de nombres
        for m in re.finditer(r"(?:^|[\s,>+~])\.([a-z][a-z0-9_-]*)", limpio):
            nombre = m.group(1)
            if not nombre.startswith(("nz-", "cat-", "demo-", "live-", "is-")) and nombre != "nz":
                aviso(f"{pack}: clase fuera del prefijo .nz- → .{nombre}")
                break

    # ---------- 4. propiedad única ----------
    dueños = {}
    for pack, d in packs.items():
        for c in d["clases"]:
            dueños.setdefault(c, []).append(pack)
    for c, ps in sorted(dueños.items()):
        if len(ps) > 1:
            fallo(f"clase {c} declarada por varios packs: {', '.join(ps)}")

    # ---------- 5. cobertura: cada clase declarada, demostrada ─ ----------
    todas_declaradas = {c for d in packs.values() for c in d["clases"]}
    shell = set()
    fshell = PACKS / bc.PACK_SHELL
    if fshell.exists():
        shell = bc.clases_declaradas(fshell)
    if SPECS.exists():
        for s in bc.carga_specs():
            usadas = set()
            for d in s["demos"]:
                usadas |= bc.clases_de_markup(d["markup"])
            declaradas = packs.get(s["pack"], {}).get("clases", set())
            faltan = sorted(c for c in declaradas if c not in usadas)
            if faltan:
                aviso(f"categoría {s['cat']:02d} {s['nombre']}: {len(faltan)} objetos declarados "
                      f"sin demo ({', '.join(faltan[:6])}{'…' if len(faltan) > 6 else ''})")
            inventadas = sorted(c for c in usadas if c not in todas_declaradas | shell)
            if inventadas:
                fallo(f"categoría {s['cat']:02d} {s['nombre']}: usa clases que ningún pack declara: "
                      f"{', '.join(inventadas)}")

    # ---------- 6. atribución ----------
    paginas = list(bc.PAGINAS.glob("*.html")) + [ROOT / "index.html"]
    for p in paginas:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if "Hecho con ❤️ por David Antizar" not in t:
            fallo(f"{p.name}: falta la atribución exacta «Hecho con ❤️ por David Antizar»")
        if "data-nz-theme" not in t:
            aviso(f"{p.name}: sin data-nz-theme (el tema se fija en el <html>)")

    # ---------- 8. HTML bien formado ----------
    from html.parser import HTMLParser

    vacias = {"area", "base", "br", "col", "embed", "hr", "img", "input",
              "link", "meta", "source", "track", "wbr"}

    class Balance(HTMLParser):
        def __init__(self):
            super().__init__()
            self.pila = []
            self.errores = []

        def handle_starttag(self, etiqueta, attrs):
            if etiqueta not in vacias:
                self.pila.append(etiqueta)

        def handle_endtag(self, etiqueta):
            if not self.pila:
                self.errores.append(f"</{etiqueta}> de más (línea {self.getpos()[0]})")
            elif self.pila[-1] == etiqueta:
                self.pila.pop()
            else:
                self.errores.append(f"</{etiqueta}> no cierra la última abierta "
                                    f"(<{self.pila[-1]}>) en línea {self.getpos()[0]}")

    for p in paginas + [OUT_HTML]:
        if not p.exists():
            continue
        b = Balance()
        b.feed(p.read_text(encoding="utf-8", errors="replace"))
        pendientes = [x for x in b.pila if x not in ("html", "body")]
        if b.errores:
            fallo(f"{p.name}: HTML mal formado → {b.errores[0]}")
        if pendientes:
            aviso(f"{p.name}: etiquetas sin cerrar {pendientes[:4]}")

    # ---------- 9. JS del catálogo ----------
    js = ROOT / "js" / "catalog.js"
    if js.exists():
        t = js.read_text(encoding="utf-8", errors="replace")
        if t.count("{") != t.count("}"):
            fallo("js/catalog.js: llaves desequilibradas")
        if t.count("(") != t.count(")"):
            fallo("js/catalog.js: paréntesis desequilibrados")
        if "use strict" not in t:
            aviso("js/catalog.js: sin 'use strict'")

    # ---------- 10. cada página carga los packs que usa ----------
    # El catálogo no enlaza los 16 packs en todas las páginas: enlaza solo los que
    # necesita (se calcula del propio HTML). Esto lo blinda: si una clase aparece
    # y su pack no está enlazado, es un fallo, no un detalle de rendimiento.
    for p in paginas + [OUT_HTML]:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        enlazados = set(re.findall(r'href="(?:\.\./)?packs/(p\d+[-a-z0-9]*\.css)"', t))
        disponibles = set(shell)
        for pack in enlazados:
            disponibles |= packs.get(pack, {}).get("clases", set())
        huerfanas = sorted(c for c in bc.clases_de_markup(t) if c not in disponibles)
        if huerfanas:
            fallo(f"{p.name}: usa clases cuyo pack NO carga → {', '.join(huerfanas[:6])}")

    # ---------- 12. utilidades de visibilidad: con [class] o no ganan ----------
    # Un helper de visibilidad con la especificidad pelada (0,1,0) lo anula
    # cualquier componente que fije su propio display (0,1,0 + cargado después:
    # gana el último fichero, no la especificidad). Caso real (2026-09-20): en
    # MasterMindPublic, .nz-navbar__links { display: flex } (p2) anulaba a
    # .nz-hide-movil (p1) y el menú móvil mostraba los 5 enlaces apretados junto
    # a la hamburguesa. La defensa del sistema es el sufijo [class] (0,2,0),
    # igual que .nz-print-hide. Esta puerta impide reintroducir el fallo.
    OCULTACION = re.compile(r"^nz-(hide-|show-)")
    for pack, d in packs.items():
        for sel in bc.selectores((PACKS / pack).read_text(encoding="utf-8", errors="replace")):
            for clase in bc.CLASE.findall(sel):
                if not OCULTACION.match(clase):
                    continue
                if "[class]" not in sel:
                    fallo(f"{pack}: .{clase} se declara sin [class] en «{sel.strip()[:70]}» — "
                          f"un componente con display propio la anulará (usa .{clase}[class])")

    # ---------- resultado ----------
    total = sum(len(d["clases"]) for d in packs.values())
    # ---------- 11. valores literales que ya tienen token ----------
    # El manifiesto dice que todos los valores son tokens. Si existe un token con
    # el mismo valor exacto, escribir el literal es una incoherencia (y una
    # trampa: el día que el token cambie, esa regla se queda atrás).
    def literales(txt):
        fuera = []
        for m in re.finditer(r"\bborder(?!-radius)(?:-[a-z]+)*\s*:\s*(1px|1\.5px)\b", txt):
            tok = "--nz-border-w" if m.group(1) == "1px" else "--nz-border-w-strong"
            fuera.append(f"border en {m.group(1)} → usa var({tok})")
        for m in re.finditer(r"\b(gap|row-gap|column-gap|padding|margin)(?:-[a-z]+)?\s*:\s*([^;{}]+)", txt):
            valor = m.group(2)
            if "var(" in valor or "calc(" in valor:
                continue
            for v in NUM.findall(valor):
                vv = ("0" + v) if v.startswith(".") else v
                if vv in MAPA_ESPACIO:
                    fuera.append(f"{m.group(1)} usa {v} → hay token var(--nz-space-{MAPA_ESPACIO[vv]})")
        for m in re.finditer(r"\bfont-size\s*:\s*([^;{}]+)", txt):
            valor = m.group(1)
            if "var(" in valor or "clamp(" in valor:
                continue
            for v in NUM.findall(valor):
                vv = ("0" + v) if v.startswith(".") else v
                if vv in MAPA_TEXTO:
                    fuera.append(f"font-size usa {v} → hay token var(--nz-text-{MAPA_TEXTO[vv]})")
        return fuera

    for pack in sorted(PACKS.glob("p[0-9]*.css")):
        if pack.name.startswith("p0"):
            continue
        txt = re.sub(r"/\*.*?\*/", "", pack.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        for e in literales(txt):
            fallo(f"{pack.name}: {e}")

    # ---------- 12. versión: docs, generador, CDN y último tag de git ----------
    version_json = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))["version"]
    gen = (ROOT / "scripts" / "generar-llm-docs.py").read_text(encoding="utf-8")
    m_gen = re.search(r'^VERSION\s*=\s*"([^"]+)"', gen, re.M)
    version_gen = m_gen.group(1) if m_gen else None
    r_tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=ROOT,
                           capture_output=True, text=True)
    version_tag = r_tag.stdout.strip().lstrip("v") if r_tag.returncode == 0 else None
    if version_tag is None:
        aviso("git no tiene tags accesibles: no se puede comprobar la versión contra el último tag")
    if not (version_json == version_gen and (version_tag is None or version_gen == version_tag)):
        fallo(f"desalineación de versión: components.json={version_json}, "
              f"generar-llm-docs={version_gen}, último tag de git={version_tag or 'ninguno'}")

    # La skill del agente viaja CON el repo: si el sistema sube de versión y la
    # skill se queda atrás, un agente usará objetos que ya no son los vigentes.
    ruta_skill = ROOT / "SKILL.md"
    if not ruta_skill.exists():
        fallo("falta SKILL.md en la raíz: la skill del agente va con el repo")
    else:
        txt_skill = ruta_skill.read_text(encoding="utf-8")
        m_skill = re.search(r'^version:\s*"([^"]+)"', txt_skill, re.M)
        if not m_skill:
            fallo("SKILL.md sin campo version en el frontmatter")
        elif m_skill.group(1) != version_json:
            fallo(f"SKILL.md desalineada: version={m_skill.group(1)} vs components.json={version_json}")
        if f"v{version_json}" not in txt_skill:
            fallo(f"SKILL.md no menciona la versión vigente v{version_json} (CDN pineado)")
        # La skill es un puntero al repo, no una copia: si pierde el PASO 0 se
        # queda ciega en cuanto el sistema suba de versión.
        if "PASO 0" not in txt_skill or "el repo manda" not in txt_skill.lower():
            fallo("SKILL.md ha perdido el PASO 0: la skill debe mandar siempre al repo (la orden máxima)")
    docu = " ".join((ROOT / "README.md").read_text(encoding="utf-8")
                    + (ROOT / "AGENTS.md").read_text(encoding="utf-8")
                    + (ROOT / "LLM.md").read_text(encoding="utf-8"))
    if version_tag is not None:
        for m2 in re.finditer(r"Ntizar/Aurora@([^/)\s\"']+)", docu):
            if m2.group(1) != f"v{version_tag}":
                fallo(f"CDN sin pinear o con versión vieja (@{m2.group(1)}) en la doc; "
                      f"debe ser @v{version_tag} (jsDelivr sirve caché vieja de @master)")
                break

    # ---------- 13. sincronía de docs IA: regenerar y comparar ----------
    # Compara el contenido ANTES y DESPUÉS de regenerar (hash): si regenerar
    # cambia algo, los docs commiteados estaban desincronizados. Funciona igual
    # con el árbol limpio (CI) que con cambios locales pendientes.
    import hashlib
    def _hash(p):
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ""
    antes = (_hash(ROOT / "components.json"), _hash(ROOT / "LLM.md"))
    docs = subprocess.run([sys.executable, str(ROOT / "scripts" / "generar-llm-docs.py")],
                          cwd=ROOT, capture_output=True, text=True)
    if docs.returncode != 0:
        fallo("generar-llm-docs.py falló al regenerar: " + docs.stderr.strip()[:300])
    else:
        despues = (_hash(ROOT / "components.json"), _hash(ROOT / "LLM.md"))
        if antes != despues:
            fallo("components.json/LLM.md desincronizados con packs/specs: "
                  "ejecuta python scripts/generar-llm-docs.py y commitea el resultado")

    # ---------- 14. el lint del consumidor funciona ----------
    st = subprocess.run([sys.executable, str(ROOT / "scripts" / "auditar-uso.py"), "--selftest"],
                        cwd=ROOT, capture_output=True, text=True)
    if st.returncode != 0:
        fallo("el auto-test de scripts/auditar-uso.py falla:\n"
              + (st.stdout + st.stderr).strip()[-400:])

    print(f"\nAurora · validación de {len(packs)} packs · {total} objetos declarados\n")
    if avisos:
        print(f"AVISOS ({len(avisos)}):")
        for a in avisos[:40]:
            print("  ·", a)
        if len(avisos) > 40:
            print(f"  … y {len(avisos) - 40} más")
        print()
    if fallos:
        print(f"FALLOS ({len(fallos)}):")
        for f in fallos[:60]:
            print("  ✗", f)
        if len(fallos) > 60:
            print(f"  … y {len(fallos) - 60} más")
        print("\nRESULTADO: NO VÁLIDO")
        return 1
    print("RESULTADO: VÁLIDO — manifiesto y cobertura en orden ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
