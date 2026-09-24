# branding — identidad Alkalma Health

Fuente única de los elementos de marca de AEGIS (sección 5 del requerimiento funcional).
Todo lo visual del frontend se lee de tokens; ningún componente usa un color, fuente o logo "a mano".

## Dónde vive cada cosa

| Elemento | Ubicación | Notas |
|---|---|---|
| Tokens (paleta oficial, tipografía Montserrat, radios, sombras) | `frontend/src/theme/brand-tokens.ts` | Único archivo que el equipo de marca debe tocar. |
| Logo oficial (color, sobre fondo claro) | `branding/alkalma-logo.png` | Copia servida por Vite en `frontend/public/branding/`. |
| Logo negativo (blanco, sobre indigo/gradiente) | `branding/alkalma-logo-white.png` | Usado en la pantalla de login. |
| Favicon (loto simplificado) | `frontend/public/branding/favicon.svg` | Derivado; no es el emblema oficial. |
| Textos de interfaz ES/EN | `frontend/src/i18n/{es,en}.json` | i18n con react-i18next; default ES, persistido en `localStorage` (`aegis.lang`). |
| Guía de uso | este archivo | Fuente: Alkalma Brand Guidelines V1.0 (Sept 2024). |

## Paleta oficial (jerarquía 50 / 25 / 12.5 / 6.25)

| Token | HEX | Peso | Uso en AEGIS |
|---|---|---|---|
| `indigo` | `#16455C` | 50% | texto, títulos, botón primario, toggle de idioma activo |
| `turquoise` | `#70C8C3` | 25% | acento: ítem activo del menú, badges de cumplimiento, focus de inputs |
| `bluegray` | `#8B9EA5` | 12.5% | texto secundario, cabeceras de tabla |
| `azureWhite` | `#F7FBFC` | 6.25% | fondo de página |
| `steelBlue` | `#007493` | secundario | enlaces; forma el gradiente de marca con indigo |
| `amber` | `#E9A941` | secundario | franja de "modo sin autenticación", severidad mayor |
| `lime` / `pink` | `#BADE8C` / `#EFB6BE` | secundario | reservados para categorías futuras |
| `danger` | `#B3261E` | excepción | única salida de la paleta: errores y severidad crítica (convención clínica) |

Gradiente digital: `linear-gradient(135deg, #16455C 0%, #007493 100%)` (login, avatar).
Tipografía: Montserrat 300/400/500/700 vía Google Fonts (`index.html`).

Nombre público del producto: **AEGIS — Clinical Governance Platform by Alkalma Health**
(sujeto a aprobación final de marca). Tagline de marca: *United in Well-Being*.

## Reglas del brandbook aplicadas

- Logo a color solo sobre fondo claro (header blanco); versión blanca sobre gradiente (login).
- Sin sombras, outlines, recolor ni distorsión del logo. Altura mínima 34 px en header (> 40 px de ancho mínimo).
- Espaciado generoso, radios 12–16 px, sombras con tinte indigo, sin negros puros.
- Contraste AA: texto indigo sobre blanco/azure/turquoise; texto blanco sobre indigo/steel blue.

## Insumos pendientes (sección 5.2 del funcional)

- [ ] Confirmación de logotipo definitivo en SVG (hoy PNG del brandbook).
- [ ] Plantillas de correo.
- [ ] Plantilla corporativa de reportes (PDF) para el Publisher Engine (M09).

Al recibirlos: reemplazar los PNG en `branding/` y en `frontend/public/branding/`, ajustar
`brand-tokens.ts` si cambia algún valor, y nada más: los componentes no requieren cambios.
