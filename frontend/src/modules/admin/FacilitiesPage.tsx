import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Facility = { id: string; name: string; city: string; country: string; is_active: boolean };

export function FacilitiesPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<Facility>("/identity/facilities");

  return (
    <section>
      <PageHeader title={t("admin.facilities.title")} subtitle={t("admin.facilities.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.facilities.empty")}
          columns={[
            { key: "name", header: t("admin.facilities.name"), render: (r) => r.name },
            { key: "city", header: t("admin.facilities.city"), render: (r) => r.city },
            { key: "country", header: t("admin.facilities.country"), render: (r) => r.country },
            { key: "active", header: t("admin.facilities.status"), render: (r) => (r.is_active ? t("app.active") : t("app.inactive")) },
          ]}
        />
      )}
    </section>
  );
}
