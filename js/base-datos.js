/* ============================================================
   AURORA — js/base-datos.js · Explorador de la base de datos
   Sin dependencias. Carga datos/base-diseno.json y lo convierte
   en un catálogo consultable: busca, filtra, abre ficha, copia
   markup y renderiza la preview real del componente.
   ============================================================ */
(function () {
  "use strict";

  var $ = function (sel, raiz) { return (raiz || document).querySelector(sel); };
  var $$ = function (sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); };

  /* ---------- Tema ---------- */
  var raiz = document.documentElement;
  var CLAVE = "aurora7-tema";
  try {
    var guardado = localStorage.getItem(CLAVE);
    if (guardado === "dark" || guardado === "light") raiz.setAttribute("data-nz-theme", guardado);
  } catch (e) { /* modo privado */ }
  var btnTema = $("#btnTheme");
  if (btnTema) {
    btnTema.addEventListener("click", function () {
      var nuevo = raiz.getAttribute("data-nz-theme") === "dark" ? "light" : "dark";
      raiz.setAttribute("data-nz-theme", nuevo);
      try { localStorage.setItem(CLAVE, nuevo); } catch (e) { /* irrelevante */ }
    });
  }

  /* ---------- Utilidades ---------- */
  function normaliza(t) {
    return (t || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function esc(t) {
    return (t || "").toString()
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  var TIPOS = {
    familia: "Familia",
    token: "Token",
    receta: "Receta",
    combo: "Combo",
    marca: "Marca",
    principio: "Ley",
    categoria: "Categoría"
  };

  var COLOR = /^(#|rgb|hsl|oklch|oklab|color-mix)/i;

  /* ---------- Estado ---------- */
  var entradas = [];
  var filtro = "todo";
  var terminos = [];
  var activa = null;

  var resultados = $("#baseResultados");
  var vacio = $("#baseVacio");
  var contador = $("#baseContador");
  var cuenta = $("#baseCuenta");
  var ficha = $("#baseFicha");
  var buscador = $("#baseBuscar");

  /* ---------- Construcción del índice ---------- */
  function entrada(tipo, id, titulo, subtitulo, texto, datos) {
    return {
      tipo: tipo, id: id, titulo: titulo, subtitulo: subtitulo,
      texto: normaliza(texto), datos: datos
    };
  }

  function construir(d) {
    var e = [];
    var cats = {};
    d.categorias.forEach(function (c) { cats[c.id] = c.nombre; });

    d.familias.forEach(function (f) {
      var texto = [f.id, f.titulo, f.cuandoUsar, f.pack, f.noUsar]
        .concat(f.clases, f.partes, f.modificadores, f.tags, f.alias, f.tokens).join(" ");
      e.push(entrada("familia", f.id, f.titulo || f.id, f.id, texto, f));
    });

    d.tokens.forEach(function (t) {
      e.push(entrada("token", t.nombre, t.nombre, t.valor, [t.nombre, t.valor, t.seccion].join(" "), t));
    });

    (d.recetas || []).concat(d.ejemplos || []).forEach(function (r) {
      var texto = [r.id, r.titulo, r.descripcion, r.fichero].concat(r.packs, r.secciones, r.tags).join(" ");
      e.push(entrada("receta", r.fichero, r.titulo, r.nivel === "canonica" ? "Receta canónica" : "Receta mínima", texto, r));
    });

    d.combos.forEach(function (c) {
      var texto = [c.id, c.tipico, c.fichero].concat(c.packs, c.familias, c.tags).join(" ");
      e.push(entrada("combo", c.id, c.id.replace(/-/g, " "), c.tipico, texto, c));
    });

    d.marcas.forEach(function (m) {
      e.push(entrada("marca", m.id, m.id, m.marca + " · " + m.acento, [m.id, m.marca, m.acento, m.fichero].join(" "), m));
    });

    d.principios.forEach(function (p) {
      e.push(entrada("principio", "ley-" + p.id, p.titulo, "Ley " + p.id, [p.titulo, p.lint, "ley " + p.id].join(" "), p));
    });

    d.categorias.forEach(function (c) {
      var texto = [c.id, c.nombre, c.descripcion, c.cuandoUsar, c.pack].concat(c.tags).join(" ");
      e.push(entrada("categoria", "cat-" + c.id, c.nombre, c.pack, texto, c));
    });

    return e;
  }

  /* ---------- Pintado de tarjetas ---------- */
  function tarjeta(en) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "cat-base-card";
    b.setAttribute("data-tipo", en.tipo);
    b.setAttribute("data-id", en.id);

    var meta = "";
    if (en.tipo === "familia") {
      meta = en.datos.clases.length + " clases · " + en.datos.nTokens + " tokens";
    } else if (en.tipo === "token") {
      meta = en.datos.seccion + (en.datos.dark ? " · dark" : "");
    } else if (en.tipo === "receta") {
      meta = en.datos.packs.length + " packs · " + en.datos.secciones.length + " secciones";
    } else if (en.tipo === "combo") {
      meta = en.datos.packs.length + " packs";
    } else if (en.tipo === "marca") {
      meta = en.datos.contrasteOk ? "contraste AA" : "revisar contraste";
    } else if (en.tipo === "principio") {
      meta = en.datos.lint || "revisión";
    } else {
      meta = en.datos.objetos + " objetos";
    }

    var swatch = "";
    if (en.tipo === "token" && en.datos.esColor) {
      swatch = '<span class="cat-base-swatch" style="--swatch:' + esc(en.datos.valor) + '"></span>';
    } else if (en.tipo === "marca") {
      swatch = '<span class="cat-base-swatch" style="--swatch:' + esc(en.datos.marca) + '"></span>' +
               '<span class="cat-base-swatch" style="--swatch:' + esc(en.datos.acento) + '"></span>';
    }

    b.innerHTML =
      '<span class="cat-base-card__top"><span class="cat-base-card__tipo cat-base-card__tipo--' + en.tipo + '">' +
      TIPOS[en.tipo] + "</span>" + swatch + "</span>" +
      '<span class="cat-base-card__title">' + esc(en.titulo) + "</span>" +
      '<code class="cat-base-card__code">' + esc(en.subtitulo) + "</code>" +
      '<span class="cat-base-card__meta">' + esc(meta) + "</span>";

    b.addEventListener("click", function () { abrirFicha(en); });
    return b;
  }

  function pintar() {
    resultados.textContent = "";
    var frag = document.createDocumentFragment();
    var n = 0;
    entradas.forEach(function (en) {
      if (filtro !== "todo" && en.tipo !== filtro) return;
      if (terminos.length && !terminos.every(function (t) { return en.texto.indexOf(t) !== -1; })) return;
      frag.appendChild(tarjeta(en));
      n++;
    });
    resultados.appendChild(frag);
    vacio.hidden = n !== 0;
    cuenta.textContent = n === entradas.length ? n + " objetos" : n + " de " + entradas.length;
    contador.textContent = n + " objetos visibles";
  }

  /* ---------- Ficha ---------- */
  function chip(t) { return '<span class="cat-base-chip">' + esc(t) + "</span>"; }

  function preview(en) {
    if (en.tipo === "familia") {
      return '<div class="cat-stage cat-base-preview"><div class="cat-base-preview__lienzo">' + en.datos.markup + "</div></div>";
    }
    if (en.tipo === "receta" || en.tipo === "combo") {
      return '<iframe class="cat-base-iframe" src="' + esc(en.datos.fichero) + '" title="Preview de ' + esc(en.titulo) +
        '" loading="lazy" sandbox></iframe>';
    }
    if (en.tipo === "token") {
      if (en.datos.esColor) {
        return '<div class="cat-base-tokenpreview" style="--swatch:' + esc(en.datos.valor) + '"><span>' + esc(en.datos.valor) + "</span></div>";
      }
      return '<div class="cat-base-tokenpreview cat-base-tokenpreview--texto"><span>' + esc(en.datos.valor) + "</span></div>";
    }
    if (en.tipo === "marca") {
      return '<div class="cat-base-marcapreview">' +
        '<span style="--swatch:' + esc(en.datos.marca) + '"><b>Marca</b>' + esc(en.datos.marca) + "</span>" +
        '<span style="--swatch:' + esc(en.datos.acento) + '"><b>Acento</b>' + esc(en.datos.acento) + "</span></div>";
    }
    return "";
  }

  function cuerpo(en) {
    var d = en.datos;
    var html = "";

    if (en.tipo === "familia") {
      html += '<p class="cat-base-ficha__lead">' + esc(d.cuandoUsar) + "</p>";
      if (d.noUsar) html += '<div class="nz-alert nz-alert--warning"><b>Cuándo NO usarlo.</b> ' + esc(d.noUsar) + "</div>";
      html += '<div class="cat-base-bloque"><h3>Clases</h3><div class="cat-base-chips">' +
        d.clases.map(chip).join("") + "</div></div>";
      if (d.modificadores.length) {
        html += '<div class="cat-base-bloque"><h3>Modificadores</h3><div class="cat-base-chips">' +
          d.modificadores.map(function (m) { return chip("--" + m); }).join("") + "</div></div>";
      }
      if (d.alias.length) {
        html += '<div class="cat-base-bloque"><h3>Alias en inglés</h3><div class="cat-base-chips">' +
          d.alias.map(chip).join("") + "</div></div>";
      }
      if (d.tokens.length) {
        html += '<div class="cat-base-bloque"><h3>Tokens que consume</h3><div class="cat-base-chips">' +
          d.tokens.slice(0, 24).map(chip).join("") + (d.tokens.length > 24 ? chip("+" + (d.tokens.length - 24)) : "") + "</div></div>";
      }
      html += '<div class="cat-base-bloque"><h3>Markup real</h3>' + bloqueCodigo(d.markup) + "</div>";
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="' + esc(d.demo) + '">Ver la demo completa</a>';
    }

    if (en.tipo === "token") {
      html += '<p class="cat-base-ficha__lead">Token del sistema. No lo copies a mano: úsalo con <code class="nz-code nz-code--inline">var(' + esc(d.nombre) + ")</code>.</p>";
      html += '<div class="cat-base-bloque"><h3>Valor</h3>' + bloqueCodigo(d.valor) + "</div>";
      html += '<div class="cat-base-bloque"><h3>Sección</h3><div class="cat-base-chips">' + chip(d.seccion) +
        (d.dark ? chip("solo dark") : "") + "</div></div>";
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="paginas/12-system.html">Ver los tokens en el catálogo</a>';
    }

    if (en.tipo === "receta") {
      html += '<p class="cat-base-ficha__lead">' + esc(d.descripcion) + "</p>";
      html += '<div class="cat-base-bloque"><h3>Packs que enlaza</h3><div class="cat-base-chips">' + d.packs.map(chip).join("") + "</div></div>";
      if (d.secciones.length) {
        html += '<div class="cat-base-bloque"><h3>Secciones</h3><div class="cat-base-chips">' + d.secciones.map(chip).join("") + "</div></div>";
      }
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="' + esc(d.fichero) + '">Abrir la receta</a> ';
      html += '<a class="nz-btn nz-btn--ghost nz-btn--sm" href="' + esc(d.fichero) + '" download>Descargar HTML</a>';
    }

    if (en.tipo === "combo") {
      html += '<p class="cat-base-ficha__lead">' + esc(d.tipico || "Esqueleto de página completo.") + "</p>";
      html += '<div class="cat-base-bloque"><h3>Packs que enlaza</h3><div class="cat-base-chips">' + d.packs.map(chip).join("") + "</div></div>";
      if (d.familias.length) {
        html += '<div class="cat-base-bloque"><h3>Familias del esqueleto</h3><div class="cat-base-chips">' + d.familias.map(chip).join("") + "</div></div>";
      }
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="' + esc(d.fichero) + '">Abrir el esqueleto</a>';
    }

    if (en.tipo === "marca") {
      html += '<p class="cat-base-ficha__lead">Preset de color: marca para la estructura y acento para el dato que importa. Se enlaza después de tokens.css.</p>';
      html += '<div class="cat-base-bloque"><h3>Contraste</h3><div class="cat-base-chips">' +
        chip("marca " + d.marca) + chip("acento " + d.acento) +
        chip(d.contrasteOk ? "AA ✓" : "revisar") + "</div></div>";
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="marcas/index.html">Ver el motor de temas</a> ';
      html += '<a class="nz-btn nz-btn--ghost nz-btn--sm" href="' + esc(d.fichero) + '">Abrir el preset CSS</a>';
    }

    if (en.tipo === "principio") {
      html += '<p class="cat-base-ficha__lead">' + esc(d.titulo) + "</p>";
      html += '<div class="cat-base-bloque"><h3>Lo comprueba</h3>' + bloqueCodigo(d.lint) + "</div>";
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="COMPOSICION.md">Leer las 12 leyes</a>';
    }

    if (en.tipo === "categoria") {
      html += '<p class="cat-base-ficha__lead">' + esc(d.descripcion) + "</p>";
      html += '<div class="cat-base-bloque"><h3>Cuándo abrirla</h3><p>' + esc(d.cuandoUsar) + "</p></div>";
      html += '<div class="cat-base-bloque"><h3>Cifras</h3><div class="cat-base-chips">' +
        chip(d.objetos + " objetos") + chip(d.familias + " familias") + chip(d.demos + " demos") + "</div></div>";
      html += '<a class="nz-btn nz-btn--primary nz-btn--sm" href="' + esc(d.pagina) + '">Ver la categoría</a>';
    }

    return html;
  }

  function bloqueCodigo(t) {
    var id = "copiar-" + Math.random().toString(36).slice(2, 8);
    return '<div class="cat-base-codigo"><pre><code id="' + id + '">' + esc(t) + "</code></pre>" +
      '<button class="nz-btn nz-btn--soft nz-btn--sm cat-base-copiar" data-copiar="' + id + '">Copiar</button></div>';
  }

  function abrirFicha(en) {
    activa = en;
    ficha.innerHTML =
      '<div class="cat-base-ficha__head">' +
        '<span class="cat-base-card__tipo cat-base-card__tipo--' + en.tipo + '">' + TIPOS[en.tipo] + "</span>" +
        '<button class="cat-base-cerrar" type="button" aria-label="Cerrar ficha">×</button>' +
      "</div>" +
      "<h2>" + esc(en.titulo) + "</h2>" +
      '<p class="cat-base-ficha__id"><code>' + esc(en.subtitulo) + "</code></p>" +
      preview(en) +
      cuerpo(en);

    var cerrar = $(".cat-base-cerrar", ficha);
    if (cerrar) cerrar.addEventListener("click", function () {
      ficha.innerHTML = intro();
      activa = null;
      history.replaceState(null, "", location.pathname + location.search);
    });

    $$("[data-copiar]", ficha).forEach(function (b) {
      b.addEventListener("click", function () {
        var codigo = document.getElementById(b.getAttribute("data-copiar"));
        if (!codigo) return;
        copiar(codigo.textContent, b);
      });
    });

    history.replaceState(null, "", "#f=" + encodeURIComponent(en.id));
    if (ficha.scrollIntoView && window.matchMedia && window.matchMedia("(max-width: 1199px)").matches) {
      ficha.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function copiar(texto, boton) {
    var hecho = function () {
      var original = boton.textContent;
      boton.textContent = "Copiado";
      setTimeout(function () { boton.textContent = original; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(hecho, function () { respaldo(texto, hecho); });
    } else {
      respaldo(texto, hecho);
    }
  }

  function respaldo(texto, hecho) {
    var ta = document.createElement("textarea");
    ta.value = texto;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); hecho(); } catch (e) { /* sin permiso */ }
    document.body.removeChild(ta);
  }

  function intro() {
    return '<div class="cat-base-ficha__intro">' +
      '<p class="cat-pagehead__over">Ficha</p>' +
      "<h2>Elige un objeto</h2>" +
      "<p>Haz clic en cualquier tarjeta y aquí verás la preview real, el markup, los tokens y cuándo usarlo. Se copia con un botón.</p>" +
      '<p class="cat-base-hint">Atajo: pulsa <kbd class="nz-kbd">/</kbd> para buscar y <kbd class="nz-kbd">Esc</kbd> para limpiar.</p>' +
      "</div>";
  }

  /* ---------- Eventos ---------- */
  function aplicarBusqueda() {
    terminos = normaliza(buscador.value).split(" ").filter(Boolean);
    pintar();
  }

  if (buscador) {
    buscador.addEventListener("input", aplicarBusqueda);
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "/" && document.activeElement !== buscador) {
        ev.preventDefault();
        buscador.focus();
      }
      if (ev.key === "Escape" && document.activeElement === buscador) {
        buscador.value = "";
        aplicarBusqueda();
        buscador.blur();
      }
    });
  }

  $$("[data-filtro]").forEach(function (chipFiltro) {
    chipFiltro.addEventListener("click", function () {
      filtro = chipFiltro.getAttribute("data-filtro");
      $$("[data-filtro]").forEach(function (c) { c.setAttribute("aria-pressed", String(c === chipFiltro)); });
      pintar();
    });
  });

  /* ---------- Arranque ---------- */
  fetch("datos/base-diseno.json")
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (d) {
      entradas = construir(d);
      pintar();

      // Cifras del hero: se rellenan del índice, nunca a mano.
      $$("[data-cifra]").forEach(function (el) {
        var clave = el.getAttribute("data-cifra");
        el.textContent = d.resumen[clave] != null ? d.resumen[clave] : "—";
      });

      // Índice de categorías, generado del JSON (sin 18 enlaces a mano).
      var indice = $("#baseIndice");
      if (indice) {
        indice.innerHTML = d.categorias.map(function (c) {
          var n = ("0" + c.id).slice(-2);
          return '<a class="cat-base-indice__item" href="#f=cat-' + c.id + '" data-cat="' + c.id + '">' +
            "<b>" + n + "</b><span>" + esc(c.nombre) + "</span><i>" + c.objetos + " objetos</i></a>";
        }).join("");
        indice.addEventListener("click", function (ev) {
          var a = ev.target.closest ? ev.target.closest("a[data-cat]") : null;
          if (!a) return;
          ev.preventDefault();
          var en = entradas.filter(function (x) { return x.id === "cat-" + a.getAttribute("data-cat"); })[0];
          if (en) abrirFicha(en);
        });
      }

      var cta = $('a[href="#baseBuscar"]');
      if (cta && buscador) {
        cta.addEventListener("click", function (ev) {
          ev.preventDefault();
          buscador.focus();
          if (buscador.scrollIntoView) buscador.scrollIntoView({ behavior: "smooth", block: "center" });
        });
      }

      var hash = /^#f=(.+)$/.exec(location.hash);
      if (hash) {
        var id = decodeURIComponent(hash[1]);
        var en = entradas.filter(function (x) { return x.id === id; })[0];
        if (en) abrirFicha(en);
      }
    })
    .catch(function (err) {
      contador.textContent = "No se pudo cargar la base";
      resultados.innerHTML = '<div class="nz-alert nz-alert--danger"><b>No se pudo cargar datos/base-diseno.json.</b> ' +
        "Abre esta página por HTTP (por ejemplo <code>python3 -m http.server</code>), no con file://. Detalle: " + esc(err.message) + "</div>";
    });
})();
