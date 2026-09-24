import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Catalog = { id: string; code: string; label: string; is_active: boolean };

export function SpecialtiesPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<Catalog>("/identity/catalogs?catalog_type=specialty");

  return (
    <section>
      <PageHeader title={t("admin.specialties.title")} subtitle={t("admin.specialties.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.specialties.empty")}
          columns={[
            { key: "code", header: t("admin.specialties.code"), render: (r) => <code>{r.code}</code> },
            { key: "label", header: t("admin.specialties.name"), render: (r) => r.label },
            { key: "active", header: t("admin.specialties.status"), render: (r) => (r.is_active ? t("app.activeF") : t("app.inactiveF")) },
          ]}
        />
      )}
    </section>
  );
}
