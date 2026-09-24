import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { AUTH_DISABLED } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { brandTokens } from "../theme/brand-tokens";

function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

/** Avatar + menú desplegable con identidad del usuario (nombre, correo, roles) y cierre de sesión. */
export function ProfileMenu() {
  const { t } = useTranslation();
  const { logout } = useAuth();
  const user = useCurrentUser();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) setOpen(false);
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const displayName = user?.full_name ?? t("profile.devUser");
  const primaryRole = user?.roles[0];

  return (
    <div ref={rootRef} style={{ position: "relative" }}>
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t("profile.menu")}
        onClick={() => setOpen((v) => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          background: "transparent",
          border: "none",
          padding: "4px 6px",
          borderRadius: 999,
        }}
      >
        <span
          aria-hidden
          style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: brandTokens.gradient,
            color: brandTokens.colors.primaryContrast,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 13,
            fontWeight: 600,
            letterSpacing: "0.02em",
          }}
        >
          {initialsOf(displayName) || "·"}
        </span>
        <span style={{ textAlign: "left", lineHeight: 1.2 }} className="profile-name">
          <span style={{ display: "block", fontSize: 14, fontWeight: 500, color: brandTokens.colors.textPrimary }}>
            {displayName}
          </span>
          {primaryRole && (
            <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>
              {primaryRole}
            </span>
          )}
        </span>
      </button>

      {open && (
        <div
          role="menu"
          style={{
            position: "absolute",
            right: 0,
            top: "calc(100% + 10px)",
            minWidth: 280,
            background: brandTokens.colors.surface,
            border: `1px solid ${brandTokens.colors.border}`,
            borderRadius: brandTokens.radius.lg,
            boxShadow: brandTokens.shadow.hover,
            padding: 20,
            zIndex: 30,
          }}
        >
          <p style={{ margin: 0, fontWeight: 500, fontSize: 15 }}>{displayName}</p>
          {user?.email && (
            <p style={{ margin: "2px 0 0", fontSize: 13, color: brandTokens.colors.textSecondary }}>{user.email}</p>
          )}

          <p
            style={{
              margin: "16px 0 6px",
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: brandTokens.colors.textSecondary,
            }}
          >
            {t("profile.roles")}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {user && user.roles.length > 0 ? (
              user.roles.map((role) => (
                <span key={role} className="chip">
                  {role}
                </span>
              ))
            ) : (
              <span style={{ fontSize: 13, color: brandTokens.colors.textSecondary }}>{t("app.none")}</span>
            )}
          </div>

          {!AUTH_DISABLED && (
            <button
              type="button"
              role="menuitem"
              onClick={logout}
              className="btn-ghost"
              style={{ width: "100%", marginTop: 18 }}
            >
              {t("profile.logout")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
