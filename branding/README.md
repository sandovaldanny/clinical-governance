# branding — identidad Alkalma Health

Fuente única de los elementos de marca de AEGIS (sección 5 del requerimiento funcional).
Todo lo visual del frontend se lee de tokens; ningún componente usa un color, fuente o logo "a mano".

## Dónde vive cada cosa

| Elemento | Ubicación | Notas |
|---|---|---|
| Tokens (colores, tipografía, nombre de producto) | `frontend/src/theme/brand-tokens.ts` | Único archivo que el equipo de marca debe reemplazar. |
| Logo (placeholder) | `branding/alkalma-logo-placeholder.svg` | Copia servida por Vite en `frontend/public/branding/`. |
| Guía de uso | este archivo | — |

## Tokens vigentes (placeholder)

| Token | Valor | Uso |
|---|---|---|
| `primary` | `#0F4C5C` | encabezado, botones primarios, enlaces activos |
| `accent` | `#2E9E8F` | acentos, estados positivos secundarios |
| `background` | `#F7F9FA` | fondo de página |
| `surface` | `#FFFFFF` | tarjetas, tablas, formularios |
| `textPrimary` | `#1A2B33` | texto principal |
| `textSecondary` | `#5B6B72` | subtítulos, ayudas |
| `danger` / `warning` / `success` | `#B3261E` / `#B45309` / `#1E7A46` | severidad crítica / mayor / cumplimiento |
| `fontFamily` | `Inter, system-ui, sans-serif` | — |

Nombre público del producto: **AEGIS — Clinical Governance Platform by Alkalma Health**
(sujeto a aprobación final de marca).

## Insumos pendientes (sección 5.2 del funcional)

- [ ] Logotipo oficial en formato digital (SVG/PNG).
- [ ] Paleta oficial de colores y reglas de uso.
- [ ] Tipografías oficiales y licencias.
- [ ] Plantillas de correo.
- [ ] Plantilla corporativa de reportes (PDF) para el Publisher Engine (M09).

Al recibirlos: reemplazar el SVG en `branding/` y en `frontend/public/branding/`, actualizar
`brand-tokens.ts`, y nada más — los componentes no requieren cambios.
