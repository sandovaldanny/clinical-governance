import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiFetchJson } from "../api/client";
import { useAuth } from "../auth/AuthContext";

/** GET de un único objeto (detalle, resumen). `path` vacío → no consulta. */
export function useApiGet<T>(path: string) {
  const { t } = useTranslation();
  const { session } = useAuth();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(Boolean(path));
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    apiFetchJson<T>(path, { signal: controller.signal }, session?.token)
      .then((row) => { if (!controller.signal.aborted) setData(row); })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        setError(err instanceof ApiError ? t("app.errorLoadStatus", { status: err.status }) : t("app.errorLoad"));
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, session?.token, reloadKey]);

  return { data, loading, error, reload: () => setReloadKey((k) => k + 1) };
}
