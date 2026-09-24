import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Role = { id: string; code: string; name: string; is_system_defined: boolean };

export function RolesPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<Role>("/identity/roles");

  return (
    <section>
      <PageHeader title={t("admin.roles.title")} subtitle={t("admin.roles.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.roles.empty")}
          columns={[
            { key: "name", header: t("admin.roles.role"), render: (r) => r.name },
            { key: "code", header: t("admin.roles.code"), render: (r) => <code>{r.code}</code> },
            { key: "system", header: t("admin.roles.system"), render: (r) => (r.is_system_defined ? t("app.yes") : t("app.no")) },
          ]}
        />
      )}
    </section>
  );
}
