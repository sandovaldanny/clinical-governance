import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Catalog = { id: string; code: string; label: string; is_active: boolean };

export function SpecialtiesPage() {
  const { data, loading, error } = useApiList<Catalog>("/identity/catalogs?catalog_type=specialty");

  return (
    <section>
      <PageHeader
        title="Especialidades"
        subtitle="M02 — Catálogo de especialidades clínicas (configurables, activables/desactivables)"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay especialidades registradas."
          columns={[
            { key: "code", header: "Código", render: (r) => r.code },
            { key: "label", header: "Especialidad", render: (r) => r.label },
            { key: "active", header: "Estado", render: (r) => (r.is_active ? "Activa" : "Inactiva") },
          ]}
        />
      )}
    </section>
  );
}
