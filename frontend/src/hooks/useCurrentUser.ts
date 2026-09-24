import { useEffect, useState } from "react";

import { apiFetchJson } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
  facilities: string[];
  is_corporate: boolean;
  permissions: string[];
};

/** Perfil del usuario autenticado (GET /identity/me). null mientras carga o si falla. */
export function useCurrentUser(): CurrentUser | null {
  const { session } = useAuth();
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiFetchJson<CurrentUser>("/identity/me", {}, session?.token)
      .then((profile) => {
        if (!cancelled) setUser(profile);
      })
      .catch(() => {
        if (!cancelled) setUser(null);
      });
    return () => {
      cancelled = true;
    };
  }, [session?.token]);

  return user;
}
