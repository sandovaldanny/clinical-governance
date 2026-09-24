import { Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { AUTH_DISABLED } from "../api/client";
import { LanguageToggle } from "../components/LanguageToggle";
import { ProfileMenu } from "../components/ProfileMenu";
import { brandTokens } from "../theme/brand-tokens";
import { Sidebar } from "./Sidebar";

/**
 * Shell de navegación: header blanco con logo Alkalma (izquierda) y selector de idioma +
 * perfil (derecha), sidebar por módulo y área principal. Branding vía brand-tokens.ts.
 */
export function AppShell() {
  const { t } = useTranslation();

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {AUTH_DISABLED && (
        <div
          role="status"
          style={{
            background: brandTokens.colors.warning,
            color: brandTokens.colors.textPrimary,
            padding: "6px 24px",
            fontSize: 13,
            fontWeight: 500,
            textAlign: "center",
          }}
        >
          {t("app.devBanner")}
        </div>
      )}

      <header
        style={{
          background: brandTokens.colors.surface,
          borderBottom: `1px solid ${brandTokens.colors.border}`,
          boxShadow: brandTokens.shadow.card,
          padding: "0 28px",
          height: 72,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 24,
          position: "sticky",
          top: 0,
          zIndex: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20, minWidth: 0 }}>
          <img
            src={brandTokens.logoUrl}
            alt="Alkalma Health"
            style={{ height: 34, width: "auto", display: "block" }}
          />
          <span aria-hidden style={{ width: 1, height: 32, background: brandTokens.colors.border }} />
          <div style={{ lineHeight: 1.15, minWidth: 0 }}>
            <span
              style={{
                display: "block",
                fontSize: 17,
                fontWeight: 700,
                letterSpacing: "0.08em",
                color: brandTokens.colors.textPrimary,
              }}
            >
              {t("app.name")}
            </span>
            <span
              style={{
                display: "block",
                fontSize: 12,
                color: brandTokens.colors.textSecondary,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {t("app.tagline")}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <LanguageToggle />
          <ProfileMenu />
        </div>
      </header>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <Sidebar />
        <main
          style={{
            flex: 1,
            padding: "36px 40px 64px",
            background: brandTokens.colors.background,
            overflowY: "auto",
            minWidth: 0,
          }}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}
