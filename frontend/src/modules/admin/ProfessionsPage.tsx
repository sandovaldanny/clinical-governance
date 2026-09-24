import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Profession = { id: string; name: string; is_active: boolean };

export function ProfessionsPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<Profession>("/identity/professions");

  return (
    <section>
      <PageHeader title={t("admin.professions.title")} subtitle={t("admin.professions.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.professions.empty")}
          columns={[
            { key: "name", header: t("admin.professions.name"), render: (r) => r.name },
            { key: "active", header: t("admin.professions.status"), render: (r) => (r.is_active ? t("app.activeF") : t("app.inactiveF")) },
          ]}
        />
      )}
    </section>
  );
}
