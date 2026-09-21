import { Link } from "react-router-dom";

import { brandTokens } from "../../theme/brand-tokens";
import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type AuditCycle = {
  id: string;
  facility_id: string;
  period_label: string;
  status: string;
};

export function UccaDashboard() {
  const { data, loading, error } = useApiList<AuditCycle>("/ucca/cycles");

  return (
    <section>
      <PageHeader
        title="UCCA — Ciclos de auditoría"
        subtitle="M04 — Universal Clinical Competency Audit (ciclos por centro y periodo)"
      />
      {loading && <p>Cargando ciclos…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay ciclos de auditoría registrados todavía."
          columns={[
            { key: "period", header: "Periodo", render: (r) => r.period_label },
            { key: "status", header: "Estado", render: (r) => r.status },
            { key: "facility", header: "Centro (ID)", render: (r) => r.facility_id.slice(0, 8) + "…" },
            {
              key: "actions",
              header: "Acciones",
              render: (r) => (
                <Link
                  to={`/ucca/cycles/${r.id}/evaluate`}
                  style={{ color: brandTokens.colors.primary, fontWeight: 600 }}
                >
                  Evaluar criterios
                </Link>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}
