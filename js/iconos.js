/* Aurora · catálogo de iconos numerados.
   Filtro por número, nombre o id de Lucide y copia del código del icono.
   Sin dependencias. Si este fichero no carga, la página sigue siendo usable:
   los 288 iconos están en el HTML y se pueden leer y copiar a mano. */
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

  /* Copiar: el botón de cada ficha lleva el id (nz-i-042). Se copia el uso por
     sprite, que es el que no engorda el HTML del consumidor. */
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
    const codigo = '<svg class="nz-icon" aria-hidden="true"><use href="iconos/sprite.svg#' + id + '"/></svg>';
    const listo = () => aviso("Copiado " + id);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(codigo).then(listo, () => aviso("No se pudo copiar " + id));
    } else {
      aviso("Copia manual: " + codigo);
    }
  });
})();
