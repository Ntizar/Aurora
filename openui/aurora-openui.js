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
    return '<section class="' + cl("nz-section", p.borde !== false && "nz-section--bordered") + '">' +
      (p.titulo ? '<h2 class="nz-h2">' + esc(p.titulo) + "</h2>" : "") + ctx.nodos(p.children) + "</section>";
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

  R.Tarjeta = function (p, ctx) {
    return '<article class="' + cl("nz-article", p.borde !== false && "nz-article--bordered") + '">' +
      (p.titulo ? '<h3 class="nz-h3">' + esc(p.titulo) + "</h3>" : "") + ctx.nodos(p.children) + "</article>";
  };

  R.Titular = function (p) {
    var nivel = String(p.nivel || "2");
    var tono = p.tono === "acento" ? "--accent" : p.tono === "marca" ? "--brand" : "";
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

  R.Kpi = function (p) {
    var tono = p.tono === "acento" ? "nz-kpi--accent" : p.tono === "marca" ? "nz-kpi--brand" : "";
    var claseValor = p.tono === "acento" ? "nz-kpi__value--accent" : p.tono === "marca" ? "nz-kpi__value--brand" : "";
    var tendencia = TENDENCIA[p.tendencia] ? "nz-kpi__delta--" + TENDENCIA[p.tendencia] : "";
    return '<div class="' + cl("nz-kpi", tono, p.tamano && "nz-kpi--" + p.tamano) + '">' +
      '<span class="nz-kpi__label">' + esc(p.etiqueta) + "</span>" +
      '<span class="' + cl("nz-kpi__value", claseValor) + '">' + esc(p.valor) + "</span>" +
      (p.delta ? '<span class="' + cl("nz-kpi__delta", tendencia) + '">' + esc(p.delta) + "</span>" : "") +
      "</div>";
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
    return '<div class="' + cl("nz-chart-donut", p.tamano === "lg" ? "nz-chart-donut--lg" : "nz-chart-donut--sm") + '">' +
      '<svg class="nz-chart-donut__svg" viewBox="0 0 42 42" role="img" aria-label="' +
      esc((p.etiqueta || "Progreso") + ": " + v + " por ciento") + '">' +
      '<circle class="nz-chart-donut__track" cx="21" cy="21" r="15.9"></circle>' +
      '<circle class="nz-chart-donut__seg ' + tono + '" cx="21" cy="21" r="15.9" stroke-dasharray="' +
      v + " " + (100 - v) + '"></circle></svg>' +
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
    return '<button type="button" class="' + cl("nz-btn", tono, p.tamano && "nz-btn--" + p.tamano, p.bloque && "nz-btn--block") + '">' + esc(p.texto) + "</button>";
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
    var enlaces = list(p.enlaces).map(function (e) {
      return '<a class="nz-navbar__link" href="#">' + esc(e) + "</a>";
    }).join("");
    return '<div class="nz-navbar nz-navbar--bordered"><span class="nz-navbar__brand"><i></i>' + esc(p.marca) + "</span>" +
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
