/* ============================================================================
   aurora-openui.js — Generative UI con Aurora
   OpenUI Lang como lenguaje · Aurora como implementación visual
   ----------------------------------------------------------------------------
   · Vanilla: cero dependencias de build, cero React.
   · El parser oficial (@openuidev/lang-core, MIT) se carga por ESM desde CDN
     la primera vez. Si no hay red, cae a un parser local del mismo subconjunto
     (marcado como «local» en `AuroraOpenUI.modo`): el dato se pinta igual.
   · El render emite SOLO clases del censo de Aurora. Ni una fuera de
     components.json — lo comprueba scripts/auditar-openui.py.
   · Sin gradientes, sin backdrop-filter, sin !important: lo que sale de aquí
     pasa `python3 scripts/auditar-uso.py` como cualquier página del sistema.
   ========================================================================== */
(function (global) {
  "use strict";

  var VERSION = "1.0.0";
  var CDN_LANG_CORE = "https://cdn.jsdelivr.net/npm/@openuidev/lang-core@1.0.1/+esm";
  var SPEC_URL = "openui/aurora.spec.json";

  /* ---------- utilidades ------------------------------------------------- */
  var ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"']/g, function (c) { return ESCAPES[c]; });
  }
  function cl() {
    var out = [];
    for (var i = 0; i < arguments.length; i++) if (arguments[i]) out.push(arguments[i]);
    return out.join(" ");
  }
  function num(v, def) {
    var n = typeof v === "number" ? v : parseFloat(String(v).replace(",", "."));
    return isFinite(n) ? n : (def || 0);
  }
  function pct(v, max) {
    var n = max > 0 ? (num(v) / max) * 100 : 0;
    return Math.max(0, Math.min(100, Math.round(n * 10) / 10));
  }
  function list(v) {
    if (Array.isArray(v)) return v;
    if (v == null || v === "") return [];
    return [v];
  }
  /* A04 · política de protocolos del enlace (plan §6.2.5): escapar comillas no
     rechaza esquemas no permitidos. Solo navegación explícita: relativos, #anclas,
     http(s), mailto y tel. javascript:/vbscript:/data: (no-imagen) → NO admisible:
     el renderer no pinta el enlace (el compilador además rechaza el programa). */
  function urlAdmitida(u) {
    var s = String(u == null ? "" : u).trim();
    if (!s) return false;
    return !/^(?:javascript|vbscript|data(?![a-z]*\/[sp]v?g))/i.test(s);
  }
  function fila(v) { return Array.isArray(v) ? v.map(function (x) { return String(x == null ? "" : x); }) : []; }
  /* El enum habla castellano; el modificador del censo habla inglés. Tabla explícita
     para que `auditar-openui.py` pueda exigir que cada valor esté tratado. */
  var TENDENCIA = { "sube": "up", "baja": "down", "plano": "flat" };

  /* ---------- renderizadores: un componente = markup del censo ----------- */
  /* Cada función recibe (props, ctx) y devuelve HTML. ctx.nodos() pinta hijos. */
  var R = {};

  R.Pagina = function (p, ctx) {
    return '<div class="' + cl("nz-container", p.ancho === "app" && "nz-container--app") + '">' + ctx.nodos(p.children) + "</div>";
  };

  R.Seccion = function (p, ctx) {
    // densidad "normal" (por defecto): sin modificador — declaración explícita para el auditor
    var densidad = p.densidad === "normal" || !p.densidad ? "" : p.densidad === "compacta" ? "nz-section--compact" : "";
    return '<section class="' + cl("nz-section", p.borde !== false && "nz-section--bordered", densidad) + '">' +
      // El rótulo es una pastilla pequeña, no un titular: dos h2 del mismo tamaño
      // (rótulo + titular) competían en la misma sección y eso es ruido, no jerarquía.
      (p.titulo ? '<span class="nz-lbl">' + esc(p.titulo) + "</span>" : "") + ctx.nodos(p.children) + "</section>";
  };

  R.Pila = function (p, ctx) {
    return '<div class="' + cl("nz-stack", p.hueco && "nz-stack--" + p.hueco) + '">' + ctx.nodos(p.children) + "</div>";
  };

  /* Fila = cluster, no row: un grupo de botones/chips debe medir lo que mide,
     no estirarse al 100 % en móvil (el row es para campos y bloques). */
  R.Fila = function (p, ctx) {
    var hueco = p.hueco === "compacto" ? "compact" : p.hueco === "amplio" ? "spacious" : "";
    return '<div class="' + cl("nz-cluster", hueco && "nz-cluster--" + hueco) + '">' + ctx.nodos(p.children) + "</div>";
  };

  R.Rejilla = function (p, ctx) {
    var col = p.columnas === "2" ? "2" : p.columnas === "4" ? "4" : "ajuste";
    return '<div class="' + cl("nz-dash-grid", "nz-dash-grid--" + col) + '">' + ctx.nodos(p.children) + "</div>";
  };

  R.DosColumnas = function (p, ctx) {
    var rep = { "2-1": "nz-split--2-1", "40-60": "nz-split--40-60", "60-40": "nz-split--60-40" }[p.reparto] || "";
    return '<div class="' + cl("nz-split", rep) + '">' +
      '<div class="nz-stack nz-stack--sm">' + ctx.nodos(p.izquierda) + "</div>" +
      '<div class="nz-stack nz-stack--sm">' + ctx.nodos(p.derecha) + "</div></div>";
  };

  R.Hero = function (p, ctx) {
    var tono = p.tono === "brand" ? "nz-hero-bleed--brand" : "";
    // densidad "normal" (por defecto): sin modificador — declaración explícita para el auditor
    var densidad = p.densidad === "normal" || !p.densidad ? "" : p.densidad === "compacto" ? "nz-hero-bleed--compact" : "";
    // banda a sangre: dentro, la tinta la pone el contenedor (brand = invertida).
    return '<div class="' + cl("nz-hero-bleed", tono, densidad) + '">' + ctx.nodos(p.children) + "</div>";
  };

  R.Tarjeta = function (p, ctx) {
    return '<article class="' + cl("nz-article", p.borde !== false && "nz-article--bordered") + '">' +
      (p.titulo ? '<h3 class="nz-h3">' + esc(p.titulo) + "</h3>" : "") + ctx.nodos(p.children) + "</article>";
  };

  R.Titular = function (p) {
    var nivel = String(p.nivel || "2");
    var tono = p.tono === "acento" ? "--accent" : p.tono === "marca" ? "--brand" : "";
    if (nivel === "display") {
      // h1 de apertura: 4xl + tracking apretado. Sin modificador de tono
      // (el tono no tiene forma para display); la tinta la pone el contenedor.
      return '<h1 class="nz-display">' + esc(p.texto) + "</h1>";
    }
    if (nivel === "1") {
      return '<h1 class="' + cl("nz-h1", tono && "nz-h1" + tono) + '">' + esc(p.texto) + "</h1>";
    }
    if (nivel === "3") {
      return '<h3 class="' + cl("nz-h4") + '">' + esc(p.texto) + "</h3>";
    }
    return '<h2 class="' + cl("nz-h2", tono && "nz-h2" + tono) + '">' + esc(p.texto) + "</h2>";
  };

  R.Entradilla = function (p) {
    var tono = p.tono === "acento" ? "nz-lead--accent" : p.tono === "marca" ? "nz-lead--brand" : "";
    return '<p class="' + cl("nz-lead", p.tamano && "nz-lead--" + p.tamano, tono) + '">' + esc(p.texto) + "</p>";
  };

  R.Texto = function (p) { return "<p>" + esc(p.texto) + "</p>"; };

  R.Lista = function (p) {
    var estilo = { "check": "nz-list--check", "num": "nz-list--numeric", "dividida": "nz-list--divided" }[p.estilo] || "";
    var items = list(p.items).map(function (t) {
      return '<li class="nz-list__item">' + esc(t) + "</li>";
    }).join("");
    return '<ul class="' + cl("nz-list", estilo) + '">' + items + "</ul>";
  };

  R.Cifra = function (p) {
    var tono = { "marca": "nz-num--brand", "acento": "nz-num--accent", "exito": "nz-num--success", "peligro": "nz-num--danger" }[p.tono] || "";
    return '<span class="' + cl("nz-num", tono, p.tamano && "nz-num--" + p.tamano) + '">' + esc(p.valor) + "</span>";
  };

  R.Separador = function (p) {
    if (p.etiqueta) {
      return '<hr class="nz-divider nz-divider--label" data-label="' + esc(p.etiqueta) + '">';
    }
    return '<hr class="' + cl("nz-divider", p.trazo === "discontinuo" && "nz-divider--dashed") + '">';
  };

  R.Icono = function (p) {
    var n = String(p.numero == null ? "" : p.numero).replace(/[^0-9]/g, "");
    if (!n) return "";
    while (n.length < 3) n = "0" + n;
    // decorativo (aria-hidden): el significado lo lleva el texto de al lado.
    return '<svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<use href="iconos/sprite.svg#nz-i-' + n + '"></use></svg>';
  };

  R.Kpi = function (p, ctx) {
    var tono = p.tono === "acento" ? "nz-kpi--accent" : p.tono === "marca" ? "nz-kpi--brand" : "";
    var claseValor = p.tono === "acento" ? "nz-kpi__value--accent" : p.tono === "marca" ? "nz-kpi__value--brand" : "";
    var tendencia = TENDENCIA[p.tendencia] ? "nz-kpi__delta--" + TENDENCIA[p.tendencia] : "";
    return '<div class="' + cl("nz-kpi", tono, p.tamano && "nz-kpi--" + p.tamano) + '">' +
      '<span class="nz-kpi__label">' + esc(p.etiqueta) + "</span>" +
      '<span class="' + cl("nz-kpi__value", claseValor) + '">' + esc(p.valor) + "</span>" +
      (p.delta ? '<span class="' + cl("nz-kpi__delta", tendencia) + '">' + esc(p.delta) + "</span>" : "") +
      "</div>";
  };

  /* Contador de toasts/tramas: ids únicos por instancia (dos patrones con el
     mismo id y distinto color se pisarían: el primero del documento gana). */
  var nzTramaN = 0;

  R.Toast = function (p) {
    var tono = { "marca": "nz-toast--brand", "acento": "nz-toast--accent", "exito": "nz-toast--success", "aviso": "nz-toast--warning", "peligro": "nz-toast--error", "info": "nz-toast--info" }[p.tono] || "";
    var icono = { "exito": "036", "peligro": "016", "aviso": "072", "marca": "150", "acento": "150", "info": "074" }[p.tono] || "074";
    return '<div class="' + cl("nz-toast", tono, p.temporal === true && "nz-toast--temporal", "is-on") + '">' +
      '<span class="nz-toast__icon"><svg class="nz-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="iconos/sprite.svg#nz-i-' + icono + '"></use></svg></span>' +
      (p.titulo ? '<span class="nz-toast__title">' + esc(p.titulo) + "</span>" : "") +
      esc(p.texto) +
      (p.accion ? '<button class="nz-toast__action">' + esc(p.accion) + "</button>" : "") +
      (p.temporal === true ? '<span class="nz-toast__progreso"></span>' : "") +
      "</div>";
  };

  R.Contador = function (p) {
    var v = String(p.valor == null ? "" : p.valor);
    return '<span class="' + cl("nz-contador", p.tamano === "sm" && "nz-contador--sm", p.tamano === "lg" && "nz-contador--lg") + '">' +
      '<span class="nz-contador__valor">' + esc(v) + "</span>" +
      '<span class="nz-contador__destino" aria-hidden="true">' + esc(v) + "</span></span>";
  };

  R.Actividad = function (p) {
    var acciones = list(p.acciones);
    var horas = list(p.horas);
    var detalles = list(p.detalles);
    var estados = list(p.estados);
    var destinos = list(p.destinos);
    var filas = acciones.map(function (a, i) {
      var estado = estados[i] || "";
      var is = estado === "hecho" ? "is-done" : estado === "error" ? "is-error" : estado === "curso" ? "is-active" : "";
      var cuerpo = '<span class="nz-actividad__cuerpo"><span class="nz-actividad__texto">' + esc(a) + "</span>" +
        (detalles[i] ? '<span class="nz-actividad__detalle">' + esc(detalles[i]) + "</span>" : "") + "</span>";
      var interior = (horas[i] ? '<span class="nz-actividad__hora">' + esc(horas[i]) + "</span>" : "") + cuerpo;
      var actual = is === "is-active" ? ' aria-current="step"' : "";
      var destino = destinos[i] && urlAdmitida(destinos[i]) ? destinos[i] : "";
      if (destino) {
        return '<a class="' + cl("nz-actividad__fila", is) + '" href="' + esc(destino) + '"' + actual + ">" + interior + "</a>";
      }
      return '<div class="' + cl("nz-actividad__fila", is) + '"' + actual + ">" + interior + "</div>";
    }).join("");
    return '<div class="nz-actividad">' + filas + "</div>";
  };

  R.Tabla = function (p) {
    var columnas = list(p.columnas).map(function (c) { return String(c); });
    var numCols = String(p.numericas || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
    function esNum(c) { return numCols.indexOf(c) !== -1; }
    var thead = "<thead><tr>" + columnas.map(function (c) {
      return '<th class="' + cl(esNum(c) && "nz-table__num nz-table__right") + '"' +
        (esNum(c) ? ' style="text-align:right"' : "") + ">" + esc(c) + "</th>";
    }).join("") + "</tr></thead>";
    var tbody = "<tbody>" + list(p.filas).map(function (f) {
      var celdas = fila(f);
      return "<tr>" + columnas.map(function (c, i) {
        var dato = celdas[i] == null ? "" : celdas[i];
        return "<td" + (p.apilable ? ' data-etiqueta="' + esc(c) + '"' : "") +
          (esNum(c) ? ' class="nz-table__num nz-table__right"' : "") + ">" + esc(dato) + "</td>";
      }).join("") + "</tr>";
    }).join("") + "</tbody>";
    var tabla = '<table class="' + cl("nz-table",
      p.apilable && "nz-table--apilable",
      p.densidad === "compacta" ? "nz-table--compact" : "nz-table--comfortable",
      p.rayada && "nz-table--striped") + '">' + thead + tbody + "</table>";
    return '<div class="' + cl("nz-table-wrap", p.apilable && "nz-table-wrap--apilable") + '">' + tabla + "</div>";
  };

  R.Barras = function (p) {
    var etiquetas = list(p.etiquetas);
    var valores = list(p.valores).map(function (v) { return num(v); });
    var max = Math.max.apply(null, valores.concat([0])) || 1;
    var tono = p.tono === "acento" ? "nz-chart-bar__bar--accent" : "nz-chart-bar__bar--brand";
    var horizontal = p.horizontal === true;
    var cols = valores.map(function (v, i) {
      var etiqueta = etiquetas[i] == null ? "" : etiquetas[i];
      var barra = '<div class="' + cl("nz-chart-bar__bar", tono) + '" style="' +
        (horizontal ? "width:" : "height:") + pct(v, max) + '%"></div>';
      return '<div class="nz-chart-bar__col">' +
        (horizontal ? "" : '<span class="nz-chart-bar__value">' + esc(v.toLocaleString("es-ES")) + "</span>") +
        barra + '<span class="nz-chart-bar__label">' + esc(etiqueta) + "</span></div>";
    }).join("");
    /* Sin <figure class="nz-chart">: el componente casi siempre vive dentro de una
       Tarjeta y dos superficies anidadas hacen un muro. 5rem por defecto; `lg` solo
       para el gráfico protagonista. */
    return '<div class="' +
      cl("nz-chart-bar", p.tamano === "lg" ? "nz-chart-bar--lg" : "nz-chart-bar--sm", horizontal && "nz-chart-bar--horizontal") +
      '">' + cols + "</div>";
  };

  R.TablaBarras = function (p) {
    var nombres = list(p.nombres);
    var valores = list(p.valores).map(function (v) { return num(v); });
    var textos = list(p.textos);
    var max = Math.max.apply(null, valores.concat([0])) || 1;
    var cols = nombres.map(function (n, i) {
      var texto = textos[i] != null ? textos[i] : valores[i].toLocaleString("es-ES");
      return '<div class="nz-chart-tablebar__row">' +
        '<span class="nz-chart-tablebar__name">' + esc(n) + "</span>" +
        '<span class="nz-chart-tablebar__track"><span class="nz-chart-tablebar__bar" style="width:' +
        pct(valores[i], max) + '%"></span></span>' +
        '<span class="nz-chart-tablebar__num">' + esc(texto) + "</span></div>";
    }).join("");
    return '<div class="nz-chart-tablebar">' + cols + "</div>";
  };

  R.Objetivo = function (p) {
    var real = num(p.real), meta = num(p.meta);
    var escala = Math.max(real, meta) * 1.5 || 1;
    var tono = p.tono === "acento" ? "nz-bullet__value--accent" : p.tono === "exito" ? "nz-bullet__value--success" : "nz-bullet__value--brand";
    var texto = p.texto || (real.toLocaleString("es-ES") + " / " + meta.toLocaleString("es-ES"));
    return '<div class="nz-bullet">' +
      '<span class="nz-bullet__label">' + esc(p.etiqueta) + "</span>" +
      '<div class="nz-bullet__track"><span class="nz-bullet__ranges"></span>' +
      '<span class="nz-bullet__value ' + tono + '" style="width:' + pct(real, escala) + '%"></span>' +
      '<span class="nz-bullet__target" style="left:' + pct(meta, escala) + '%"></span></div>' +
      '<span class="nz-bullet__num">' + esc(texto) + "</span></div>";
  };

  R.MiniTendencia = function (p) {
    var tendencia = TENDENCIA[p.tendencia] ? "nz-chart-stat__delta--" + TENDENCIA[p.tendencia] : "";
    return '<div class="nz-chart-stat">' +
      '<span class="nz-chart-stat__label">' + esc(p.etiqueta) + "</span>" +
      '<span class="nz-chart-stat__value">' + esc(p.valor) + "</span>" +
      (p.delta ? '<span class="' + cl("nz-chart-stat__delta", tendencia) + '">' + esc(p.delta) + "</span>" : "") +
      "</div>";
  };

  R.Anillo = function (p) {
    var v = Math.max(0, Math.min(100, num(p.valor)));
    var tono = p.tono === "acento" ? "nz-chart-donut__seg--accent" : "nz-chart-donut__seg--brand";
    var trama = p.tramas === true;
    var claseSeg = tono;
    var extra = "";
    var pid = "";
    if (trama) {
      nzTramaN += 1;
      pid = "tramaDiag-" + nzTramaN;
      claseSeg = "nz-trama--diagonal " + tono;
      extra = ' style="stroke: url(#' + pid + ')"';
    }
    return '<div class="' + cl("nz-chart-donut", p.tamano === "lg" ? "nz-chart-donut--lg" : "nz-chart-donut--sm") + '">' +
      '<svg class="nz-chart-donut__svg" viewBox="0 0 42 42" role="img" aria-label="' +
      esc((p.etiqueta || "Progreso") + ": " + v + " por ciento") + '">' +
      (trama ? '<defs><pattern id="' + pid + '" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0,4 L4,0" stroke="currentColor" stroke-width="1.2"/></pattern></defs>' : "") +
      '<circle class="nz-chart-donut__track" cx="21" cy="21" r="15.9"></circle>' +
      '<circle class="nz-chart-donut__seg ' + claseSeg + '" cx="21" cy="21" r="15.9" stroke-dasharray="' +
      v + " " + (100 - v) + '"' + extra + '></circle></svg>' +
      '<div class="nz-chart-donut__center"><span class="nz-chart-donut__value">' + v + "%</span>" +
      (p.etiqueta ? '<span class="nz-chart-donut__label">' + esc(p.etiqueta) + "</span>" : "") +
      "</div></div>";
  };

  R.Progreso = function (p) {
    var v = Math.max(0, Math.min(100, num(p.valor)));
    return '<div class="nz-progress">' +
      '<div class="nz-progress__bar" style="width:' + v + '%"></div>' +
      (p.etiqueta ? '<span class="nz-progress__caption">' + esc(p.etiqueta) + "</span>" : "") +
      "</div>";
  };

  R.Boton = function (p) {
    var tono = { "primario": "nz-btn--primary", "acento": "nz-btn--accent", "suave": "nz-btn--soft", "contorno": "nz-btn--outline", "fantasma": "nz-btn--ghost" }[p.tono] || "";
    var clase = cl("nz-btn", tono, p.tamano && "nz-btn--" + p.tamano, p.bloque && "nz-btn--block");
    if (p.href && urlAdmitida(p.href)) {
      return '<a class="' + clase + '" href="' + esc(p.href) + '">' + esc(p.texto) + "</a>";
    }
    // sin href o con esquema inadmisible: botón declarativo, nunca un enlace tóxico
    return '<button type="button" class="' + clase + '">' + esc(p.texto) + "</button>";
  };

  R.Etiqueta = function (p) {
    var tono = { "marca": "nz-badge--brand", "acento": "nz-badge--accent", "exito": "nz-badge--success", "aviso": "nz-badge--warning", "peligro": "nz-badge--danger", "neutro": "nz-badge--neutral" }[p.tono] || "";
    var forma = p.forma === "contorno" ? "nz-badge--outline" : p.forma === "punto" ? "nz-badge--dot" : "";
    return '<span class="' + cl("nz-badge", tono, forma) + '"><i></i>' + esc(p.texto) + "</span>";
  };

  R.Chip = function (p) {
    var tono = { "marca": "nz-chip--brand", "acento": "nz-chip--accent", "exito": "nz-chip--success", "peligro": "nz-chip--danger" }[p.tono] || "";
    return '<span class="' + cl("nz-chip", tono) + '">' + esc(p.texto) + "</span>";
  };

  R.Aviso = function (p) {
    var tono = { "info": "nz-alert--info", "exito": "nz-alert--success", "aviso": "nz-alert--warning", "peligro": "nz-alert--danger", "neutro": "nz-alert--neutral" }[p.tono] || "nz-alert--info";
    var icono = { "info": "i", "exito": "ok", "aviso": "!", "peligro": "x", "neutro": "·" }[p.tono || "info"];
    return '<div class="' + cl("nz-alert", tono, p.contorno && "nz-alert--outline") + '" role="status">' +
      '<span class="nz-alert__icon" aria-hidden="true">' + icono + "</span>" +
      '<div class="nz-alert__body"><span class="nz-alert__title">' + esc(p.titulo) + "</span>" +
      '<span class="nz-alert__msg">' + esc(p.mensaje) + "</span></div></div>";
  };

  R.Nota = function (p) {
    var tono = { "nota": "nz-callout--note", "consejo": "nz-callout--tip", "aviso": "nz-callout--warn", "peligro": "nz-callout--danger", "marca": "nz-callout--brand", "acento": "nz-callout--accent", "exito": "nz-callout--success" }[p.tono || "nota"];
    return '<div class="nz-callout ' + tono + '"><p>' + esc(p.texto) + "</p></div>";
  };

  R.Pestanas = function (p) {
    var activa = p.activa == null ? 0 : num(p.activa);
    var tabs = list(p.pestanas).map(function (t, i) {
      return '<button type="button" class="nz-tabs__tab"' + (i === activa ? ' aria-selected="true"' : "") + ">" + esc(t) + "</button>";
    }).join("");
    return '<div class="' + cl("nz-tabs", p.forma === "pastilla" && "nz-tabs--pill") + '" role="tablist">' + tabs + "</div>";
  };

  R.Segmentado = function (p) {
    var activa = p.activa == null ? 0 : num(p.activa);
    var opciones = list(p.opciones).map(function (o, i) {
      return '<button type="button"' + (i === activa ? ' aria-selected="true"' : ' aria-selected="false"') + ">" + esc(o) + "</button>";
    }).join("");
    return '<div class="nz-segmented">' + opciones + "</div>";
  };

  R.Pasos = function (p) {
    var actual = p.actual == null ? 0 : num(p.actual);
    var pasos = list(p.pasos).map(function (s, i) {
      var estado = i < actual ? " is-done" : i === actual ? " is-active" : "";
      return '<li class="nz-stepper__step' + estado + '"><span class="nz-stepper__num">' + (i + 1) + "</span>" + esc(s) + "</li>";
    }).join("");
    return '<ol class="nz-stepper">' + pasos + "</ol>";
  };

  R.Navegacion = function (p) {
    var urls = list(p.urls);
    var enlaces = list(p.enlaces).map(function (e, i) {
      var destino = urls[i] ? urls[i] : "#";
      if (!urlAdmitida(destino)) {
        return '<span class="nz-navbar__link">' + esc(e) + "</span>";
      }
      return '<a class="nz-navbar__link" href="' + esc(destino) + '">' + esc(e) + "</a>";
    }).join("");
    // B03 · homeRoute: la marca enlaza al inicio del producto. Prioridad:
    // p.inicio (el programa) → data-nz-inicio de la página → sin enlace.
    var inicio = p.inicio;
    if (!inicio && typeof document !== "undefined" && document.documentElement) {
      inicio = document.documentElement.getAttribute("data-nz-inicio") || "";
    }
    var marca = inicio && urlAdmitida(inicio)
      ? '<a class="nz-navbar__brand" href="' + esc(inicio) + '"><i></i>' + esc(p.marca) + "</a>"
      : '<span class="nz-navbar__brand"><i></i>' + esc(p.marca) + "</span>";
    return '<div class="nz-navbar nz-navbar--bordered">' + marca +
      '<span class="nz-navbar__links">' + enlaces + "</span></div>";
  };

  R.Campo = function (p) {
    var id = "nzc-" + Math.random().toString(36).slice(2, 8);
    var tipo = { "numero": "number", "email": "email", "fecha": "date", "busqueda": "search" }[p.tipo] || "text";
    return '<label class="nz-field" for="' + id + '">' +
      '<span class="nz-field__label">' + esc(p.etiqueta) + (p.requerido ? '<span class="nz-field__label--req" aria-hidden="true">*</span>' : "") + "</span>" +
      '<input class="' + cl("nz-input", p.tipo === "busqueda" && "nz-input--search") + '" id="' + id + '" type="' + tipo + '"' +
      (p.valor ? ' value="' + esc(p.valor) + '"' : "") + ">" +
      (p.error ? '<span class="nz-field__error">' + esc(p.error) + "</span>" : "") +
      (p.ayuda ? '<span class="nz-field__help">' + esc(p.ayuda) + "</span>" : "") +
      "</label>";
  };

  R.Formulario = function (p, ctx) {
    var col = p.columnas === "3" ? "3" : "2";
    return '<div class="nz-formgrid nz-formgrid--' + col + '">' + ctx.nodos(p.children) + "</div>";
  };

  R.Interruptor = function (p) {
    return '<label class="nz-switch"><input type="checkbox"' + (p.activo ? " checked" : "") + ">" +
      '<span class="nz-switch__track"><span class="nz-switch__thumb"></span></span>' +
      '<span class="nz-switch__label">' + esc(p.etiqueta) + "</span></label>";
  };

  R.Casilla = function (p) {
    return '<label class="nz-checkbox"><input type="checkbox"' + (p.marcada ? " checked" : "") + ">" +
      '<span class="nz-checkbox__box"></span>' + esc(p.etiqueta) + "</label>";
  };

  R.Chat = function (p) {
    var mensajes = list(p.mensajes).map(function (m) {
      var par = fila(m);
      var rol = (par[0] || "").toLowerCase();
      var clase = rol === "usuario" ? "nz-msg--usuario" : "nz-msg--asistente";
      return '<div class="nz-msg ' + clase + '"><div class="nz-msg__body">' +
        '<div class="nz-msg__author">' + esc(rol || "asistente") + "</div>" +
        '<div class="nz-msg__bubble"><p class="nz-msg__text">' + esc(par[1] || "") + "</p></div></div></div>";
    }).join("");
    return '<div class="nz-chat nz-chat--bordered">' +
      (p.titulo ? '<div class="nz-chat__head"><span class="nz-chat__title">' + esc(p.titulo) + "</span></div>" : "") +
      '<div class="nz-chat__body">' + mensajes + "</div></div>";
  };

  R.Herramienta = function (p) {
    var estado = { "ejecutando": "nz-toolcall__status--running", "hecho": "nz-toolcall__status--ok", "error": "nz-toolcall__status--error" }[p.estado || "hecho"];
    var is = { "ejecutando": "is-loading", "hecho": "is-done", "error": "is-error" }[p.estado || "hecho"];
    var etiqueta = { "ejecutando": "en curso", "hecho": "completado", "error": "error" }[p.estado || "hecho"];
    return '<div class="nz-toolcall ' + is + '"><div class="nz-toolcall__head">' +
      '<span class="nz-toolcall__name">' + esc(p.nombre) + "</span>" +
      '<span class="nz-toolcall__status ' + estado + '">' + etiqueta + "</span></div>" +
      (p.detalle ? '<div class="nz-toolcall__result">' + esc(p.detalle) + "</div>" : "") + "</div>";
  };

  /* ---------- presentación: deck con barra autocontenida ----------------
     El componente pinta el contador («02 / 03 · el dato») y las anclas
     (Anterior · Siguiente · ↺ Repetir) según la posición real: el programa
     no escribe posiciones y no puede desincronizarse. La última slide
     repite desde la primera. Fuera de deck, Slide se pinta sola. */
  function slideHTML(p, ctx, pos) {
    var cuerpo = ctx.nodos(p.children);
    var fondo = p.fondo === "profundo" ? " nz-escenario--profundo" : "";
    var abierta = '<section class="nz-escenario nz-escenario--pantalla' + fondo + '"' +
      (pos && pos.id ? ' id="' + pos.id + '"' : "") +
      '><div class="nz-escenario__cuerpo">' + cuerpo + "</div>";
    if (!pos) return abierta + "</section>";
    var n1 = pos.i + 1, t = pos.total;
    var contador = (n1 < 10 ? "0" : "") + n1 + " / " + (t < 10 ? "0" : "") + t +
      (p.titulo ? " · " + esc(p.titulo) : "");
    var izq = pos.i > 0
      ? '<a class="nz-esc-nav__enlace" href="#' + pos.prev + '"><span aria-hidden="true">←</span> Anterior</a>'
      : "";
    var der = pos.i === pos.total - 1
      ? '<a class="nz-esc-nav__enlace nz-esc-nav__enlace--final" href="#' + pos.prim + '">↺ Repetir</a>'
      : '<a class="nz-esc-nav__enlace" href="#' + pos.next + '">Siguiente <span aria-hidden="true">→</span></a>';
    return abierta + '<nav class="nz-esc-nav">' + izq +
      '<span class="nz-esc-nav__contador">' + contador + "</span>" + der + "</nav></section>";
  }

  R.Slide = function (p, ctx) {
    return slideHTML(p, ctx, null);
  };

  R.Presentacion = function (p, ctx) {
    var hijos = list(p.children);
    if (!hijos.length) return "";
    // el deck manda su propio scroll: la página pasa a modo presentación
    // (snap en <html> sin depender de dónde se inserte el marcado).
    if (typeof document !== "undefined" && document.documentElement) {
      document.documentElement.setAttribute("data-nz-presentacion", "");
    }
    var base = "nzp" + Math.random().toString(36).slice(2, 7);
    var ids = hijos.map(function (_, i) { return base + "-" + (i + 1); });
    var cuerpo = hijos.map(function (s, i) {
      var nodo = (s && s.type === "element" && s.typeName === "Slide") ? s : null;
      var props = nodo ? (nodo.props || {}) : { children: s };
      return slideHTML(props, ctx, {
        i: i, total: hijos.length, id: ids[i],
        prev: ids[i - 1], next: ids[i + 1], prim: ids[0]
      });
    }).join("");
    return '<div class="nz-presentacion">' + cuerpo + "</div>";
  };

  /* ---------- recorrido del árbol ---------------------------------------- */
  function renderNode(nodo) {
    if (!nodo) return "";
    if (nodo.type !== "element") return esc(nodo);
    var fn = R[nodo.typeName];
    if (!fn) {
      return '<span class="nz-badge nz-badge--danger">' + esc(nodo.typeName) + " no existe</span>";
    }
    var ctx = {
      nodos: function (v) {
        return list(v).map(function (h) { return renderNode(h); }).join("");
      }
    };
    try {
      return fn(nodo.props || {}, ctx);
    } catch (e) {
      return '<span class="nz-badge nz-badge--danger">' + esc(nodo.typeName) + ": " + esc(e.message) + "</span>";
    }
  }

  function contar(nodo, acc) {
    if (!nodo || nodo.type !== "element") return acc;
    acc.nodos++;
    acc.componentes[nodo.typeName] = (acc.componentes[nodo.typeName] || 0) + 1;
    var props = nodo.props || {};
    for (var k in props) {
      if (!Object.prototype.hasOwnProperty.call(props, k)) continue;
      var v = props[k];
      if (Array.isArray(v)) {
        for (var i = 0; i < v.length; i++) contar(v[i], acc);
      } else if (v && v.type === "element") {
        contar(v, acc);
      }
    }
    return acc;
  }

  /* ---------- parser local (red de seguridad sin CDN) -------------------- */
  function tokenizar(texto) {
    var t = [], i = 0;
    while (i < texto.length) {
      var c = texto[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '"') {
        var s = "", j = i + 1;
        while (j < texto.length && texto[j] !== '"') {
          if (texto[j] === "\\") { s += texto[j + 1]; j += 2; continue; }
          s += texto[j++];
        }
        t.push({ t: "str", v: s }); i = j + 1; continue;
      }
      if ("[](){},=".indexOf(c) !== -1) { t.push({ t: c }); i++; continue; }
      var m = /^(-?\d+(?:[.,]\d+)?)/.exec(texto.slice(i));
      if (m) { t.push({ t: "num", v: parseFloat(m[1].replace(",", ".")) }); i += m[1].length; continue; }
      var w = /^[A-Za-z_$][\w$.]*/.exec(texto.slice(i));
      if (w) {
        var palabra = w[0];
        if (palabra === "true" || palabra === "false") t.push({ t: "bool", v: palabra === "true" });
        else t.push({ t: "id", v: palabra });
        i += palabra.length; continue;
      }
      i++;
    }
    return t;
  }

  function parserLocal(programa, spec) {
    var t = tokenizar(programa), pos = 0;
    var sentencias = {}, orden = [];
    function peek() { return t[pos]; }
    function eat(tipo) {
      if (!t[pos] || (tipo && t[pos].t !== tipo)) throw new Error("se esperaba " + tipo);
      return t[pos++];
    }
    function expresion() {
      var tok = peek();
      if (!tok) throw new Error("fin inesperado");
      if (tok.t === "str" || tok.t === "num" || tok.t === "bool") { pos++; return { k: "lit", v: tok.v }; }
      if (tok.t === "[") {
        pos++;
        var arr = [];
        while (peek() && peek().t !== "]") {
          arr.push(expresion());
          if (peek() && peek().t === ",") pos++;
        }
        eat("]");
        return { k: "arr", v: arr };
      }
      if (tok.t === "{") {
        pos++;
        var obj = {};
        while (peek() && peek().t !== "}") {
          var clave = eat("id").v;
          eat(":");
          obj[clave] = expresion();
          if (peek() && peek().t === ",") pos++;
        }
        eat("}");
        return { k: "obj", v: obj };
      }
      if (tok.t === "id") {
        pos++;
        if (peek() && peek().t === "(") {
          pos++;
          var args = [];
          while (peek() && peek().t !== ")") {
            args.push(expresion());
            if (peek() && peek().t === ",") pos++;
          }
          eat(")");
          return { k: "call", nombre: tok.v, args: args };
        }
        return { k: "ref", nombre: tok.v };
      }
      throw new Error("token inesperado " + tok.t);
    }
    while (pos < t.length) {
      var id = eat("id").v;
      eat("=");
      sentencias[id] = expresion();
      orden.push(id);
    }
    function resolver(e) {
      if (!e) return null;
      if (e.k === "lit") return e.v;
      if (e.k === "arr") return e.v.map(resolver);
      if (e.k === "obj") {
        var o = {};
        for (var k in e.v) o[k] = resolver(e.v[k]);
        return o;
      }
      if (e.k === "ref") {
        if (!(e.nombre in sentencias)) return null;
        return resolver(sentencias[e.nombre]);
      }
      if (e.k === "call") {
        var def = spec.components[e.nombre];
        var props = {};
        var nombres = def ? Object.keys(spec.schema.$defs[e.nombre].properties) : [];
        e.args.forEach(function (a, i) {
          var clave = nombres[i] || ("arg" + i);
          props[clave] = resolver(a);
        });
        return { type: "element", typeName: e.nombre, props: props, partial: false };
      }
      return null;
    }
    var raiz = "root" in sentencias ? resolver(sentencias.root) : null;
    var errores = [];
    if (!raiz) errores.push({ code: "no-root", message: "el programa no define root" });
    return { root: raiz, meta: { statementCount: orden.length, errors: errores }, _local: true };
  }

  /* ---------- estado del módulo ------------------------------------------ */
  var estado = {
    spec: null,
    modo: "sin-cargar",
    parser: null,
    streaming: null,
    version: VERSION
  };

  function cargarSpec(url) {
    return fetch(url || SPEC_URL, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("spec " + r.status);
      return r.json();
    });
  }

  function cargarLangCore() {
    return import(CDN_LANG_CORE).then(function (m) { return m; });
  }

  function iniciar(opciones) {
    opciones = opciones || {};
    return cargarSpec(opciones.spec || SPEC_URL).then(function (spec) {
      estado.spec = spec;
      var quieroOficial = opciones.parser !== "local";
      var intento = quieroOficial ? cargarLangCore() : Promise.reject(new Error("forzado local"));
      return intento.then(function (m) {
        estado.parser = m;
        estado.modo = "oficial";
        return estado;
      }).catch(function () {
        estado.parser = null;
        estado.modo = "local";
        return estado;
      });
    });
  }

  function parsear(programa, completo) {
    var spec = estado.spec;
    if (!spec) throw new Error("llama antes a AuroraOpenUI.iniciar()");
    if (estado.parser) {
      if (completo) {
        var p = estado.parser.createParser(spec.schema, spec.root);
        return p.parse(programa);
      }
      if (!estado.streaming) {
        estado.streaming = estado.parser.createStreamingParser(spec.schema, spec.root);
      }
      return estado.streaming.set(programa, false);
    }
    return parserLocal(programa, spec);
  }

  /* ---------- API pública ------------------------------------------------ */
  function pintar(programa, contenedor, opciones) {
    opciones = opciones || {};
    var res = parsear(programa, opciones.streaming !== true);
    var html = renderNode(res.root);
    var el = typeof contenedor === "string" ? document.querySelector(contenedor) : contenedor;
    if (el) el.innerHTML = html;
    var cuenta = contar(res.root, { nodos: 0, componentes: {} });
    return {
      html: html,
      nodos: cuenta.nodos,
      componentes: cuenta.componentes,
      sentencias: (res.meta && res.meta.statementCount) || 0,
      errores: (res.meta && res.meta.errors) || [],
      modo: estado.modo
    };
  }

  function stream(programa, contenedor, opciones) {
    opciones = opciones || {};
    var paso = opciones.paso || 18;
    var ms = opciones.ms || 16;
    var el = typeof contenedor === "string" ? document.querySelector(contenedor) : contenedor;
    var completo = false;
    estado.streaming = null;
    return new Promise(function (resolve) {
      var i = 0;
      var ultimo = null;
      function tick() {
        if (i >= programa.length) {
          ultimo = pintar(programa, el, { streaming: false });
          if (opciones.onTick) opciones.onTick(ultimo, true);
          resolve(ultimo);
          return;
        }
        i = Math.min(programa.length, i + paso);
        ultimo = pintar(programa.slice(0, i), el, { streaming: true });
        if (opciones.onTick) opciones.onTick(ultimo, false);
        setTimeout(tick, ms);
      }
      tick();
    });
  }

  /* Inyecta el módulo de lang-core que ya tengas (build propio, import estático
     o test con jsdom). Si no se llama, `iniciar()` lo trae del CDN. */
  function inyectarParser(modulo) {
    estado.parser = modulo && modulo.createParser ? modulo : null;
    estado.modo = estado.parser ? "oficial" : "local";
    return estado.modo;
  }

  global.AuroraOpenUI = {
    version: VERSION,
    iniciar: iniciar,
    inyectarParser: inyectarParser,
    pintar: pintar,
    stream: stream,
    renderNode: renderNode,
    componentes: R,
    get modo() { return estado.modo; },
    get spec() { return estado.spec; }
  };
})(typeof window !== "undefined" ? window : this);
