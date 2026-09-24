export type LoginResponse = {
  access_token: string;
  token_type: string;
  must_change_password: boolean;
};

export const AUTH_DISABLED = import.meta.env.VITE_AUTH_DISABLED === "true";

const API_BASE = "/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/identity/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    throw new Error("Credenciales inválidas o cuenta no autorizada.");
  }
  return response.json();
}

export function apiFetch(path: string, init: RequestInit = {}, token?: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (!AUTH_DISABLED && token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...init, headers });
}

export async function apiFetchJson<T>(
  path: string,
  init: RequestInit = {},
  token?: string,
): Promise<T> {
  const response = await apiFetch(path, init, token);
  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}`, response.status);
  }
  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("Respuesta no válida del servidor", response.status);
  }
}

export function authorizedFetch(path: string, token: string, init: RequestInit = {}) {
  return apiFetch(path, init, token);
}

export async function apiPostJson<T>(path: string, body: unknown, token?: string): Promise<T> {
  const response = await apiFetch(
    path,
    { method: "POST", body: JSON.stringify(body) },
    token,
  );
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = (await response.json()) as { detail?: string };
      if (typeof err.detail === "string") detail = err.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

export async function apiPatchJson<T>(path: string, body: unknown, token?: string): Promise<T> {
  const response = await apiFetch(path, { method: "PATCH", body: JSON.stringify(body) }, token);
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = (await response.json()) as { detail?: string };
      if (typeof err.detail === "string") detail = err.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}
