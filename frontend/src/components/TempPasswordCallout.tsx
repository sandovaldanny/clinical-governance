import { useState } from "react";
import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../theme/brand-tokens";

/** Contraseña temporal generada por el sistema: se muestra una sola vez tras crear el usuario. */
export function TempPasswordCallout({ email, password, onDismiss }: { email: string; password: string; onDismiss: () => void }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(password);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div
      role="status"
      style={{
        background: alkalma.turquoiseTint,
        border: `1px solid ${alkalma.turquoiseLight}`,
        borderRadius: brandTokens.radius.lg,
        padding: "18px 22px",
        marginBottom: 20,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        flexWrap: "wrap",
      }}
    >
      <div>
        <p style={{ margin: 0, fontWeight: 500 }}>{t("admin.users.tempPasswordTitle", { email })}</p>
        <p style={{ margin: "4px 0 0", fontSize: 13, color: brandTokens.colors.textSecondary }}>
          {t("admin.users.tempPasswordHint")}
        </p>
        <code
          style={{
            display: "inline-block",
            marginTop: 10,
            padding: "6px 12px",
            background: brandTokens.colors.surface,
            borderRadius: brandTokens.radius.sm,
            fontSize: 15,
            letterSpacing: "0.06em",
          }}
        >
          {password}
        </code>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <button type="button" className="btn-ghost" onClick={copy}>
          {copied ? t("app.copied") : t("app.copy")}
        </button>
        <button type="button" className="btn-ghost" onClick={onDismiss}>
          {t("app.close")}
        </button>
      </div>
    </div>
  );
}
