# Contrato único: registro de contradicciones de la auditoría (A01–A13)

Fuente: `AURORA-AUDITORIA.md` (revisión `d0278f5`, censo 10.1.0) y `AURORA-PLAN-DE-MEJORA.md`.
Este registro es la **línea base de verdad** del contrato vigente: documenta qué regla
mandaba antes, cuál manda ahora y qué comprobación lo garantiza. La documentación
histórica vive en `docs/planes/` y **no se inyecta en el prompt de generación**.

Estado de cada hallazgo tras la aplicación del plan (orden P0 → P2):

| ID | Hallazgo | Regla vigente (la que manda ahora) | Garantía |
|---|---|---|---|
| A01 | Prohibición absoluta de glass vs. `p16-cristal.css` implementado y exceptuado | El cristal es una **capa oficial de excepción controlada**: única capa con blur/gradiente, uso en navegación o superficie flotante, con fallback opaco por tema; todo lo demás, cero | `COMPOSICION.md` ley 11, `AGENTS.md` regla 3, `LLM.md` anti-patrones; `validar-css.py` exceptúa solo `p16-cristal` |
| A02 | `Navegacion` con `href="#"` y marca `span` | `Navegacion` acepta `inicio` (homeRoute): la marca es `<a>` al inicio del producto; sin destino admisible no se pinta enlace; en modo producto el `#` placeholder es **fallo** | `openui/aurora-openui.js` (`urlAdmitida`), `auditar-enlaces.py` (modo `data-nz-modo="producto"`), `--inicio` en compilador/horneado |
| A03 | Acciones sin contrato de comportamiento | **Pendiente (Entrega 3 del plan):** ActionRegistry con loading/éxito/error/disabled/permisos y distinción documento/prototipo/aplicación. Hoy: `Boton` con `href` es enlace real; sin `href`, botón declarativo — ninguna pantalla se declara «aplicación conectada» sin handler | Plan §10 Entrega 3 · backlog B08 |
| A04 | URLs escapadas como HTML, sin política de protocolos | Política de protocolos **doble**: el compilador rechaza el programa (`javascript:`/`vbscript:`/`data:`) y los renderers no pintan enlaces con esquema inadmisible | `programa-a-html.py` `politica_url()`, `aurora-openui.js` `urlAdmitida()`, `auditar-enlaces.py` (protocolos = fallo) |
| A05 | Auditoría tipográfica sobre texto del HTML | Pendiente de medición computada en navegador; parcialmente cubierta por la matriz de producto (§12.3) | `scripts/probar-producto.py` (medición computada) |
| A06 | Color contado por clases, no por composición | Se mantiene el presupuesto de5 momentos (freno), y las **referencias de producto** se revisan visualmente (§12.2) antes de ser normativas | `auditar-uso.py` + revisión humana de `examples/golden/` |
| A07 | Cristal desconectado del contrato generativo | Expuesto como material en la doctrina (A01) con su modo `data-nz-estilo="cristal"` y fallbacks corregidos; la exposición en firmas OpenUI sigue pendiente de la Entrega 2/4 | `packs/p16-cristal.css` fallbacks, `LLM.md` |
| A08 | Firma personal obligatoria en shell y doctrina | Firma = **política configurable** `data-nz-firma`: `none` (0), `subtle` (1 línea), `full` (pie, 1 vez). Repetida = fallo. Licencias aparte en `NOTICE.md` | `--firma` en `programa-a-html.py`/`hornear.py`, `auditar-uso.py` (`firma-*`) |
| A09 | Preset de marca sin carga explícita | El compilador **enlaza siempre** `marcas/<marca>.css` tras `tokens.css`; marca inexistente = error con diagnóstico (sin fallback silencioso) | `programa-a-html.py`/`hornear.py`, verificación computada en `probar-producto.py` |
| A10 | Responsive estructural, sin producto usable | Matriz mínima de navegador: landing/detalle × 390/768/1440 con overflow medido, enlaces resueltos y estilos computados; ampliación por regresión real | `scripts/probar-producto.py` |
| A11 | Documentación y versiones desalineadas | README con recuento vivo único (2.195 objetos), badge y canal `@v10`; canal vivo coherente con los tags publicados; consumidores fijados de la serie 9 intactos | `README.md`, `CONTRATO.md`, `generar-llm-docs.py` |
| A12 | Catálogo sin superficie recomendada clara | **Pendiente (Entrega 4 del plan):** núcleo/extensiones/compatibilidad y manifiestos por arquetipo con contexto medido | Plan §10 Entrega 4 · backlog B10 |
| A13 | Generación vinculada a `~/.hermes` | **Pendiente (Entrega 4 del plan):** configuración de proveedor explícita y ruta sin modelo reproducible | Plan §10 Entrega 4 · backlog B11 |

Advertencias de alcance de la propia auditoría, respetadas aquí:

- La auditoría **no ejecutó** los auditores (su entorno no tenía Python): sus
  observaciones de código son inferencias. Las comprobaciones de este registro están
  ejecutadas en local y la cadena CI completa debe quedar en verde antes del release.
- Las referencias visuales proceden de la captura facilitada, no de una sesión
  interactiva propia. La revisión visual humana (§12.2) sigue siendo el paso que
  convierte `examples/golden/` en referencia normativa.
- No se retiran familias ni se borra CSS: la reducción exige manifiesto de
  deprecaciones y migración (plan §5.2, backlog B13).
