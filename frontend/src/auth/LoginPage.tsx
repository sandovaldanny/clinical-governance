import { useState } from "react";

import { login } from "../api/client";
import { brandTokens } from "../theme/brand-tokens";
import { useAuth } from "./AuthContext";

/**
 * Pantalla de acceso con branding Alkalma (sección 6.1 del funcional): sin acceso anónimo,
 * y el sistema deberá exigir cambio de contraseña en el primer acceso (must_change_password).
 */
export function LoginPage() {
  const { setSession } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const result = await login(email, password);
      setSession({ token: result.access_token, mustChangePassword: result.must_change_password });
    } catch {
      setError("No fue posible iniciar sesión. Verifique sus credenciales.");
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: brandTokens.colors.background,
        fontFamily: brandTokens.fontFamily,
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: brandTokens.colors.surface,
          padding: 32,
          borderRadius: 8,
          width: 360,
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ color: brandTokens.colors.primary, fontSize: 22, marginBottom: 4 }}>
          {brandTokens.productName}
        </h1>
        <p style={{ color: brandTokens.colors.textSecondary, marginBottom: 24, fontSize: 13 }}>
          {brandTokens.productTagline}
        </p>

        <label style={{ display: "block", fontSize: 13, marginBottom: 4 }}>Correo corporativo</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: "100%", padding: 8, marginBottom: 16 }}
        />

        <label style={{ display: "block", fontSize: 13, marginBottom: 4 }}>Contraseña</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: "100%", padding: 8, marginBottom: 16 }}
        />

        {error && (
          <p style={{ color: brandTokens.colors.danger, fontSize: 13, marginBottom: 12 }}>{error}</p>
        )}

        <button
          type="submit"
          style={{
            width: "100%",
            padding: 10,
            background: brandTokens.colors.primary,
            color: brandTokens.colors.primaryContrast,
            border: "none",
            borderRadius: 6,
            fontWeight: 600,
          }}
        >
          Ingresar
        </button>
      </form>
    </div>
  );
}
