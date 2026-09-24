import { useTranslation } from "react-i18next";

import { SUPPORTED_LANGUAGES, type Language } from "../i18n";
import { brandTokens } from "../theme/brand-tokens";

/** Selector ES | EN siempre visible en el header. Persiste en localStorage (aegis.lang). */
export function LanguageToggle() {
  const { i18n, t } = useTranslation();
  const current = (i18n.resolvedLanguage ?? "es") as Language;

  return (
    <div
      role="group"
      aria-label={t("app.language")}
      style={{
        display: "inline-flex",
        border: `1px solid ${brandTokens.colors.border}`,
        borderRadius: 999,
        padding: 2,
        background: brandTokens.colors.surface,
      }}
    >
      {SUPPORTED_LANGUAGES.map((lng) => {
        const active = lng === current;
        return (
          <button
            key={lng}
            type="button"
            aria-pressed={active}
            onClick={() => i18n.changeLanguage(lng)}
            style={{
              border: "none",
              borderRadius: 999,
              padding: "4px 12px",
              fontSize: 12,
              fontWeight: 600,
              letterSpacing: "0.04em",
              background: active ? brandTokens.colors.primary : "transparent",
              color: active ? brandTokens.colors.primaryContrast : brandTokens.colors.textSecondary,
              transition: "background .15s, color .15s",
            }}
          >
            {lng.toUpperCase()}
          </button>
        );
      })}
    </div>
  );
}
