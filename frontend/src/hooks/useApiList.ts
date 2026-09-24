import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiFetchJson } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function useApiList<T>(path: string) {
  const { t } = useTranslation();
  const { session } = useAuth();
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!path || (path.includes("cycle_id=") && path.endsWith("cycle_id="))) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    apiFetchJson<T[]>(path, { signal: controller.signal }, session?.token)
      .then((rows) => {
        if (!controller.signal.aborted) {
          setData(rows);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        if (err instanceof ApiError) {
          setError(t("app.errorLoadStatus", { status: err.status }));
        } else {
          setError(t("app.errorLoad"));
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
    // t cambia de identidad al cambiar idioma; no queremos refetch por eso.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, session?.token, reloadKey]);

  return { data, loading, error, reload: () => setReloadKey((k) => k + 1) };
}
