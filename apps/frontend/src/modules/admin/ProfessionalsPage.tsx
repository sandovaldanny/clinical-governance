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
  const { data, loading, error } = useApiList<Professional>("/identity/professionals");

  return (
    <section>
      <PageHeader
        title="Profesionales"
        subtitle="M02 — Registro único de profesionales clínicos vinculados a centros y profesiones"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay profesionales registrados."
          columns={[
            { key: "name", header: "Nombre", render: (r) => r.full_name },
            { key: "emp", header: "N.º empleado", render: (r) => r.employee_number },
            { key: "prof", header: "Profesión", render: (r) => r.profession_name },
            { key: "spec", header: "Especialidad", render: (r) => r.specialty ?? "—" },
            { key: "active", header: "Estado", render: (r) => (r.is_active ? "Activo" : "Inactivo") },
          ]}
        />
      )}
    </section>
  );
}
