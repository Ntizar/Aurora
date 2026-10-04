/* ============================================================
   AURORA — js/catalog.js · Comportamiento del catálogo
   Sin dependencias. Trozo de JS real, no decorativo:
     1. Tema light/dark persistente (localStorage).
     2. Buscador en vivo sobre las demos (título, clase, contenido).
     3. Filtro por categoría.
     4. "Ver código" + copiar el markup de cada demo.
   El catálogo es CSS puro: este archivo solo sirve para navegar por
   él cómodamente. Las páginas del sistema no lo necesitan.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- 1. Tema ---------- */
  var raiz = document.documentElement;
  var CLAVE = "aurora7-tema";
  try {
    var guardado = localStorage.getItem(CLAVE);
    if (guardado === "dark" || guardado === "light") raiz.setAttribute("data-nz-theme", guardado);
  } catch (e) { /* modo privado: se ignora */ }

  var btn = document.getElementById("btnTheme");
  if (btn) {
    btn.addEventListener("click", function () {
      var nuevo = raiz.getAttribute("data-nz-theme") === "dark" ? "light" : "dark";
      raiz.setAttribute("data-nz-theme", nuevo);
      try { localStorage.setItem(CLAVE, nuevo); } catch (e) { /* irrelevante */ }
    });
  }

  /* ---------- 2 y 3. Buscador y filtro ---------- */
  var buscador = document.getElementById("catBuscar");
  var contador = document.getElementById("catContador");
  var vacio = document.getElementById("catVacio");
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-filtro]"));
  var demos = Array.prototype.slice.call(document.querySelectorAll(".cat-demo"));
  var tarjetas = Array.prototype.slice.call(document.querySelectorAll(".cat-cat"));
  var filtroActual = "todo";

  function normaliza(t) {
    return (t || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function aplica() {
    var q = normaliza(buscador ? buscador.value.trim() : "");
    var visibles = 0;

    demos.forEach(function (d) {
      var texto = normaliza(d.textContent);
      var categorias = normaliza(d.getAttribute("data-cat") || "");
      var coincideTexto = !q || texto.indexOf(q) !== -1;
      var coincideFiltro = filtroActual === "todo" || categorias.indexOf(filtroActual) !== -1;
      var ok = coincideTexto && coincideFiltro;
      d.hidden = !ok;
      if (ok) visibles++;
    });

    tarjetas.forEach(function (t) {
      var texto = normaliza(t.textContent);
      t.hidden = !!q && texto.indexOf(q) === -1;
    });

    if (contador) {
      contador.textContent = (q || filtroActual !== "todo")
        ? visibles + " de " + demos.length
        : demos.length + " objetos";
    }
    if (vacio) vacio.hidden = visibles !== 0 || demos.length === 0;
  }

  if (buscador) {
    buscador.addEventListener("input", aplica);
    buscador.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { buscador.value = ""; aplica(); }
    });
    // Atajo: "/" enfoca el buscador (salvo que se esté escribiendo en él).
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== buscador) {
        e.preventDefault();
        buscador.focus();
      }
    });
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      filtroActual = c.getAttribute("data-filtro") || "todo";
      chips.forEach(function (o) { o.setAttribute("aria-pressed", String(o === c)); });
      aplica();
    });
  });

  if (demos.length) aplica();

  /* ---------- 4. Ver código + copiar ---------- */
  document.querySelectorAll(".cat-demo").forEach(function (d) {
    var stage = d.querySelector(".cat-stage");
    if (!stage) return;
    var markup = stage.innerHTML.trim().replace(/^\s+/gm, "");
    var det = document.createElement("details");
    det.className = "cat-demo__code";
    var sum = document.createElement("summary");
    sum.textContent = "Ver código";
    var pre = document.createElement("pre");
    var code = document.createElement("code");
    code.textContent = markup;
    pre.appendChild(code);
    det.appendChild(sum);
    det.appendChild(pre);
    d.appendChild(det);
  });

  document.addEventListener("click", function (e) {
    var b = e.target.closest(".cat-demo__copy");
    if (!b) return;
    var pre = b.parentNode.querySelector("code");
    if (!pre) return;
    var texto = pre.textContent;
    var hecho = function () {
      var previo = b.textContent;
      b.textContent = "✓ Copiado";
      setTimeout(function () { b.textContent = previo; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(hecho, function () { /* sin permiso */ });
    } else {
      var ta = document.createElement("textarea");
      ta.value = texto;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); hecho(); } catch (err) { /* sin permiso */ }
      document.body.removeChild(ta);
    }
  });

  /* Botón de copiar dentro de cada bloque de código */
  document.querySelectorAll(".cat-demo__code").forEach(function (det) {
    var pre = det.querySelector("pre");
    if (!pre) return;
    var b = document.createElement("button");
    b.type = "button";
    b.className = "cat-demo__copy";
    b.textContent = "Copiar";
    b.setAttribute("aria-label", "Copiar el código del objeto");
    pre.insertBefore(b, pre.firstChild);
  });

  /* ---------- Contadores de la portada ---------- */
  function cuenta(el, objetivo, dur) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { el.textContent = objetivo; return; }
    var t0 = null;
    (function paso(t) {
      if (!t0) t0 = t;
      var k = Math.min((t - t0) / dur, 1);
      el.textContent = Math.round(objetivo * (k === 1 ? 1 : 1 - Math.pow(2, -10 * k)));
      if (k < 1) requestAnimationFrame(paso);
    })(performance.now());
  }
  document.querySelectorAll("[data-cuenta]").forEach(function (el) {
    cuenta(el, +el.getAttribute("data-cuenta"), 1400);
  });

  /* ---------- Botón que cicla (señales de vida) ---------- */
  var save = document.getElementById("liveSave");
  if (save) {
    save.addEventListener("click", function () {
      if (save.classList.contains("is-busy")) return;
      save.classList.add("is-busy");
      save.textContent = "Guardando…";
      setTimeout(function () { save.textContent = "✓ Guardado"; save.classList.add("is-ok"); }, 1100);
      setTimeout(function () { save.textContent = "Guardar cambios"; save.classList.remove("is-busy", "is-ok"); }, 3000);
    });
  }
  var prog = document.getElementById("liveProg");
  if (prog) setTimeout(function () { prog.classList.add("go"); }, 500);
})();
