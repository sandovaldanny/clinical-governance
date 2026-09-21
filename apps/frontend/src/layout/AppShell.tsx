import { Outlet } from "react-router-dom";

import { AUTH_DISABLED } from "../api/client";
import { brandTokens } from "../theme/brand-tokens";
import { useAuth } from "../auth/AuthContext";
import { Sidebar } from "./Sidebar";

export function AppShell() {
  const { logout } = useAuth();

  return (
    <div style={{ fontFamily: brandTokens.fontFamily, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {AUTH_DISABLED && (
        <div
          style={{
            background: brandTokens.colors.warning,
            color: "#fff",
            padding: "6px 24px",
            fontSize: 13,
            textAlign: "center",
          }}
        >
          Modo local sin autenticación — no usar en producción
        </div>
      )}
      <header
        style={{
          background: brandTokens.colors.primary,
          color: brandTokens.colors.primaryContrast,
          padding: "12px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <strong>{brandTokens.productName}</strong>
          <span style={{ marginLeft: 12, fontSize: 13, opacity: 0.85 }}>
            {brandTokens.productTagline}
          </span>
        </div>
        {!AUTH_DISABLED && (
          <button onClick={logout} style={{ background: "transparent", color: "white", border: "none", cursor: "pointer" }}>
            Cerrar sesión
          </button>
        )}
      </header>
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <Sidebar />
        <main style={{ flex: 1, padding: 24, background: brandTokens.colors.background, overflowY: "auto" }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
