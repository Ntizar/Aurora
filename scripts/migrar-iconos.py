#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra los símbolos de texto que hacían de icono a SVG `.nz-icon`.

Los specs son la fuente de verdad de las demos: se reemplaza ahí y se regenera.
También se aplica a bloques/ejemplos/ (páginas de consumidor) y al shell del catálogo.

Es idempotente: si ya no queda ningún símbolo, no cambia nada.

Uso: python3 scripts/migrar-iconos.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SVG = {
    "▦": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
    "▤": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "⚙": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.09a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.09a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.09a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "⌕": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "◐": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/></svg>',
    "⌂": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/></svg>',
    "✓": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "✕": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    "✎": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L20 8l-4-4L4 16z"/><path d="M14 6l4 4"/></svg>',
    "▶": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7z"/></svg>',
    "＋": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    "⤓": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12"/><path d="m7 12 5 5 5-5"/><path d="M5 21h14"/></svg>',
    "⊞": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/></svg>',
    "✉": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "⌸": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5v14h16"/><path d="M8 16v-5M13 16V8M18 16v-3"/></svg>',
    "⌗": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m4 17 6-6-6-6"/><path d="M12 19h8"/></svg>',
    "◈": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z"/></svg>',
    "⑂": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 8v8M8 6h4a4 4 0 0 1 4 4v0"/></svg>',
    "¶": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>',
    "?": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 2-3 4"/><path d="M12 17h.01"/></svg>',
    "✳": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v20M2 12h20M4.9 4.9l14.2 14.2M19.1 4.9 4.9 19.1"/></svg>',
    "✦": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.2 6.8L21 12l-6.8 2.2L12 21l-2.2-6.8L3 12l6.8-2.2z"/></svg>',
    "★": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.7 5.9 6.3.8-4.6 4.4 1.2 6.4L12 17.4 6.4 20.5l1.2-6.4L3 9.7l6.3-.8z"/></svg>',
    "♥": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.3 4.6 13a4.6 4.6 0 0 1 6.5-6.5l.9.9.9-.9A4.6 4.6 0 0 1 19.4 13Z"/></svg>',
    "♡": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.3 4.6 13a4.6 4.6 0 0 1 6.5-6.5l.9.9.9-.9A4.6 4.6 0 0 1 19.4 13Z"/></svg>',
    "◆": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.8 21.2 12 12 21.2 2.8 12Z"/></svg>',
    "●": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="6.5"/></svg>',
    "■": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2"/></svg>',
    "▲": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4.5 20 18.5H4Z"/></svg>',
    "◦": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/></svg>',
    "▢": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>',
    "▤": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h9"/></svg>',
    "▸": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>',
    "▾": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg>',
    "▼": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg>',
    "⚠": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20h20Z"/><path d="M12 9.5v4.5M12 17h.01"/></svg>',
    "🎉": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9z"/><path d="M18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z"/></svg>',
    "📦": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 8 12 3 3 8v8l9 5 9-5Z"/><path d="m3 8 9 5 9-5M12 13v8"/></svg>',
    "🔍": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>',
    "📂": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M3 11h18"/></svg>',
    "🛒": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M3 4h2l2.4 11h11.2L21 8H6"/></svg>',
    "☰": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "⬆": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20V5"/><path d="m5.5 11.5 6.5-6.5 6.5 6.5"/></svg>',
    "↻": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4v5h-5"/></svg>',
    "✗": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    "⛔": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m6 18 12-12"/></svg>',
    "💬": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a8 8 0 0 1-8 8H8l-5 3V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8Z"/></svg>',
    "🔗": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1"/></svg>',
    "✉": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "➤": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3 3 10.5l7 2.5 2.5 7Z"/><path d="m10 13 4.5-4.5"/></svg>',
    "🔖": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 3H6a1 1 0 0 0-1 1v17l7-4.5 7 4.5V4a1 1 0 0 0-1-1Z"/></svg>',
    "✓": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "◍": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M12 11v5"/></svg>',
    "←": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5"/><path d="m11 18-6-6 6-6"/></svg>',
}


# Símbolos que se usan como icono y nunca como prosa: se sustituyen incluso
# cuando van pegados a texto ("5★", "★★★★★").
CATCHALL = "★♥♡◆●■▲▢▤▸▾▼⚠🎉📦🔍📂🛒☰⬆↻✗⛔💬🔗✉➤🔖✓◍◦"


def sustituir_markup(markup: str) -> str:
    # Solo cuando el símbolo es TODO el contenido de un elemento: >X< o >X</
    for simbolo, svg in SVG.items():
        markup = markup.replace(f">{simbolo}<", f">{svg}<")
        markup = markup.replace(f">{simbolo}</", f">{svg}</")
        # Símbolo con texto detrás dentro del mismo elemento ("⚠ No se pudo") y
        # símbolo al final del contenido ("chat 💬</div>").
        markup = markup.replace(f">{simbolo} ", f">{svg} ")
        markup = markup.replace(f" {simbolo}</", f" {svg}</")
    # Última pasada: símbolos que nunca son prosa (una valoración "★★★★★", un
    # "5★"). Los de teclado (⌘ ⇧ ↵ ↑ ↓ ⇥) y las flechas de texto NO están aquí a
    # propósito: ahí el glifo es tipografía, no icono.
    for simbolo in CATCHALL:
        if simbolo in markup and simbolo in SVG:
            markup = markup.replace(simbolo, SVG[simbolo])
    return markup


def main() -> int:
    cambios = 0
    for p in sorted((ROOT / "specs").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        tocado = False
        for demo in d.get("demos", []):
            antes = demo.get("markup", "")
            despues = sustituir_markup(antes)
            if despues != antes:
                demo["markup"] = despues
                tocado = True
                cambios += 1
        if tocado:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"specs/{p.name}: iconos migrados")

    for p in sorted((ROOT / "bloques" / "ejemplos").glob("*.html")):
        t = p.read_text(encoding="utf-8")
        nuevo = t
        for simbolo, svg in SVG.items():
            nuevo = nuevo.replace(f">{simbolo}<", f">{svg}<")
            nuevo = nuevo.replace(f">{simbolo}</", f">{svg}</")
        if nuevo != t:
            p.write_text(nuevo, encoding="utf-8")
            cambios += 1
            print(f"bloques/ejemplos/{p.name}: iconos migrados")

    print(f"Total: {cambios} bloque(s) actualizados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
