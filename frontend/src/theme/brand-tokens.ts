/**
 * Tokens de marca Alkalma Health — Brand Guidelines V1.0 (Sept 2024).
 *
 * Único punto de branding del frontend (sección 5 del requerimiento funcional). Ningún
 * componente usa un color, fuente o logo "a mano": todo se lee de aquí. Los assets viven en
 * `branding/` (fuente) y `frontend/public/branding/` (copia servida).
 *
 * Jerarquía visual oficial: Indigo 50% · Turquoise 25% · Blue Gray 12.5% · Azure White 6.25%.
 */
export const alkalma = {
  // Paleta primaria
  indigo: "#16455C",
  turquoise: "#70C8C3",
  bluegray: "#8B9EA5",
  azureWhite: "#F7FBFC",
  // Paleta secundaria
  steelBlue: "#007493",
  lime: "#BADE8C",
  pink: "#EFB6BE",
  amber: "#E9A941",
  // Variaciones (derivadas del brandbook digital)
  indigoDark: "#0E2E3D",
  indigoLight: "#2A6582",
  turquoiseDark: "#4FA8A3",
  turquoiseLight: "#A4DDDA",
  turquoiseTint: "#E6F5F4",
  bgSoft: "#EEF5F8",
  border: "#DCE5EA",
} as const;

export const brandTokens = {
  productName: "AEGIS",
  productTagline: "Clinical Governance Platform by Alkalma Health",
  brandTagline: "United in Well-Being",
  logoUrl: "/branding/alkalma-logo.png",
  logoWhiteUrl: "/branding/alkalma-logo-white.png",
  colors: {
    primary: alkalma.indigo,
    primaryHover: alkalma.indigoDark,
    primaryContrast: "#FFFFFF",
    accent: alkalma.turquoise,
    accentSoft: alkalma.turquoiseTint,
    link: alkalma.steelBlue,
    background: alkalma.azureWhite,
    surface: "#FFFFFF",
    surfaceSoft: alkalma.bgSoft,
    border: alkalma.border,
    textPrimary: alkalma.indigo,
    textSecondary: alkalma.bluegray,
    // Semánticos. `danger` es la única excepción fuera de paleta (estados de error/crítico
    // exigen rojo por convención clínica); warning/success usan colores oficiales.
    danger: "#B3261E",
    warning: alkalma.amber,
    success: alkalma.turquoiseDark,
  },
  gradient: "linear-gradient(135deg, #16455C 0%, #007493 100%)",
  fontFamily: "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
  radius: { sm: 8, md: 12, lg: 16 },
  shadow: {
    card: "0 2px 12px rgba(22, 69, 92, 0.06)",
    hover: "0 6px 24px rgba(22, 69, 92, 0.10)",
  },
} as const;
