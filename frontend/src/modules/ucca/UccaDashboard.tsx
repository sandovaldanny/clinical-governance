import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { useApiList } from "../../hooks/useApiList";
import { brandTokens } from "../../theme/brand-tokens";

type AuditCycle = { id: string; facility_id: string; period_label: string; status: string };
type Facility = { id: string; name: string };

export function UccaDashboard() {
  const { t } = useTranslation();
  const cycles = useApiList<AuditCycle>("/ucca/cycles");
  const facilities = useApiList<Facility>("/identity/facilities");

  const facilityName = (id: string) => facilities.data.find((f) => f.id === id)?.name ?? `${id.slice(0, 8)}…`;

  return (
    <section>
      <PageHeader title={t("ucca.title")} subtitle={t("ucca.subtitle")} />
      {cycles.loading && <p>{t("ucca.loadingCycles")}</p>}
      {cycles.error && <p>{cycles.error}</p>}
      {!cycles.loading && !cycles.error && (
        <DataTable
          rows={cycles.data}
          emptyMessage={t("ucca.empty")}
          columns={[
            { key: "period", header: t("ucca.period"), render: (r) => <strong>{r.period_label}</strong> },
            { key: "facility", header: t("ucca.facility"), render: (r) => facilityName(r.facility_id) },
            { key: "status", header: t("ucca.status"), render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            {
              key: "actions",
              header: t("ucca.actions"),
              render: (r) => (
                <Link to={`/ucca/cycles/${r.id}/evaluate`} style={{ color: brandTokens.colors.link, fontWeight: 600, textDecoration: "none" }}>
                  {t("ucca.evaluate")} →
                </Link>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}
