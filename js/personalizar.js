/* ============================================================
   personalizar.js — el motor de temas, en el navegador
   ------------------------------------------------------------
   Mismas cuentas que scripts/generar-marca.py, pero en vivo: eliges cualquier
   color y genera la rampa completa en OKLCH (luz uniforme), la ancla al paso
   primario (marca→600, acento→500) y la ajusta para que cumpla contraste AA.

   No es un truco de la portada: es el mismo modelo que el generador del repo.
   Genera el CSS de una marca concreta con:
       python scripts/generar-marca.py miweb "#0ea5e9" "#f43f5e"

   Hecho con ❤️ por David Antizar
   ============================================================ */
(function () {
  'use strict';

  /* ---------- sRGB <-> OKLab/OKLCH (las mismas fórmulas que el generador) ---------- */
  function srgbALineal(v) {
    v /= 255;
    return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  }
  function linealASrgb(v) {
    v = Math.max(0, Math.min(1, v));
    return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
  }
  function hexARgb(hex) {
    hex = String(hex).trim().replace('#', '');
    if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    if (!/^[0-9a-fA-F]{6}$/.test(hex)) return null;
    return [parseInt(hex.slice(0, 2), 16), parseInt(hex.slice(2, 4), 16), parseInt(hex.slice(4, 6), 16)];
  }
  function hexAOklch(hex) {
    var rgb = hexARgb(hex);
    if (!rgb) return null;
    var r = srgbALineal(rgb[0]), g = srgbALineal(rgb[1]), b = srgbALineal(rgb[2]);
    var l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b;
    var m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b;
    var s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b;
    var l_ = Math.cbrt(l), m_ = Math.cbrt(m), s_ = Math.cbrt(s);
    var L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_;
    var A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_;
    var B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_;
    var H = Math.atan2(B, A) * 180 / Math.PI;
    return { L: L, C: Math.hypot(A, B), H: (H % 360 + 360) % 360 };
  }
  function oklchAHex(L, C, H) {
    var a = H * Math.PI / 180, ca = Math.cos(a), sa = Math.sin(a);
    function lineal(c) {
      var A = c * ca, B = c * sa;
      var l_ = L + 0.3963377774 * A + 0.2158037573 * B;
      var m_ = L - 0.1055613458 * A - 0.0638541728 * B;
      var s_ = L - 0.0894841775 * A - 1.2914855480 * B;
      var l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
      return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
              -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
              -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s];
    }
    var lo = 0, hi = C, mid, v;
    for (var i = 0; i < 28; i++) {
      mid = (lo + hi) / 2; v = lineal(mid);
      if (v[0] >= -1e-4 && v[0] <= 1 + 1e-4 && v[1] >= -1e-4 && v[1] <= 1 + 1e-4 &&
          v[2] >= -1e-4 && v[2] <= 1 + 1e-4) lo = mid; else hi = mid;
    }
    v = lineal(lo);
    return '#' + v.map(function (x) {
      return ('0' + Math.round(linealASrgb(x) * 255).toString(16)).slice(-2);
    }).join('');
  }

  /* ---------- contraste WCAG ---------- */
  function luminancia(hex) {
    var rgb = hexARgb(hex);
    if (!rgb) return 0;
    return 0.2126 * srgbALineal(rgb[0]) + 0.7152 * srgbALineal(rgb[1]) + 0.0722 * srgbALineal(rgb[2]);
  }
  function contraste(a, b) {
    var x = luminancia(a), y = luminancia(b);
    var hi = Math.max(x, y), lo = Math.min(x, y);
    return (hi + 0.05) / (lo + 0.05);
  }

  /* ---------- rampa: ancla en el paso primario + taper de croma ---------- */
  var OFF_MARCA = { 50: 0.425, 100: 0.390, 200: 0.339, 300: 0.262, 400: 0.158,
                    500: 0.077, 600: 0, 700: -0.058, 800: -0.122, 900: -0.167 };
  var OFF_ACENTO = { 50: 0.348, 100: 0.313, 200: 0.262, 300: 0.185,
                     400: 0.081, 500: 0, 600: -0.077, 700: -0.135 };
  var REF = 0.546, TECHO = 0.97, SUELO = 0.10;

  function luzDe(luzFuente, off) {
    if (off > 0) {
      var esc = Math.min(1, Math.max(0.05, TECHO - luzFuente) / (TECHO - REF));
      return Math.min(TECHO, Math.max(SUELO, luzFuente + off * esc));
    }
    if (off < 0) {
      var esc2 = Math.max(0.05, luzFuente - SUELO) / (REF - SUELO);
      return Math.min(TECHO, Math.max(SUELO, luzFuente + off * esc2));
    }
    return luzFuente;
  }

  function rampa(hex, offsets, ancla) {
    var o = hexAOklch(hex);
    if (!o) return null;
    var orden = Object.keys(offsets).map(Number), iAncla = orden.indexOf(ancla);
    var salida = {};
    orden.forEach(function (paso, i) {
      if (paso === ancla) { salida[paso] = hex.toLowerCase(); return; }
      var d = Math.abs(i - iAncla);
      var croma = o.C * (d <= 1 ? 1 : d === 2 ? 0.85 : d === 3 ? 0.62 : 0.4);
      salida[paso] = oklchAHex(luzDe(o.L, offsets[paso]), croma, o.H);
    });
    return salida;
  }

  /* Si el color no aguanta texto blanco, se oscurece lo justo y se avisa. */
  function ajustarAA(hex, objetivo) {
    objetivo = objetivo || 4.5;
    if (contraste(hex, '#ffffff') >= objetivo) return { hex: hex, ajustado: false, ratio: contraste(hex, '#ffffff') };
    var o = hexAOklch(hex);
    if (!o) return { hex: hex, ajustado: false, ratio: 1 };
    for (var i = 0; i < 90; i++) {
      o.L -= 0.004;
      if (o.L < 0.15) break;
      var cand = oklchAHex(o.L, o.C, o.H);
      if (contraste(cand, '#ffffff') >= objetivo) return { hex: cand, ajustado: true, ratio: contraste(cand, '#ffffff') };
    }
    return { hex: hex, ajustado: false, ratio: contraste(hex, '#ffffff') };
  }

  /* ---------- aplicar al documento ---------- */
  var raiz = document.documentElement;

  function aplicarMarca(hexMarca, hexAcento) {
    var m = ajustarAA(hexMarca);
    var rm = rampa(m.hex, OFF_MARCA, 600);
    var ra = rampa(hexAcento, OFF_ACENTO, 500);
    if (!rm || !ra) return null;
    raiz.removeAttribute('data-nz-marca');           // el color propio manda
    Object.keys(rm).forEach(function (k) { raiz.style.setProperty('--nz-marca-' + k, rm[k]); });
    Object.keys(ra).forEach(function (k) { raiz.style.setProperty('--nz-acento-' + k, ra[k]); });
    return { marca: m, acento: { hex: hexAcento.toLowerCase() }, marcaPasos: rm };
  }

  function limpiarMarca() {
    var props = raiz.style;
    Object.keys(OFF_MARCA).forEach(function (k) { props.removeProperty('--nz-marca-' + k); });
    Object.keys(OFF_ACENTO).forEach(function (k) { props.removeProperty('--nz-acento-' + k); });
  }

  /* ---------- tipografía bajo demanda ---------- */
  var FUENTES = {
    inter: { nombre: 'Inter', param: 'Inter:wght@400..800', pila: '"Inter", "Inter Variable", system-ui, sans-serif' },
    geist: { nombre: 'Geist', param: 'Geist:wght@400..800', pila: '"Geist", system-ui, sans-serif' },
    manrope: { nombre: 'Manrope', param: 'Manrope:wght@400..800', pila: '"Manrope", system-ui, sans-serif' },
    jakarta: { nombre: 'Plus Jakarta Sans', param: 'Plus+Jakarta+Sans:wght@400..800', pila: '"Plus Jakarta Sans", system-ui, sans-serif' },
    grotesk: { nombre: 'Space Grotesk', param: 'Space+Grotesk:wght@400..700', pila: '"Space Grotesk", system-ui, sans-serif' },
    system: { nombre: 'Sistema', param: null, pila: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif' }
  };
  var cargadas = {};
  function cargarFuente(clave) {
    var f = FUENTES[clave];
    if (!f || !f.param || cargadas[clave]) return;
    cargadas[clave] = true;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=' + f.param + '&display=swap';
    document.head.appendChild(l);
  }
  function aplicarFuente(clave) {
    var f = FUENTES[clave] || FUENTES.inter;
    cargarFuente(clave);
    raiz.style.setProperty('--nz-font', f.pila);
    raiz.style.setProperty('--nz-font-titulo', f.pila);
    return f.nombre;
  }

  /* ---------- API pública (la usa la portada y cualquier página) ---------- */
  window.aurora = {
    aplicarMarca: aplicarMarca,
    limpiarMarca: limpiarMarca,
    aplicarFuente: aplicarFuente,
    cargarFuente: cargarFuente,
    ajustarAA: ajustarAA,
    contraste: contraste,
    fuentes: FUENTES
  };

  /* ---------- cableado de la interfaz, si existe en la página ---------- */
  function $(id) { return document.getElementById(id); }

  function pintaRampa() {
    var cont = $('marcasRampa');
    if (!cont) return;
    var cs = getComputedStyle(raiz), html = '';
    [50, 100, 200, 300, 400, 500, 600, 700, 800, 900].forEach(function (p) {
      var c = cs.getPropertyValue('--nz-marca-' + p).trim();
      html += '<span style="background:' + c + ';color:' + (p >= 500 ? '#fff' : '#111827') + '">' + p + '</span>';
    });
    cont.innerHTML = html;
  }

  function pintaAviso(res) {
    var aviso = $('marcaAviso');
    if (!aviso || !res) return;
    var r = res.marca.ratio.toFixed(2);
    var ok = res.marca.ratio >= 4.5;
    aviso.innerHTML = (res.marca.ajustado
      ? 'Tu color no aguantaba el texto blanco, así que lo he oscurecido a <code>' + res.marca.hex +
        '</code> para que cumpla AA. '
      : 'Tu color ya cumple AA tal cual. ') +
      'Contraste del botón: <b>' + r + '</b> ' + (ok ? '✅' : '⚠️');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var inMarca = $('inputMarca'), inAcento = $('inputAcento');
    if (!inMarca || !inAcento) return;

    var guardado = null;
    try { guardado = JSON.parse(localStorage.getItem('nz-tema') || 'null'); } catch (e) { /* irrelevante */ }

    function guarda(datos) { try { localStorage.setItem('nz-tema', JSON.stringify(datos)); } catch (e) {} }

    function aplicaTodo(avisar) {
      var res = aplicarMarca(inMarca.value, inAcento.value);
      pintaRampa();
      if (avisar !== false) pintaAviso(res);
      return res;
    }

    inMarca.addEventListener('input', function () { aplicaTodo(); pintaRampa(); guarda({ m: inMarca.value, a: inAcento.value, f: $('selFuente') && $('selFuente').value, e: raiz.getAttribute('data-nz-estilo') }); });
    inAcento.addEventListener('input', function () { aplicaTodo(); guarda({ m: inMarca.value, a: inAcento.value, f: $('selFuente') && $('selFuente').value, e: raiz.getAttribute('data-nz-estilo') }); });

    var reset = $('btnAurora');
    if (reset) reset.addEventListener('click', function () {
      limpiarMarca();
      raiz.setAttribute('data-nz-marca', 'aurora');
      inMarca.value = '#2563eb'; inAcento.value = '#f97316';
      pintaRampa();
      var aviso = $('marcaAviso');
      if (aviso) aviso.innerHTML = 'De vuelta a <b>Aurora</b>: azul <code>#2563eb</code> y naranja <code>#f97316</code>.';
      guarda({ m: inMarca.value, a: inAcento.value, f: $('selFuente') && $('selFuente').value, e: raiz.getAttribute('data-nz-estilo') });
    });

    var selFuente = $('selFuente');
    if (selFuente) {
      // carga la fuente elegida por defecto para que el primer pintado sea el bueno
      cargarFuente(selFuente.value);
      selFuente.addEventListener('change', function () {
        aplicarFuente(selFuente.value);
        var e = $('fuenteAviso'); if (e) e.textContent = FUENTES[selFuente.value].nombre;
        guarda({ m: inMarca.value, a: inAcento.value, f: selFuente.value, e: raiz.getAttribute('data-nz-estilo') });
      });
    }

    var selEstilo = $('selEstilo');
    if (selEstilo) selEstilo.addEventListener('change', function () {
      if (selEstilo.value === 'cristal') raiz.setAttribute('data-nz-estilo', 'cristal');
      else raiz.removeAttribute('data-nz-estilo');
      guarda({ m: inMarca.value, a: inAcento.value, f: selFuente && selFuente.value, e: selEstilo.value });
    });

    if (guardado) {
      if (guardado.m) inMarca.value = guardado.m;
      if (guardado.a) inAcento.value = guardado.a;
      if (guardado.f && selFuente) selFuente.value = guardado.f;
      if (guardado.e && selEstilo) { selEstilo.value = guardado.e; if (guardado.e === 'cristal') raiz.setAttribute('data-nz-estilo', 'cristal'); }
      if (guardado.f && selFuente) aplicarFuente(guardado.f);
    }
    aplicaTodo();
  });
})();
