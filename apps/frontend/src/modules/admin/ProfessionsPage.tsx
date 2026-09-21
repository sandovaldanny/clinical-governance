import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Profession = { id: string; name: string; is_active: boolean };

export function ProfessionsPage() {
  const { data, loading, error } = useApiList<Profession>("/identity/professions");

  return (
    <section>
      <PageHeader
        title="Profesiones"
        subtitle="M02 — Profesiones clínicas para criterios UCCA/JAWDA y alcance de práctica"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay profesiones registradas."
          columns={[
            { key: "name", header: "Profesión", render: (r) => r.name },
            { key: "active", header: "Estado", render: (r) => (r.is_active ? "Activa" : "Inactiva") },
          ]}
        />
      )}
    </section>
  );
}
