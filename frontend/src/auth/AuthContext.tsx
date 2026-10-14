import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { UNAUTHORIZED_EVENT } from "../api/client";

type Session = { token: string; mustChangePassword: boolean } | null;

type AuthContextValue = {
  session: Session;
  setSession: (session: Session) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// La sesión vive en sessionStorage: sobrevive a recargar la página, muere al cerrar la pestaña.
const STORAGE_KEY = "aegis.session";

function readStoredSession(): Session {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { token?: unknown; mustChangePassword?: unknown };
    if (typeof parsed.token !== "string") return null;
    return { token: parsed.token, mustChangePassword: Boolean(parsed.mustChangePassword) };
  } catch {
    return null;
  }
}

function writeStoredSession(session: Session): void {
  try {
    if (session) window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    else window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* almacenamiento no disponible (modo privado, etc.): la sesión queda solo en memoria */
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<Session>(readStoredSession);

  // Token rechazado por el backend (expirado, secreto rotado): se descarta y se vuelve al login.
  useEffect(() => {
    const onUnauthorized = () => {
      writeStoredSession(null);
      setSessionState(null);
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    const setSession = (next: Session) => {
      writeStoredSession(next);
      setSessionState(next);
    };
    return { session, setSession, logout: () => setSession(null) };
  }, [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
