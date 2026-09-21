import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Role = { id: string; code: string; name: string; is_system_defined: boolean };

export function RolesPage() {
  const { data, loading, error } = useApiList<Role>("/identity/roles");

  return (
    <section>
      <PageHeader
        title="Roles AEGIS"
        subtitle="M01 — Roles funcionales (System Administrator, Medical Director, Auditor, …)"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay roles registrados."
          columns={[
            { key: "name", header: "Rol", render: (r) => r.name },
            { key: "code", header: "Código", render: (r) => r.code },
            {
              key: "system",
              header: "Sistema",
              render: (r) => (r.is_system_defined ? "Sí" : "No"),
            },
          ]}
        />
      )}
    </section>
  );
}
