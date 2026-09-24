import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type User = { id: string; email: string; full_name: string; is_active: boolean };

export function UsersPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<User>("/identity/users");

  return (
    <section>
      <PageHeader title={t("admin.users.title")} subtitle={t("admin.users.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.users.empty")}
          columns={[
            { key: "name", header: t("admin.users.name"), render: (r) => r.full_name },
            { key: "email", header: t("admin.users.email"), render: (r) => r.email },
            { key: "active", header: t("admin.users.status"), render: (r) => (r.is_active ? t("app.active") : t("app.inactive")) },
          ]}
        />
      )}
    </section>
  );
}
