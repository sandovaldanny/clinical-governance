import { brandTokens } from "../../theme/brand-tokens";
import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Criterion = {
  id: string;
  code: string;
  description: string;
  severity: string;
};

type Catalog = { id: string; code: string; label: string; catalog_type: string };

function severityColor(severity: string): string {
  if (severity === "critical") return brandTokens.colors.danger;
  if (severity === "major") return brandTokens.colors.warning;
  return brandTokens.colors.textSecondary;
}

export function IndicatorsPage() {
  const ucca = useApiList<Criterion>("/ucca/criteria");
  const omh001 = useApiList<Catalog>("/identity/catalogs?catalog_type=omh001_investigation");
  const medication = useApiList<Catalog>("/identity/catalogs?catalog_type=medication_class");

  const loading = ucca.loading || omh001.loading || medication.loading;

  return (
    <section>
      <PageHeader
        title="Indicadores a evaluar"
        subtitle="M04 UCCA + M05 JAWDA/OMH001 — criterios versionados de la plantilla vigente y catálogos regulatorios"
      />

      <h2 style={{ fontSize: 17, marginTop: 28 }}>UCCA — Criterios de auditoría (plantilla vigente)</h2>
      {ucca.loading && <p>Cargando criterios UCCA…</p>}
      {ucca.error && <p>{ucca.error}</p>}
      {!ucca.loading && !ucca.error && (
        <DataTable
          rows={ucca.data}
          emptyMessage="No hay criterios UCCA configurados."
          columns={[
            { key: "code", header: "Código", render: (r) => r.code },
            { key: "desc", header: "Indicador / criterio", render: (r) => r.description },
            {
              key: "sev",
              header: "Severidad",
              render: (r) => (
                <span style={{ color: severityColor(r.severity), fontWeight: 600 }}>{r.severity}</span>
              ),
            },
          ]}
        />
      )}

      <h2 style={{ fontSize: 17, marginTop: 32 }}>OMH001 — Investigaciones requeridas (antipsicóticos)</h2>
      {omh001.loading && <p>Cargando…</p>}
      {!omh001.loading && !omh001.error && (
        <DataTable
          rows={omh001.data}
          emptyMessage="No hay investigaciones OMH001 configuradas."
          columns={[
            { key: "code", header: "Código", render: (r) => r.code },
            { key: "label", header: "Investigación", render: (r) => r.label },
          ]}
        />
      )}

      <h2 style={{ fontSize: 17, marginTop: 32 }}>Clasificación de medicación psicotrópica (M05)</h2>
      {medication.loading && <p>Cargando…</p>}
      {!medication.loading && !medication.error && (
        <DataTable
          rows={medication.data}
          emptyMessage="No hay clases de medicación configuradas."
          columns={[
            { key: "code", header: "Código", render: (r) => r.code },
            { key: "label", header: "Clase / ruta", render: (r) => r.label },
          ]}
        />
      )}

      {loading && <p style={{ marginTop: 16, color: brandTokens.colors.textSecondary }}>Actualizando…</p>}
    </section>
  );
}
