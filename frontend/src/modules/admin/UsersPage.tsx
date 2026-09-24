import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusToggle } from "../../components/StatusToggle";
import { useApiList } from "../../hooks/useApiList";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import { brandTokens } from "../../theme/brand-tokens";

type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  profession_name: string | null;
  specialty: string | null;
};

export function UsersPage() {
  const { t } = useTranslation();
  const { session } = useAuth();
  const me = useCurrentUser();
  const { data, loading, error, reload } = useApiList<User>("/identity/users");
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const canManage = me?.permissions.includes("users.manage") ?? false;

  async function toggleStatus(user: User, next: boolean) {
    setPendingId(user.id);
    setActionError(null);
    try {
      await apiPatchJson<User>(`/identity/users/${user.id}/status`, { is_active: next }, session?.token);
      reload();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t("admin.users.statusError"));
    } finally {
      setPendingId(null);
    }
  }

  return (
    <section>
      <PageHeader title={t("admin.users.title")} subtitle={t("admin.users.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {actionError && (
        <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13, marginBottom: 12 }}>
          {actionError}
        </p>
      )}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.users.empty")}
          columns={[
            {
              key: "name",
              header: t("admin.users.name"),
              render: (r) => (
                <span style={{ color: r.is_active ? undefined : brandTokens.colors.textSecondary }}>{r.full_name}</span>
              ),
            },
            { key: "email", header: t("admin.users.email"), render: (r) => r.email },
            { key: "prof", header: t("admin.users.profession"), render: (r) => r.profession_name ?? t("app.none") },
            { key: "spec", header: t("admin.users.specialty"), render: (r) => r.specialty ?? t("app.none") },
            {
              key: "active",
              header: t("admin.users.status"),
              render: (r) => (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
                  {canManage && (
                    <StatusToggle
                      checked={r.is_active}
                      disabled={pendingId === r.id || r.id === me?.id}
                      label={r.is_active ? t("admin.users.deactivate") : t("admin.users.activate")}
                      onChange={(next) => toggleStatus(r, next)}
                    />
                  )}
                  <span style={{ fontSize: 13, color: r.is_active ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary }}>
                    {r.is_active ? t("app.active") : t("app.inactive")}
                  </span>
                </span>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}
