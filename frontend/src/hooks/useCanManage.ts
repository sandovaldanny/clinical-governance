import { useCurrentUser } from "./useCurrentUser";

/** true si el usuario actual tiene el permiso `code` (ej. "users.manage"). false mientras carga. */
export function useCanManage(code: string): boolean {
  const me = useCurrentUser();
  return me?.permissions.includes(code) ?? false;
}
