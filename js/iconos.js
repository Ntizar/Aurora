/* Aurora · catálogo de iconos numerados.
   Filtro por número, nombre o id de Lucide, cambio de tono en vivo y copia del
   código del icono. Sin dependencias.

   Si este fichero no carga, la página sigue siendo usable: los iconos están en el
   HTML, se leen y se copian a mano, y el color se pone con el modificador que
   explica la sección «Cómo se usa». */
(() => {
  "use strict";

  const rejilla = document.getElementById("rejillaIconos");
  const buscador = document.getElementById("buscarIcono");
  const cuenta = document.getElementById("cuentaIconos");
  if (!rejilla || !buscador) return;

  const fichas = Array.from(rejilla.querySelectorAll("[data-icono]"));
  const total = fichas.length;

  const plano = (t) =>
    (t || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();

  fichas.forEach((f) => { f.dataset.busca = plano(f.dataset.buscar); });

  const pinta = () => {
    const q = plano(buscador.value);
    let visibles = 0;
    fichas.forEach((f) => {
      const coincide = !q || f.dataset.busca.includes(q);
      f.hidden = !coincide;
      if (coincide) visibles += 1;
    });
    if (cuenta) {
      cuenta.textContent = q
        ? visibles + " de " + total + " iconos"
        : total + " iconos · todos visibles";
    }
  };

  buscador.addEventListener("input", pinta);
  buscador.addEventListener("search", pinta);
  pinta();

  /* --- Tono ---------------------------------------------------------------
     El trazo del icono es currentColor: no hay que recolorear el SVG, basta con
     cambiar la caja que lo envuelve. Se usan las clases del sistema
     (.nz-icon-tile--accent …), nunca un color suelto escrito en el DOM. */
  const botonesTono = Array.from(document.querySelectorAll("[data-tono]"));
  const cajas = Array.from(rejilla.querySelectorAll(".nz-icon-tile"));

  const pintaTono = (valor) => {
    cajas.forEach((caja) => {
      caja.className = "nz-icon-tile" + (valor ? " nz-icon-tile--" + valor : "");
    });
    botonesTono.forEach((b) => {
      const activo = b.dataset.tono === valor;
      b.classList.toggle("is-active", activo);
      b.setAttribute("aria-pressed", activo ? "true" : "false");
    });
  };

  if (botonesTono.length) {
    botonesTono.forEach((b) => {
      b.addEventListener("click", () => pintaTono(b.dataset.tono));
    });
    /* ?tono=acento abre el catálogo ya en naranja: sirve para enseñar el
       resultado sin tener que pulsar nada. */
    const pedido = new URLSearchParams(window.location.search).get("tono");
    const conocido = botonesTono.some((b) => b.dataset.tono === pedido);
    pintaTono(conocido ? pedido : "");
  }

  /* Copiar: el botón de cada ficha lleva el id (nz-i-042). Se copia el uso por
     sprite —el que no engorda el HTML del consumidor— con el tono que esté puesto. */
  const aviso = (texto) => {
    if (!cuenta) return;
    const previo = cuenta.textContent;
    cuenta.textContent = texto;
    window.setTimeout(() => { cuenta.textContent = previo; }, 1600);
  };

  rejilla.addEventListener("click", (ev) => {
    const boton = ev.target.closest("[data-copiar]");
    if (!boton) return;
    const id = boton.dataset.copiar;
    const activo = botonesTono.find((b) => b.classList.contains("is-active"));
    const tono = activo && activo.dataset.tono ? " nz-icon--" + activo.dataset.tono : "";
    const codigo = '<svg class="nz-icon' + tono + '" aria-hidden="true"><use href="iconos/sprite.svg#' + id + '"/></svg>';
    const listo = () => aviso("Copiado " + id);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(codigo).then(listo, () => aviso("No se pudo copiar " + id));
    } else {
      aviso("Copia manual: " + codigo);
    }
  });
})();
