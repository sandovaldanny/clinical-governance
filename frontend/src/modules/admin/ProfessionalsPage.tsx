import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Professional = {
  id: string;
  employee_number: string;
  full_name: string;
  specialty: string | null;
  profession_name: string;
  is_active: boolean;
};

export function ProfessionalsPage() {
  const { t } = useTranslation();
  const { data, loading, error } = useApiList<Professional>("/identity/professionals");

  return (
    <section>
      <PageHeader title={t("admin.professionals.title")} subtitle={t("admin.professionals.subtitle")} />
      {loading && <p>{t("app.loading")}</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage={t("admin.professionals.empty")}
          columns={[
            { key: "name", header: t("admin.professionals.name"), render: (r) => r.full_name },
            { key: "emp", header: t("admin.professionals.employee"), render: (r) => r.employee_number },
            { key: "prof", header: t("admin.professionals.profession"), render: (r) => r.profession_name },
            { key: "spec", header: t("admin.professionals.specialty"), render: (r) => r.specialty ?? t("app.none") },
            { key: "active", header: t("admin.professionals.status"), render: (r) => (r.is_active ? t("app.active") : t("app.inactive")) },
          ]}
        />
      )}
    </section>
  );
}
