# Ley de elevación — «editorial de archivo»

Dirección visual de Aurora desde la 10.10.x. Sustituye la elevación por capas
(xs · sm · md · lg · xl · glows de marca) por **una sola altura**.

## La regla

1. **En el flujo no se proyecta sombra.** Un contenedor, una tarjeta, una tabla o un
   KPI se definen con **línea de 1px** (`--nz-border-w`) y fondo
   (`--nz-surface`), nunca con una sombra.
2. **Flota solo lo que se superpone**: modal, drawer, hoja, menú, desplegable, popover,
   toast, tooltip, lightbox, spotlight, paleta de comandos, ventana del shell y FAB.
   Todo eso usa **`--nz-shadow-xl`**, el único nivel con valor. `--nz-shadow-float` es su alias.
3. **`--nz-shadow-xs`, `-sm`, `-md`, `-lg` valen `none`.** Los nombres se conservan para no
   romper consumidores: cualquier componente antiguo que las use simplemente se aplana.
4. **`--nz-shadow-brand` y `--nz-shadow-accent` valen `none`.** El acento se comunica con
   color de fondo, línea de 1px o barra `inset 3px`, nunca con un resplandor: un glow azul
   se convierte en un glow negro al pasar a monocromo y delata el apaño.
5. **Lo que no es elevación no es una sombra**: los anillos de foco
   (`--nz-focus-ring*`), las líneas de 1px hechas con `inset` y los halos de estado
   (`0 0 0 Npx`) tienen su propio hueco y su propio token.

## Por qué

- Un sistema plano con radios a 0 y cinco niveles de sombra se contradice: la sombra da
  volumen a una geometría que dice «papel».
- La jerarquía pasa a la **tipografía, la línea y el aire**, que es lo único que sobrevive
  igual en claro, oscuro y monocromo.
- Con los glows neutralizados, cambiar de marca es cambiar `--nz-marca-*`: no hay sombras
  de color que rehacer.

## Cómo se comprueba

```bash
python scripts/auditar-elevacion.py     # en CI, tras validar-css
```

- 0 infracciones: ninguna sombra proyectada fuera de un overlay.
- Avisos permitidos: bisel de 1px de `.nz-kbd` y anillos de estado pendientes de token.

## Excepciones declaradas

| Caso | Por qué |
|---|---|
| `p16-cristal.css` (`--nz-cristal-sombra`) | capa opcional con su propia doctrina (material) |
| Shell de ventanas de `p15-apps.css` | un escritorio simulado necesita profundidad diegética |
| `.nz-kbd` | bisel físico de 1px, no elevación |
| `icon-tile--circle`, avatares, puntos de estado | círculo por convención del objeto, no por decoración |
