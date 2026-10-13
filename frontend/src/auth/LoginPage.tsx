import { useState } from "react";
import { useTranslation } from "react-i18next";

import { login } from "../api/client";
import { LanguageToggle } from "../components/LanguageToggle";
import { brandTokens } from "../theme/brand-tokens";
import { useAuth } from "./AuthContext";

/**
 * Pantalla de acceso con branding Alkalma (sección 6.1 del funcional): sin acceso anónimo.
 * El identificador es el correo o solo su parte local (`admin`).
 */
export function LoginPage() {
  const { t } = useTranslation();
  const { setSession } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const result = await login(identifier, password);
      setSession({ token: result.access_token, mustChangePassword: result.must_change_password });
    } catch {
      setError(t("login.error"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "minmax(0, 5fr) minmax(0, 4fr)" }}>
      <section
        style={{
          background: brandTokens.gradient,
          color: brandTokens.colors.primaryContrast,
          padding: "56px 64px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <img src={brandTokens.logoWhiteUrl} alt="Alkalma Health" style={{ height: 44, width: "auto", alignSelf: "flex-start" }} />
        <div>
          <p style={{ fontSize: 13, letterSpacing: "0.14em", textTransform: "uppercase", opacity: 0.8, margin: 0 }}>
            {t("app.name")}
          </p>
          <h1 style={{ fontSize: 40, fontWeight: 300, margin: "12px 0 0", maxWidth: 520 }}>{t("app.tagline")}</h1>
        </div>
        <p style={{ fontSize: 13, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.8, margin: 0 }}>
          {brandTokens.brandTagline}
        </p>
      </section>

      <section
        style={{
          background: brandTokens.colors.background,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: 48,
          position: "relative",
        }}
      >
        <div style={{ position: "absolute", top: 24, right: 24 }}>
          <LanguageToggle />
        </div>
        <form
          onSubmit={handleSubmit}
          style={{
            background: brandTokens.colors.surface,
            padding: 40,
            borderRadius: brandTokens.radius.lg,
            width: "100%",
            maxWidth: 400,
            boxShadow: brandTokens.shadow.card,
            border: `1px solid ${brandTokens.colors.border}`,
          }}
        >
          <h2 style={{ fontSize: 24, marginBottom: 6 }}>{t("login.welcome")}</h2>
          <p style={{ color: brandTokens.colors.textSecondary, margin: "0 0 28px", fontSize: 14 }}>
            {t("login.subtitle")}
          </p>

          <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6 }}>{t("login.user")}</label>
          <input
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            placeholder={t("login.userPlaceholder")}
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            style={{ marginBottom: 18 }}
          />

          <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6 }}>{t("login.password")}</label>
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ marginBottom: 22 }}
          />

          {error && (
            <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13, margin: "0 0 14px" }}>
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary" disabled={submitting} style={{ width: "100%" }}>
            {t("login.submit")}
          </button>
        </form>
      </section>
    </div>
  );
}
