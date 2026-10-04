/* ============================================================
   AURORA — js/graficos.js · Interactividad de gráficos real
   Sin dependencias. Lee el propio HTML y añade, sin configurar nada:
     1. Tooltip flotante (.nz-chart-tip) al pasar el ratón o al enfocar con
        teclado sobre barras, puntos de línea, segmentos de donut, tramos de
        cascada y demás. El valor sale de .nz-chart-bar__value o de
        data-valor / data-etiqueta: nunca se inventa nada.
     2. Animación de entrada con IntersectionObserver (data-nz-anim en <html>
        + data-nz-crecido en cada pieza), respetando prefers-reduced-motion.
     3. Leyenda clicable: pulsa un .nz-legend__item (aria-pressed) y su serie
        se atenúa (.is-selected) buscando por data-serie.
     4. Accesible: el tooltip se abre con foco de teclado y se cierra con
        Escape o al salir; los puntos con dato reciben tabindex y aria-label.
   Si la página no tiene ni un gráfico, sale sin tocar el DOM.
   ============================================================ */
(function () {
  "use strict";
  if (window.__nzGraficos) return;
  window.__nzGraficos = true;

  var SEL_GRAFICO = [
    ".nz-chart", ".nz-chart-bar", ".nz-chart-line", ".nz-chart-donut",
    ".nz-chart-waterfall", ".nz-chart-tablebar", ".nz-chart-bullet",
    ".nz-sparkline", ".nz-chart-compare", ".nz-chart-scatter", ".nz-heatmap",
    ".nz-heatcalendar", ".nz-treemap", ".nz-funnel", ".nz-chart-gauge",
    ".nz-chart-radar", ".nz-chart-flow", ".nz-chart-stat"
  ].join(",");

  var OBJ = [
    ".nz-chart-bar__bar", ".nz-chart-bar__seg", ".nz-chart-line__dot",
    ".nz-chart-donut__seg", ".nz-chart-waterfall__bar", ".nz-chart-tablebar__bar",
    ".nz-bullet__value", ".nz-funnel__bar", ".nz-sparkline__bar",
    ".nz-chart-mini__bar", ".nz-treemap__cell", ".nz-chart-scatter__dot",
    ".nz-chart-compare__bar", ".nz-chart-gauge__fill", ".nz-chart-radar__area",
    ".nz-heatmap__cell"
  ].join(",");

  var SEL_ETIQUETA = [
    ".nz-chart-waterfall__label", ".nz-chart-tablebar__name", ".nz-chart-compare__name",
    ".nz-bullet__label", ".nz-treemap__label", ".nz-funnel__label",
    ".nz-chart-bar__label", ".nz-heatmap__row-label", ".nz-chart-donut__label",
    ".nz-chart-gauge__label", ".nz-chart-stat__label"
  ];
  var SEL_VALOR = [
    ".nz-chart-bar__value", ".nz-chart-waterfall__value", ".nz-chart-tablebar__num",
    ".nz-chart-compare__num", ".nz-bullet__num", ".nz-treemap__value",
    ".nz-funnel__value", ".nz-chart-gauge__value", ".nz-chart-donut__value",
    ".nz-chart-stat__value"
  ];

  function cada(lista, fn) { Array.prototype.forEach.call(lista, fn); }
  function txt(el) { return el ? (el.textContent || "").replace(/\s+/g, " ").trim() : ""; }

  /* Sube por los ancestros buscando el primer texto que case con los selectores. */
  function busca(el, selectores) {
    var n = el;
    for (var i = 0; i < 6 && n && n.nodeType === 1; i++) {
      for (var s = 0; s < selectores.length; s++) {
        var t = txt(n.querySelector(selectores[s]));
        if (t) return t;
      }
      n = n.parentNode;
    }
    return "";
  }

  function describe(el) {
    return {
      etiqueta: el.getAttribute("data-etiqueta") || el.getAttribute("data-label") || busca(el, SEL_ETIQUETA),
      valor: el.getAttribute("data-valor") || el.getAttribute("data-value") || busca(el, SEL_VALOR)
    };
  }

  function init() {
    var raices = document.querySelectorAll(SEL_GRAFICO);
    if (!raices.length) return;                    /* coste cero si no hay gráficos */

    /* ---------- 1. Tooltip compartido (uno solo para toda la página) ---------- */
    var tip = document.createElement("div");
    tip.className = "nz-chart-tip";
    tip.setAttribute("role", "tooltip");
    tip.setAttribute("aria-hidden", "true");
    var tipEt = document.createElement("span");
    tipEt.className = "nz-chart-tip__label";
    var tipVa = document.createElement("span");
    tipVa.className = "nz-chart-tip__value";
    tip.appendChild(tipEt);
    tip.appendChild(tipVa);
    document.body.appendChild(tip);

    var actual = null;

    function coloca(el) {
      var r = el.getBoundingClientRect();
      var tr = tip.getBoundingClientRect();
      var x = r.left + r.width / 2 - tr.width / 2;
      var y = r.top - tr.height - 8;
      if (y < 8) y = r.bottom + 8;                 /* poco espacio arriba → debajo */
      x = Math.max(8, Math.min(x, window.innerWidth - tr.width - 8));
      y = Math.max(8, Math.min(y, window.innerHeight - tr.height - 8));
      tip.style.left = x + "px";
      tip.style.top = y + "px";
    }

    function muestra(el) {
      var d = describe(el);
      if (!d.etiqueta && !d.valor) { oculta(); return; }
      tipEt.textContent = d.etiqueta;
      tipEt.style.display = d.etiqueta ? "" : "none";
      tipVa.textContent = d.valor;
      tipVa.style.display = d.valor ? "" : "none";
      tip.classList.add("is-active");
      tip.setAttribute("aria-hidden", "false");
      coloca(el);
      actual = el;
    }
    function oculta() {
      tip.classList.remove("is-active");
      tip.setAttribute("aria-hidden", "true");
      actual = null;
    }
    function objetivo(e) {
      var el = e.target;
      return (el && el.closest) ? el.closest(OBJ) : null;
    }

    document.addEventListener("mouseover", function (e) {
      var t = objetivo(e);
      if (t && t !== actual) muestra(t);
    });
    document.addEventListener("mouseout", function (e) {
      var t = objetivo(e);
      if (!t || actual !== t) return;
      var r = e.relatedTarget;
      if (r && r.closest && r.closest(OBJ) === t) return;   /* sigue dentro del punto */
      oculta();
    });
    document.addEventListener("focusin", function (e) {
      var t = objetivo(e);
      if (t) muestra(t);
    });
    document.addEventListener("focusout", function (e) {
      if (objetivo(e)) oculta();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && actual) oculta();
    });
    window.addEventListener("scroll", function () { if (actual) coloca(actual); }, { passive: true });
    window.addEventListener("resize", function () { if (actual) oculta(); });

    /* ---------- 1b. Enfocables y etiquetados los puntos que tienen dato ---------- */
    cada(raices, function (raiz) {
      raiz.classList.add("nz-chart--interactivo");
      cada(raiz.querySelectorAll(OBJ), function (el) {
        var d = describe(el);
        if (!d.etiqueta && !d.valor) return;
        if (el.getAttribute("tabindex") === null) el.setAttribute("tabindex", "0");
        if (!el.getAttribute("aria-label")) {
          el.setAttribute("aria-label", (d.etiqueta ? d.etiqueta + ": " : "") + d.valor);
        }
      });
    });

    /* ---------- 2. Animación de entrada (IntersectionObserver) ---------- */
    var reducido = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reducido && "IntersectionObserver" in window) {
      var ANIM = [
        ".nz-chart-bar__bar", ".nz-chart-bar__seg", ".nz-chart-waterfall__bar",
        ".nz-sparkline__bar", ".nz-chart-mini__bar", ".nz-funnel__bar",
        ".nz-chart-tablebar__bar", ".nz-bullet__value", ".nz-chart-line__svg",
        ".nz-chart-donut__svg", ".nz-chart-gauge__svg", ".nz-heatmap__cell"
      ].join(",");
      var animables = document.querySelectorAll(ANIM);
      if (animables.length) {
        document.documentElement.setAttribute("data-nz-anim", "");
        var obs = new IntersectionObserver(function (ents) {
          ents.forEach(function (en) {
            if (en.isIntersecting) {
              en.target.setAttribute("data-nz-crecido", "");
              obs.unobserve(en.target);
            }
          });
        }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
        /* Lo que ya está a la vista al cargar crece de inmediato; lo demás, al
           entrar en pantalla. Nunca se queda a medias: además hay red de
           seguridad por tiempo, porque una pieza sin crecer se vería al 55%. */
        var vista = window.innerHeight || 800;
        cada(animables, function (el) {
          var r = el.getBoundingClientRect();
          if (r.bottom > 0 && r.top < vista) el.setAttribute("data-nz-crecido", "");
          else obs.observe(el);
        });
        setTimeout(function () {
          cada(animables, function (el) {
            if (!el.hasAttribute("data-nz-crecido")) el.setAttribute("data-nz-crecido", "");
          });
        }, 2500);
      }
    }

    /* ---------- 3. Leyenda clicable (filtra la serie por data-serie) ---------- */
    cada(document.querySelectorAll(".nz-legend__item"), function (item) {
      if (item.tagName !== "BUTTON") {
        if (!item.getAttribute("role")) item.setAttribute("role", "button");
        if (item.getAttribute("tabindex") === null) item.setAttribute("tabindex", "0");
      }
      if (item.getAttribute("aria-pressed") === null) item.setAttribute("aria-pressed", "true");

      function alterna() {
        var estabaActivo = item.getAttribute("aria-pressed") !== "false";
        var activo = !estabaActivo;
        item.setAttribute("aria-pressed", activo ? "true" : "false");
        item.classList.toggle("is-selected", !activo);
        var serie = item.getAttribute("data-serie");
        if (!serie) return;
        var ambito = item.closest(SEL_GRAFICO) || document;
        cada(ambito.querySelectorAll("[data-serie]"), function (el) {
          if (el !== item && el.getAttribute("data-serie") === serie) {
            el.classList.toggle("is-selected", !activo);
          }
        });
      }

      item.addEventListener("click", alterna);
      item.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
          e.preventDefault();
          alterna();
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
