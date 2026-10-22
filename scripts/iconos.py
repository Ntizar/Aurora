#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repositorio de iconos numerados de Aurora.

Cada icono tiene un **número estable** (`nz-i-001`, `nz-i-042`, …) que no se
reutiliza nunca: un diseño puede decir «el icono 042» y todos hablan del mismo
dibujo, aunque el nombre castellano cambie o la colección se amplíe. El número
es la referencia pública; el nombre es la comodidad.

Fuente: **Lucide** (ISC) vía el JSON de Iconify. El repositorio guarda el SVG
normalizado, así que servir un icono no depende de la red ni de un CDN ajeno.

  iconos/iconos.json   manifiesto: número, id lucide, nombre, grupo, licencia, hash
  iconos/NNN-nombre.svg un fichero por icono, SVG plano 24×24 con currentColor
  iconos/sprite.svg    un solo fichero con un <symbol> por icono (para <use>)
  iconos/index.html    catálogo navegable por número, nombre o id

Uso:
  python3 scripts/iconos.py sembrar                # siembra el núcleo (idempotente)
  python3 scripts/iconos.py anadir lucide:key lucide:pill
  python3 scripts/iconos.py listar [--grupo mapas]
  python3 scripts/iconos.py retirar 042            # el número NO se reutiliza
  python3 scripts/iconos.py sprite                 # regenera iconos/sprite.svg
  python3 scripts/iconos.py catalogo               # regenera iconos/index.html
  python3 scripts/iconos.py todo                   # sprite + catalogo

Reglas que este script mantiene solo:
  · numeración correlativa sin huecos salvo retirados declarados,
  · un id lucide no entra dos veces,
  · el nombre del fichero es `NNN-nombre.svg` y siempre en castellano,
  · el SVG no lleva color a mano (stroke=currentColor) ni tamaño fijo de diseño.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "iconos"
MANIFIESTO = DIR / "iconos.json"
SPRITE = DIR / "sprite.svg"
CATALOGO = DIR / "index.html"
FUENTE = "https://raw.githubusercontent.com/iconify/icon-sets/master/json/lucide.json"
CACHE = Path.home() / ".cache" / "aurora-iconos"
PREFIJO = "nz-i-"
DIGITOS = 3

# Atributos que Lucide repite en cada elemento y que suben a la raíz del SVG:
# el color y el grosor los pone el sistema (var(--nz-icon-stroke)), no el fichero.
ATTRS_STD = ('fill="none" stroke="currentColor" stroke-linecap="round" '
             'stroke-linejoin="round" stroke-width="2"')

# ---------------------------------------------------------------------------
# Núcleo: los iconos que el sistema necesita de verdad, en orden de numeración.
# (id lucide, nombre castellano, grupo). El orden manda: no se reordena nunca,
# porque reordenar cambiaría los números ya publicados.
# ---------------------------------------------------------------------------
GRUPOS = {
    "navegacion": "Navegación",
    "acciones": "Acciones",
    "estados": "Estados",
    "datos": "Datos y gráficas",
    "archivos": "Archivos",
    "personas": "Personas y organización",
    "comunicacion": "Comunicación",
    "media": "Media y dispositivos",
    "mapas": "Mapas y transporte",
    "comercio": "Comercio",
    "sistema": "Sistema y desarrollo",
    "marcas": "Marcas",
    "formato": "Formato y objetos",
    "varios": "Varios",
}

NUCLEO = [
    # --- navegación ---
    ("house", "hogar", "navegacion"),
    ("arrow-left", "flecha-izquierda", "navegacion"),
    ("arrow-right", "flecha-derecha", "navegacion"),
    ("arrow-up", "flecha-arriba", "navegacion"),
    ("arrow-down", "flecha-abajo", "navegacion"),
    ("arrow-up-right", "flecha-arriba-derecha", "navegacion"),
    ("arrow-down-right", "flecha-abajo-derecha", "navegacion"),
    ("chevron-left", "angulo-izquierda", "navegacion"),
    ("chevron-right", "angulo-derecha", "navegacion"),
    ("chevron-up", "angulo-arriba", "navegacion"),
    ("chevron-down", "angulo-abajo", "navegacion"),
    ("chevrons-left", "doble-angulo-izquierda", "navegacion"),
    ("chevrons-right", "doble-angulo-derecha", "navegacion"),
    ("corner-down-left", "retorno", "navegacion"),
    ("menu", "menu", "navegacion"),
    ("x", "cerrar", "navegacion"),
    ("ellipsis", "mas-opciones", "navegacion"),
    ("ellipsis-vertical", "mas-opciones-vertical", "navegacion"),
    ("external-link", "enlace-externo", "navegacion"),
    ("search", "buscar", "navegacion"),
    ("panel-left", "panel-izquierda", "navegacion"),
    ("panel-right", "panel-derecha", "navegacion"),
    ("layout-grid", "rejilla", "navegacion"),
    ("list", "lista", "navegacion"),
    ("filter", "filtro", "navegacion"),
    ("sliders-horizontal", "ajustes-rapidos", "navegacion"),
    ("expand", "ampliar", "navegacion"),
    ("shrink", "reducir", "navegacion"),
    ("move", "mover", "navegacion"),
    ("maximize", "maximizar", "navegacion"),
    ("minimize", "minimizar", "navegacion"),
    ("zoom-in", "acercar", "navegacion"),
    ("zoom-out", "alejar", "navegacion"),
    # --- acciones ---
    ("plus", "anadir", "acciones"),
    ("minus", "quitar", "acciones"),
    ("check", "comprobado", "acciones"),
    ("pencil", "editar", "acciones"),
    ("trash-2", "borrar", "acciones"),
    ("copy", "copiar", "acciones"),
    ("clipboard", "portapapeles", "acciones"),
    ("download", "descargar", "acciones"),
    ("upload", "subir", "acciones"),
    ("refresh-cw", "actualizar", "acciones"),
    ("rotate-ccw", "deshacer", "acciones"),
    ("undo-2", "volver-atras", "acciones"),
    ("redo-2", "rehacer", "acciones"),
    ("share-2", "compartir", "acciones"),
    ("save", "guardar", "acciones"),
    ("printer", "imprimir", "acciones"),
    ("send", "enviar", "acciones"),
    ("link", "enlace", "acciones"),
    ("paperclip", "adjuntar", "acciones"),
    ("scissors", "cortar", "acciones"),
    ("pin", "fijar", "acciones"),
    ("bookmark", "marcador", "acciones"),
    ("star", "estrella", "acciones"),
    ("heart", "corazon", "acciones"),
    ("flag", "bandera", "acciones"),
    ("tag", "etiqueta", "acciones"),
    ("eye", "ver", "acciones"),
    ("eye-off", "ocultar", "acciones"),
    ("lock", "bloquear", "acciones"),
    ("unlock", "desbloquear", "acciones"),
    ("key", "llave", "acciones"),
    ("log-in", "entrar", "acciones"),
    ("log-out", "salir", "acciones"),
    ("settings", "ajustes", "acciones"),
    ("power", "encendido", "acciones"),
    # --- estados ---
    ("circle-check", "verificado", "estados"),
    ("circle-x", "error", "estados"),
    ("circle-alert", "aviso", "estados"),
    ("triangle-alert", "atencion", "estados"),
    ("circle-help", "ayuda", "estados"),
    ("info", "informacion", "estados"),
    ("circle", "circulo", "estados"),
    ("circle-dot", "punto-activo", "estados"),
    ("dot", "punto", "estados"),
    ("ban", "prohibido", "estados"),
    ("loader", "cargando", "estados"),
    ("clock", "reloj", "estados"),
    ("timer", "temporizador", "estados"),
    ("alarm-clock", "alarma", "estados"),
    ("hourglass", "espera", "estados"),
    ("badge-check", "sello-verificado", "estados"),
    ("badge-alert", "sello-aviso", "estados"),
    ("shield", "escudo", "estados"),
    ("shield-check", "protegido", "estados"),
    ("shield-alert", "riesgo-seguridad", "estados"),
    # --- datos ---
    ("chart-column", "barras", "datos"),
    ("chart-line", "linea", "datos"),
    ("chart-pie", "tarta", "datos"),
    ("chart-area", "area", "datos"),
    ("chart-scatter", "dispersion", "datos"),
    ("trending-up", "sube", "datos"),
    ("trending-down", "baja", "datos"),
    ("activity", "actividad", "datos"),
    ("calendar", "calendario", "datos"),
    ("calendar-days", "calendario-mensual", "datos"),
    ("database", "base-de-datos", "datos"),
    ("table", "tabla", "datos"),
    ("list-checks", "tareas", "datos"),
    ("target", "objetivo", "datos"),
    ("gauge", "indicador", "datos"),
    ("percent", "porcentaje", "datos"),
    ("calculator", "calculadora", "datos"),
    ("sigma", "suma", "datos"),
    ("layers", "capas", "datos"),
    ("workflow", "flujo", "datos"),
    ("kanban", "kanban", "datos"),
    # --- archivos ---
    ("file", "archivo", "archivos"),
    ("file-text", "documento", "archivos"),
    ("file-plus", "archivo-nuevo", "archivos"),
    ("file-check", "archivo-validado", "archivos"),
    ("file-spreadsheet", "hoja-calculo", "archivos"),
    ("presentation", "presentacion", "archivos"),
    ("folder", "carpeta", "archivos"),
    ("folder-open", "carpeta-abierta", "archivos"),
    ("folder-plus", "carpeta-nueva", "archivos"),
    ("archive", "archivo-comprimido", "archivos"),
    ("box", "caja", "archivos"),
    ("package", "paquete", "archivos"),
    ("hard-drive", "disco", "archivos"),
    ("cloud", "nube", "archivos"),
    ("cloud-upload", "subir-a-nube", "archivos"),
    ("book", "libro", "archivos"),
    ("book-open", "libro-abierto", "archivos"),
    ("notebook", "cuaderno", "archivos"),
    ("newspaper", "periodico", "archivos"),
    ("receipt", "recibo", "archivos"),
    ("sticky-note", "nota", "archivos"),
    # --- personas ---
    ("user", "usuario", "personas"),
    ("users", "usuarios", "personas"),
    ("user-plus", "usuario-nuevo", "personas"),
    ("user-check", "usuario-validado", "personas"),
    ("user-x", "usuario-bloqueado", "personas"),
    ("user-cog", "usuario-configuracion", "personas"),
    ("contact", "contacto", "personas"),
    ("building-2", "edificio", "personas"),
    ("briefcase", "maletin", "personas"),
    ("id-card", "tarjeta-identidad", "personas"),
    ("accessibility", "accesibilidad", "personas"),
    ("handshake", "acuerdo", "personas"),
    # --- comunicación ---
    ("mail", "correo", "comunicacion"),
    ("mail-open", "correo-abierto", "comunicacion"),
    ("message-square", "mensaje", "comunicacion"),
    ("message-circle", "mensaje-redondo", "comunicacion"),
    ("messages-square", "conversacion", "comunicacion"),
    ("phone", "telefono", "comunicacion"),
    ("phone-call", "llamada", "comunicacion"),
    ("bell", "campana", "comunicacion"),
    ("bell-off", "sin-avisos", "comunicacion"),
    ("at-sign", "arroba", "comunicacion"),
    ("megaphone", "megafono", "comunicacion"),
    ("reply", "responder", "comunicacion"),
    ("forward", "reenviar", "comunicacion"),
    ("inbox", "bandeja", "comunicacion"),
    ("voicemail", "buzon-de-voz", "comunicacion"),
    ("rss", "fuente-rss", "comunicacion"),
    # --- media ---
    ("image", "imagen", "media"),
    ("video", "video", "media"),
    ("camera", "camara", "media"),
    ("film", "pelicula", "media"),
    ("music", "musica", "media"),
    ("audio-lines", "ondas-de-audio", "media"),
    ("radio", "radio", "media"),
    ("tv", "television", "media"),
    ("monitor", "pantalla", "media"),
    ("smartphone", "movil", "media"),
    ("tablet", "tableta", "media"),
    ("laptop", "portatil", "media"),
    ("watch", "reloj-de-pulsera", "media"),
    ("cast", "emitir", "media"),
    ("play", "reproducir", "media"),
    ("pause", "pausar", "media"),
    ("square", "detener", "media"),
    ("skip-forward", "siguiente", "media"),
    ("skip-back", "anterior", "media"),
    ("volume-2", "volumen", "media"),
    ("volume-x", "silencio", "media"),
    ("mic", "microfono", "media"),
    ("mic-off", "microfono-apagado", "media"),
    ("headphones", "auriculares", "media"),
    # --- mapas ---
    ("map-pin", "ubicacion", "mapas"),
    ("map", "mapa", "mapas"),
    ("map-pinned", "ubicacion-fijada", "mapas"),
    ("navigation", "navegacion", "mapas"),
    ("compass", "brujula", "mapas"),
    ("route", "ruta", "mapas"),
    ("globe", "mundo", "mapas"),
    ("locate-fixed", "posicion-actual", "mapas"),
    ("plane", "avion", "mapas"),
    ("car", "coche", "mapas"),
    ("train-front", "tren", "mapas"),
    ("bike", "bicicleta", "mapas"),
    ("ship", "barco", "mapas"),
    ("truck", "camion", "mapas"),
    ("fuel", "combustible", "mapas"),
    ("milestone", "hito", "mapas"),
    ("signpost", "senal", "mapas"),
    # --- comercio ---
    ("shopping-cart", "carrito", "comercio"),
    ("shopping-bag", "bolsa-compra", "comercio"),
    ("credit-card", "tarjeta", "comercio"),
    ("wallet", "monedero", "comercio"),
    ("banknote", "billete", "comercio"),
    ("coins", "monedas", "comercio"),
    ("piggy-bank", "hucha", "comercio"),
    ("store", "tienda", "comercio"),
    ("gift", "regalo", "comercio"),
    ("ticket", "entrada", "comercio"),
    ("badge-percent", "oferta", "comercio"),
    # --- sistema ---
    ("cpu", "procesador", "sistema"),
    ("server", "servidor", "sistema"),
    ("terminal", "terminal", "sistema"),
    ("code", "codigo", "sistema"),
    ("code-xml", "codigo-xml", "sistema"),
    ("git-branch", "rama", "sistema"),
    ("git-commit", "commit", "sistema"),
    ("git-pull-request", "pull-request", "sistema"),
    ("git-merge", "fusion", "sistema"),
    ("bug", "error-software", "sistema"),
    ("rocket", "lanzamiento", "sistema"),
    ("sparkles", "destellos", "sistema"),
    ("zap", "rayo", "sistema"),
    ("flame", "llama", "sistema"),
    ("sun", "sol", "sistema"),
    ("moon", "luna", "sistema"),
    ("droplet", "gota", "sistema"),
    ("wind", "viento", "sistema"),
    ("thermometer", "termometro", "sistema"),
    ("umbrella", "paraguas", "sistema"),
    ("lightbulb", "idea", "sistema"),
    ("leaf", "hoja", "sistema"),
    ("wifi", "wifi", "sistema"),
    ("wifi-off", "sin-conexion", "sistema"),
    ("bluetooth", "bluetooth", "sistema"),
    ("battery", "bateria", "sistema"),
    ("battery-charging", "bateria-cargando", "sistema"),
    ("plug", "enchufe", "sistema"),
    ("fingerprint", "huella", "sistema"),
    ("qr-code", "codigo-qr", "sistema"),
    ("barcode", "codigo-barras", "sistema"),
    ("scan", "escanear", "sistema"),
    ("bot", "bot", "sistema"),
    ("brain", "cerebro", "sistema"),
    ("network", "red", "sistema"),
    ("webhook", "webhook", "sistema"),
    # --- marcas ---
    ("github", "github", "marcas"),
    ("twitter", "twitter", "marcas"),
    ("linkedin", "linkedin", "marcas"),
    ("youtube", "youtube", "marcas"),
    ("instagram", "instagram", "marcas"),
    ("facebook", "facebook", "marcas"),
    ("slack", "slack", "marcas"),
    ("figma", "figma", "marcas"),
    ("gitlab", "gitlab", "marcas"),
    ("chrome", "chrome", "marcas"),
    ("twitch", "twitch", "marcas"),
    ("dribbble", "dribbble", "marcas"),
    ("codepen", "codepen", "marcas"),
    ("framer", "framer", "marcas"),
    ("bitcoin", "bitcoin", "marcas"),
    # --- formato ---
    ("graduation-cap", "formacion", "formato"),
    ("scale", "balanza", "formato"),
    ("gavel", "mazo", "formato"),
    ("languages", "idiomas", "formato"),
    ("type", "tipografia", "formato"),
    ("bold", "negrita", "formato"),
    ("italic", "cursiva", "formato"),
    ("underline", "subrayado", "formato"),
    ("align-left", "alinear-izquierda", "formato"),
    ("align-center", "centrar", "formato"),
    ("align-right", "alinear-derecha", "formato"),
    ("palette", "paleta", "formato"),
    ("paintbrush", "pincel", "formato"),
    ("wand-sparkles", "magia", "formato"),
    ("crop", "recortar", "formato"),
    ("shapes", "formas", "formato"),
    ("puzzle", "pieza", "formato"),
    ("trophy", "trofeo", "formato"),
    ("medal", "medalla", "formato"),
    ("gem", "gema", "formato"),
    ("anchor", "ancla", "formato"),
    ("telescope", "telescopio", "formato"),
    ("binoculars", "prismaticos", "formato"),
    ("thumbs-up", "me-gusta", "formato"),
    ("smile", "sonrisa", "formato"),
    ("hand", "mano", "formato"),
    ("mouse-pointer", "puntero", "formato"),
]

# Glosario para `anadir`: token inglés → castellano. Un id nuevo se traduce
# componiendo sus tokens; si falta uno, el script lo dice y no inventa nombres.
GLOSARIO = {
    "arrow": "flecha", "chevron": "angulo", "chevrons": "doble-angulo",
    "circle": "circulo", "square": "cuadrado", "triangle": "triangulo",
    "left": "izquierda", "right": "derecha", "up": "arriba", "down": "abajo",
    "big": "grande", "small": "pequeno", "up-right": "arriba-derecha",
    "check": "comprobado", "x": "cerrar", "plus": "mas", "minus": "menos",
    "file": "archivo", "folder": "carpeta", "user": "usuario",
    "users": "usuarios", "heart": "corazon", "star": "estrella",
    "calendar": "calendario", "clock": "reloj", "timer": "temporizador",
    "mail": "correo", "message": "mensaje", "phone": "telefono",
    "bell": "campana", "chart": "grafica", "bar": "barra", "line": "linea",
    "pie": "tarta", "area": "area", "map": "mapa", "pin": "alfiler",
    "globe": "mundo", "lock": "candado", "key": "llave", "eye": "vista",
    "book": "libro", "box": "caja", "package": "paquete", "cloud": "nube",
    "sun": "sol", "moon": "luna", "zap": "rayo", "flame": "llama",
    "leaf": "hoja", "droplet": "gota", "wind": "viento", "snow": "nieve",
    "cpu": "procesador", "server": "servidor", "terminal": "terminal",
    "code": "codigo", "git": "git", "branch": "rama", "commit": "commit",
    "merge": "fusion", "bug": "error-software", "sparkles": "destellos",
    "wifi": "wifi", "battery": "bateria", "plug": "enchufe",
    "badge": "sello", "shield": "escudo", "alert": "aviso",
    "info": "informacion", "help": "ayuda", "ban": "prohibido",
    "loader": "cargando", "search": "buscar", "menu": "menu",
    "list": "lista", "grid": "rejilla", "layout": "disposicion",
    "panel": "panel", "filter": "filtro", "sliders": "controles",
    "settings": "ajustes", "cog": "engranaje", "tool": "herramienta",
    "refresh": "actualizar", "rotate": "rotar", "undo": "deshacer",
    "redo": "rehacer", "share": "compartir", "save": "guardar",
    "download": "descargar", "upload": "subir", "copy": "copiar",
    "clipboard": "portapapeles", "trash": "borrar", "pencil": "lapiz",
    "edit": "editar", "send": "enviar", "link": "enlace", "unlink": "desenlazar",
    "external": "externo", "paperclip": "adjuntar", "scissors": "tijeras",
    "tag": "etiqueta", "flag": "bandera", "bookmark": "marcador",
    "shopping": "compra", "cart": "carrito", "bag": "bolsa",
    "credit": "credito", "card": "tarjeta", "wallet": "monedero",
    "coins": "monedas", "banknote": "billete", "receipt": "recibo",
    "store": "tienda", "truck": "camion", "car": "coche", "plane": "avion",
    "train": "tren", "bike": "bicicleta", "ship": "barco", "fuel": "combustible",
    "house": "hogar", "home": "hogar", "building": "edificio",
    "briefcase": "maletin", "camera": "camara", "video": "video",
    "image": "imagen", "film": "pelicula", "music": "musica", "mic": "microfono",
    "volume": "volumen", "play": "reproducir", "pause": "pausar",
    "skip": "saltar", "forward": "reenviar", "reply": "responder",
    "inbox": "bandeja", "at": "arroba", "sign": "signo", "rss": "fuente-rss",
    "monitor": "pantalla", "tv": "television", "smartphone": "movil",
    "tablet": "tableta", "laptop": "portatil", "watch": "reloj-de-pulsera",
    "type": "tipografia", "bold": "negrita", "italic": "cursiva",
    "underline": "subrayado", "align": "alinear", "palette": "paleta",
    "crop": "recortar", "shapes": "formas", "puzzle": "pieza",
    "trophy": "trofeo", "medal": "medalla", "gem": "gema",
    "fingerprint": "huella", "qr": "qr", "scan": "escanear",
    "bot": "bot", "brain": "cerebro", "network": "red", "workflow": "flujo",
    "layer": "capa", "layers": "capas", "table": "tabla",
    "database": "base-de-datos", "target": "objetivo", "gauge": "indicador",
    "percent": "porcentaje", "calculator": "calculadora", "sigma": "suma",
    "trending": "tendencia", "activity": "actividad", "kanban": "kanban",
    "languages": "idiomas", "scale": "balanza", "gavel": "mazo",
    "graduation": "formacion", "cap": "birrete", "anchor": "ancla",
    "telescope": "telescopio", "smile": "sonrisa", "thumbs": "pulgar",
    "hand": "mano", "mouse": "raton", "pointer": "puntero", "move": "mover",
    "expand": "ampliar", "shrink": "reducir", "maximize": "maximizar",
    "minimize": "minimizar", "zoom": "zoom", "in": "acercar", "out": "alejar",
    "lock-open": "desbloquear", "log": "sesion", "login": "entrar",
    "logout": "salir", "power": "encendido", "archive": "archivo-comprimido",
    "hard": "duro", "drive": "disco", "notebook": "cuaderno",
    "newspaper": "periodico", "note": "nota", "sticky": "adhesiva",
    "presentation": "presentacion", "spreadsheet": "hoja-calculo",
    "contact": "contacto", "id": "identidad", "accessibility": "accesibilidad",
    "handshake": "acuerdo", "megaphone": "megafono", "voicemail": "buzon-de-voz",
    "milestone": "hito", "signpost": "senal", "compass": "brujula",
    "route": "ruta", "navigation": "navegacion", "locate": "localizar",
    "fixed": "fijado", "gift": "regalo", "ticket": "entrada",
    "piggy": "hucha", "cpu": "procesador", "rocket": "lanzamiento",
    "thermometer": "termometro", "umbrella": "paraguas",
    "lightbulb": "bombilla", "bluetooth": "bluetooth", "barcode": "codigo-barras",
    "webhook": "webhook", "headphones": "auriculares", "audio": "audio",
    "lines": "lineas", "radio": "radio", "cast": "emitir", "paintbrush": "pincel",
    "wand": "varita", "magic": "magia", "binoculars": "prismaticos",
    "dots": "puntos", "dot": "punto", "ring": "anillo", "hourglass": "reloj-de-arena",
    "alarm": "alarma", "ellipsis": "puntos-suspensivos", "vertical": "vertical",
    "horizontal": "horizontal", "more": "mas", "corner": "esquina",
    "return": "retorno", "enter": "intro", "space": "espacio",
    "picker": "selector", "pipette": "cuentagotas", "swatch": "muestra",
    "brush": "brocha", "ruler": "regla", "pen": "pluma", "eraser": "goma",
    "highlight": "resaltar", "crop": "recortar", "flip": "voltear",
    "rotate-cw": "girar-derecha", "rotate-ccw": "girar-izquierda",
}

# Alias: el JSON de Iconify resuelve nombres antiguos a su icono actual.
ALIAS = {}


# ---------------------------------------------------------------------------
# Fuente
# ---------------------------------------------------------------------------
def descargar() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    destino = CACHE / "lucide.json"
    if not destino.exists():
        print(f"· descargando Lucide desde Iconify ({FUENTE})")
        with urllib.request.urlopen(FUENTE, timeout=60) as r:
            destino.write_bytes(r.read())
    return json.loads(destino.read_text(encoding="utf-8"))


def cuerpo_de(datos: dict, nombre: str) -> tuple[str, str]:
    """Devuelve (cuerpo SVG normalizado, id real). Resuelve alias."""
    iconos = datos["icons"]
    if nombre in iconos:
        return normalizar(iconos[nombre]["body"]), nombre
    alias = datos.get("aliases", {})
    if nombre in alias and alias[nombre].get("parent") in iconos:
        padre = alias[nombre]["parent"]
        return normalizar(iconos[padre]["body"]), padre
    raise SystemExit(f"icono desconocido en Lucide: {nombre}")


def normalizar(body: str) -> str:
    """Sube los atributos repetidos a la raíz y deja el cuerpo limpio.

    Lucide envuelve muchos iconos en un `<g>` que solo llevaba los atributos de
    trazo: al subirlos a la raíz, el grupo sobra. Se desenvuelve solo cuando es
    un único grupo exterior (nada de tocar grupos internos con transformación).
    """
    cuerpo = body.replace(ATTRS_STD, "").strip()
    cuerpo = re.sub(r"\s+>", ">", cuerpo)
    m = re.match(r"^<g[^>]*>(.*)</g>$", cuerpo, re.S)
    if m and "<g" not in m.group(1):
        cuerpo = m.group(1).strip()
        cuerpo = re.sub(r"\s+>", ">", cuerpo)
    cuerpo = re.sub(r"\s+", " ", cuerpo)
    return cuerpo


def hash_de(cuerpo: str) -> str:
    return "sha256:" + hashlib.sha256(cuerpo.encode("utf-8")).hexdigest()[:16]


def svg_archivo(numero: int, nombre: str, cuerpo: str, lucide: str, spdx: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
        f'stroke-linecap="round" stroke-linejoin="round" role="img" '
        f'data-icono="{PREFIJO}{numero:0{DIGITOS}d}" data-lucide="{lucide}">\n'
        f"  <!-- {PREFIJO}{numero:0{DIGITOS}d} · {nombre} · Lucide ({spdx}) -->\n"
        f"  {cuerpo}\n</svg>\n"
    )


def manifiesto_vacio() -> dict:
    return {
        "sistema": "Aurora",
        "coleccion": "Lucide",
        "fuente": "https://github.com/lucide-icons/lucide",
        "licencia": {
            "titulo": "ISC",
            "spdx": "ISC",
            "url": "https://github.com/lucide-icons/lucide/blob/main/LICENSE",
            "atribucion": "Lucide Contributors · https://lucide.dev",
        },
        "convencion": {
            "prefijo": PREFIJO,
            "digitos": DIGITOS,
            "archivo": f"NNN-nombre.svg",
            "enLinea": '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true">…</svg>',
            "enSprite": f'<svg class="nz-icon" aria-hidden="true"><use href="sprite.svg#{PREFIJO}042"/></svg>',
            "regla": "Un número no se reutiliza nunca; un icono retirado deja su hueco declarado.",
        },
        "total": 0,
        "siguiente": 1,
        "numerosRetirados": [],
        "iconos": [],
    }


def cargar() -> dict:
    if MANIFIESTO.exists():
        return json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    return manifiesto_vacio()


def guardar(m: dict) -> None:
    m["iconos"].sort(key=lambda i: i["numero"])
    vivos = [i for i in m["iconos"] if i.get("estado", "activo") == "activo"]
    m["total"] = len(vivos)
    m["siguiente"] = max((i["numero"] for i in m["iconos"]), default=0) + 1
    DIR.mkdir(parents=True, exist_ok=True)
    MANIFIESTO.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Numérico / nombres
# ---------------------------------------------------------------------------
def numero_de(m: dict, lucide: str):
    for i in m["iconos"]:
        if i["lucide"] == lucide and i.get("estado", "activo") == "activo":
            return i["numero"]
    return None


def slug_de(m: dict, nombre: str) -> str:
    base = re.sub(r"[^a-z0-9-]", "-", nombre.lower())
    usado = {i["archivo"] for i in m["iconos"] if i.get("archivo")}
    if any(u.endswith(f"-{base}.svg") for u in usado):
        n = 2
        while any(u.endswith(f"-{base}-{n}.svg") for u in usado):
            n += 1
        base = f"{base}-{n}"
    return base


def nombre_por_tokens(lucide: str):
    tokens = lucide.split("-")
    faltan = [t for t in tokens if t not in GLOSARIO]
    if faltan:
        return None, faltan
    return "-".join(GLOSARIO[t] for t in tokens), []


def alta(m: dict, datos: dict, lucide: str, nombre: str, grupo: str) -> dict | None:
    if numero_de(m, lucide):
        return None
    if grupo not in GRUPOS:
        raise SystemExit(f"grupo desconocido: {grupo} (válidos: {', '.join(GRUPOS)})")
    choque = next((i for i in m["iconos"]
                   if i.get("estado", "activo") == "activo" and i["nombre"] == nombre), None)
    if choque:
        raise SystemExit(f"ya existe {choque['id']} con el nombre «{nombre}» "
                         f"(lucide:{choque['lucide']}); pasa un --nombre distinto")
    cuerpo, real = cuerpo_de(datos, lucide)
    numero = max((i["numero"] for i in m["iconos"]), default=0) + 1
    slug = slug_de(m, nombre)
    archivo = f"{numero:0{DIGITOS}d}-{slug}.svg"
    spdx = m["licencia"]["spdx"]
    (DIR / archivo).write_text(svg_archivo(numero, nombre, cuerpo, real, spdx), encoding="utf-8")
    entradas_alias = sorted(a for a, v in datos.get("aliases", {}).items() if v.get("parent") == real)
    e = {
        "numero": numero,
        "id": f"{PREFIJO}{numero:0{DIGITOS}d}",
        "lucide": real,
        "solicitado": lucide if lucide != real else None,
        "nombre": nombre,
        "archivo": archivo,
        "grupo": grupo,
        "grupoNombre": GRUPOS[grupo],
        "alias": entradas_alias,
        "licencia": spdx,
        "hash": hash_de(cuerpo),
        "estado": "activo",
    }
    if lucide == real:
        del e["solicitado"]
    m["iconos"].append(e)
    return e


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def sembrar(argv):
    datos = descargar()
    DIR.mkdir(parents=True, exist_ok=True)
    m = cargar()
    nuevos = 0
    for lucide, nombre, grupo in NUCLEO:
        if alta(m, datos, lucide, nombre, grupo):
            nuevos += 1
    guardar(m)
    print(f"sembrado: {nuevos} iconos nuevos · total {m['total']} · siguiente {PREFIJO}{m['siguiente']:0{DIGITOS}d}")
    sprite(None)
    catalogo(None)


def anadir(argv):
    if not argv:
        raise SystemExit("uso: iconos.py anadir lucide:house [lucide:key …] [--grupo mapas] [--nombre nombre-es]")
    grupo = "varios"
    if "--grupo" in argv:
        i = argv.index("--grupo")
        grupo = argv[i + 1]
        del argv[i:i + 2]
    nombre_forzado = None
    if "--nombre" in argv:
        i = argv.index("--nombre")
        nombre_forzado = argv[i + 1]
        del argv[i:i + 2]
    if nombre_forzado and len(argv) > 1:
        raise SystemExit("--nombre vale para UN icono: añade de uno en uno para no bautizar "
                         "todos con el mismo nombre")
    datos = descargar()
    m = cargar()
    for bruto in argv:
        lucide = bruto.split(":", 1)[1] if ":" in bruto else bruto
        nombre, faltan = nombre_por_tokens(lucide)
        if nombre_forzado:
            nombre = nombre_forzado
        elif faltan:
            raise SystemExit(
                f"«{lucide}» tiene tokens sin traducir: {', '.join(faltan)}. "
                f"Añádelos a GLOSARIO en scripts/iconos.py o pasa --nombre <castellano>.")
        e = alta(m, datos, lucide, nombre, grupo)
        print(f"  {'+' if e else '='} {lucide} → " +
              (f"{e['id']} {e['nombre']} ({e['archivo']})" if e else "ya estaba"))
    guardar(m)
    sprite(None)
    catalogo(None)


def retirar(argv):
    if not argv:
        raise SystemExit("uso: iconos.py retirar 042 [043 …]")
    m = cargar()
    for bruto in argv:
        n = int(re.sub(r"\D", "", bruto))
        e = next((i for i in m["iconos"] if i["numero"] == n), None)
        if not e:
            raise SystemExit(f"no existe el número {n:0{DIGITOS}d}")
        e["estado"] = "retirado"
        if e.get("archivo"):
            (DIR / e["archivo"]).unlink(missing_ok=True)
        m["numerosRetirados"].append({"numero": n, "id": e["id"], "lucide": e["lucide"],
                                      "nombre": e["nombre"], "motivo": "retirado"})
        print(f"  − {e['id']} {e['nombre']} retirado (el número no se reutiliza)")
    guardar(m)
    sprite(None)
    catalogo(None)


def listar(argv):
    m = cargar()
    grupo = None
    if "--grupo" in argv:
        grupo = argv[argv.index("--grupo") + 1]
    for i in m["iconos"]:
        if i.get("estado", "activo") != "activo":
            continue
        if grupo and i["grupo"] != grupo:
            continue
        print(f"{i['id']}  {i['nombre']:<28} {i['grupo']:<14} lucide:{i['lucide']}")
    print(f"\n{m['total']} iconos · siguiente {PREFIJO}{m['siguiente']:0{DIGITOS}d}")


def sprite(argv) -> str:
    m = cargar()
    piezas = []
    for i in m["iconos"]:
        if i.get("estado", "activo") != "activo":
            continue
        ruta = DIR / i["archivo"]
        if not ruta.exists():
            raise SystemExit(f"falta el fichero {ruta.name}: regenera con `iconos.py sembrar`")
        cuerpo = extraer_cuerpo(ruta.read_text(encoding="utf-8"))
        piezas.append(f'<symbol id="{i["id"]}" viewBox="0 0 24 24" '
                      f'data-nombre="{i["nombre"]}">{cuerpo}</symbol>')
    texto = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true">\n'
        f"<!-- Aurora · sprite de iconos numerados · Lucide ({m['licencia']['spdx']}) · "
        f"{m['total']} símbolos · generado por scripts/iconos.py -->\n"
        + "\n".join(piezas) + "\n</svg>\n"
    )
    SPRITE.write_text(texto, encoding="utf-8")
    print(f"sprite: {len(piezas)} símbolos → iconos/sprite.svg ({len(texto) // 1024} KB)")
    return texto


def extraer_cuerpo(svg: str) -> str:
    m = re.search(r">\s*(<!--.*?-->\s*)?(.*)</svg>", svg, re.S)
    if not m:
        raise SystemExit("SVG sin cuerpo reconocible")
    return re.sub(r"\s+", " ", m.group(2)).strip()


# ---------------------------------------------------------------------------
# Catálogo HTML (generado: no se edita a mano)
# ---------------------------------------------------------------------------
def catalogo(argv) -> str:
    m = cargar()
    vivos = [i for i in m["iconos"] if i.get("estado", "activo") == "activo"]
    version = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))["version"]

    fichas = []
    for i in vivos:
        ruta = DIR / i["archivo"]
        cuerpo = extraer_cuerpo(ruta.read_text(encoding="utf-8"))
        buscar = " ".join([i["id"], i["nombre"], i["lucide"], i["grupoNombre"],
                           " ".join(i.get("alias", []))]).lower()
        fichas.append(
            '<li class="nz-article nz-article--bordered" '
            f'data-icono="{i["id"]}" data-buscar="{buscar}">\n'
            '  <div class="nz-cluster nz-cluster--between">'
            f'<span class="nz-icon-tile">{svg_en_linea(cuerpo)}</span>'
            f'<button class="nz-btn nz-btn--ghost nz-btn--sm" type="button" '
            f'data-copiar="{i["id"]}" aria-label="Copiar el código de {i["id"]}">'
            f'Copiar {i["numero"]:0{DIGITOS}d}</button>'
            "</div>\n"
            f'  <p class="nz-text--peso-fuerte">{i["nombre"]}</p>\n'
            f'  <p class="nz-text--small nz-text--muted">{i["id"]} · {i["grupoNombre"]}</p>\n'
            f'  <p class="nz-text--small nz-text--mono">{i["lucide"]}</p>\n'
            "</li>")

    grupos = []
    for clave, nombre in GRUPOS.items():
        n = sum(1 for i in vivos if i["grupo"] == clave)
        if n:
            grupos.append(f'<span class="nz-badge nz-badge--outline nz-badge--sm">{nombre} · {n}</span>')

    html = f"""<!DOCTYPE html>
<html lang="es" data-nz-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Aurora · Iconos numerados · {m['total']} iconos</title>
<meta name="description" content="Repositorio de iconos numerados de Aurora: {m['total']} iconos Lucide ({m['licencia']['spdx']}) con número estable nz-i-NNN, sprite y manifiesto.">
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="../packs/p1-layout.css">
<link rel="stylesheet" href="../packs/p3-typography.css">
<link rel="stylesheet" href="../packs/p4-actions.css">
<link rel="stylesheet" href="../packs/p5-forms.css">
<link rel="stylesheet" href="../packs/p6-feedback.css">
<link rel="stylesheet" href="../packs/p9-media.css">
<script src="../js/iconos.js" defer></script>
</head>
<body class="nz">
<main class="nz-container" id="contenido">
  <header class="nz-stack">
    <p class="nz-text--small nz-text--muted">Aurora v{version} · colección {m['coleccion']} · licencia {m['licencia']['spdx']}</p>
    <h1 class="nz-h1">Iconos numerados</h1>
    <p class="nz-lead">Cada icono tiene un número estable —<span class="nz-text--accent-soft">{PREFIJO}001</span>, {PREFIJO}042— que no se reutiliza nunca. El número es la referencia; el nombre es la comodidad. Todos son SVG de 24×24 con el color y el grosor del sistema.</p>
    <div class="nz-cluster">{''.join(grupos)}</div>
    <div class="nz-field">
      <label class="nz-field__label" for="buscarIcono">Buscar por número, nombre o id de Lucide</label>
      <input class="nz-input nz-input--search" id="buscarIcono" type="search" placeholder="042, hogar, lucide:house…" autocomplete="off">
      <p class="nz-field__help" id="cuentaIconos">{m['total']} iconos · todos visibles</p>
    </div>
  </header>

  <ul class="nz-dash-grid nz-dash-grid--4" id="rejillaIconos" role="list">
{chr(10).join(fichas)}
  </ul>

  <section class="nz-stack">
    <h2 class="nz-h2">Cómo se usa</h2>
    <p>En línea, copiando el SVG del fichero (lo que hace esta página):</p>
    <pre class="nz-code nz-code--block">&lt;svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true"&gt;…cuerpo del icono…&lt;/svg&gt;</pre>
    <p>Por sprite, una sola petición para todos:</p>
    <pre class="nz-code nz-code--block">&lt;svg class="nz-icon" aria-hidden="true"&gt;&lt;use href="iconos/sprite.svg#{PREFIJO}042"/&gt;&lt;/svg&gt;</pre>
    <p>Y por número, desde el manifiesto:</p>
    <pre class="nz-code nz-code--block">python3 -c "import json;m=json.load(open('iconos/iconos.json'));print([i for i in m['iconos'] if i['numero']==42][0])"</pre>
    <p class="nz-text--small nz-text--muted">Iconos de <a href="https://lucide.dev">Lucide</a> ({m['licencia']['spdx']}), {m['licencia']['atribucion']}. Manifiesto: <span class="nz-text--mono">iconos/iconos.json</span> · sprite: <span class="nz-text--mono">iconos/sprite.svg</span>.</p>
  </section>
</main>
<footer class="nz-container">
  <p class="nz-text--small nz-text--muted">Hecho con ❤️ por David Antizar</p>
</footer>
</body>
</html>
"""
    CATALOGO.write_text(html, encoding="utf-8")
    print(f"catálogo: {len(vivos)} iconos → iconos/index.html ({len(html) // 1024} KB)")
    return html


def svg_en_linea(cuerpo: str) -> str:
    return ('<svg class="nz-icon nz-icon--xl" viewBox="0 0 24 24" aria-hidden="true">'
            f"{cuerpo}</svg>")


def todo(argv):
    sprite(argv)
    catalogo(argv)



def verificar_generados(argv):
    """Comprueba que sprite.svg e index.html son exactamente lo que genera el script.

    Se genera en un directorio temporal y se comparan los bytes: si alguien editó
    el catálogo a mano, esto lo caza (el catálogo no es documentación, es salida).
    """
    import contextlib
    import io
    import tempfile

    global SPRITE, CATALOGO
    tmp = Path(tempfile.mkdtemp(prefix="aurora-iconos-"))
    real_sprite, real_catalogo = SPRITE, CATALOGO
    SPRITE, CATALOGO = tmp / "sprite.svg", tmp / "index.html"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sprite(None)
            catalogo(None)
        fallos = []
        for generado, real, nombre in ((SPRITE, real_sprite, "iconos/sprite.svg"),
                                       (CATALOGO, real_catalogo, "iconos/index.html")):
            if not real.exists():
                fallos.append(f"falta {nombre}: ejecuta python3 scripts/iconos.py todo")
            elif generado.read_bytes() != real.read_bytes():
                fallos.append(f"{nombre} desincronizado: ejecuta python3 scripts/iconos.py todo")
    finally:
        SPRITE, CATALOGO = real_sprite, real_catalogo
    if fallos:
        for f in fallos:
            print(f"FALLO {f}")
        return 1
    print("sprite.svg y index.html coinciden con el manifiesto")
    return 0


COMANDOS = {
    "sembrar": sembrar,
    "anadir": anadir,
    "retirar": retirar,
    "listar": listar,
    "sprite": sprite,
    "catalogo": catalogo,
    "todo": todo,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "ayuda"):
        print(__doc__)
        return 0
    if sys.argv[1] == "--check":
        return verificar_generados(sys.argv[2:])
    comando = sys.argv[1]
    if comando not in COMANDOS:
        raise SystemExit(f"comando desconocido: {comando}\n\n{__doc__}")
    COMANDOS[comando](sys.argv[2:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
