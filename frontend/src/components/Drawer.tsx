import { useEffect, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../theme/brand-tokens";

type DrawerProps = {
  open: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  width?: number;
};

/** Panel lateral derecho sobre la tabla. Cierra con Esc o click en el overlay. */
export function Drawer({ open, title, subtitle, onClose, children, footer, width = 480 }: DrawerProps) {
  const { t } = useTranslation();

  useEffect(() => {
    if (!open) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(22, 69, 92, 0.28)",
        zIndex: 40,
        display: "flex",
        justifyContent: "flex-end",
      }}
    >
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={title}
        style={{
          width,
          maxWidth: "100vw",
          height: "100%",
          background: brandTokens.colors.surface,
          boxShadow: "-8px 0 32px rgba(22, 69, 92, 0.16)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <header
          style={{
            padding: "24px 28px 18px",
            borderBottom: `1px solid ${brandTokens.colors.border}`,
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <div>
            <h2 style={{ fontSize: 20 }}>{title}</h2>
            {subtitle && (
              <p style={{ margin: "4px 0 0", fontSize: 13, color: brandTokens.colors.textSecondary }}>{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("app.close")}
            style={{
              border: "none",
              background: "transparent",
              fontSize: 22,
              lineHeight: 1,
              color: brandTokens.colors.textSecondary,
              padding: 4,
            }}
          >
            ×
          </button>
        </header>
        <div style={{ flex: 1, overflowY: "auto", padding: "22px 28px" }}>{children}</div>
        {footer && (
          <footer
            style={{
              padding: "16px 28px",
              borderTop: `1px solid ${brandTokens.colors.border}`,
              display: "flex",
              justifyContent: "flex-end",
              gap: 10,
              background: brandTokens.colors.background,
            }}
          >
            {footer}
          </footer>
        )}
      </aside>
    </div>
  );
}
