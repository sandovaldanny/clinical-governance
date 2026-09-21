import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type Session = { token: string; mustChangePassword: boolean } | null;

type AuthContextValue = {
  session: Session;
  setSession: (session: Session) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session>(null);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      setSession,
      logout: () => setSession(null),
    }),
    [session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
