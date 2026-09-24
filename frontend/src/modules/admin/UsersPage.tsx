import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type User = { id: string; email: string; full_name: string; is_active: boolean };

export function UsersPage() {
  const { data, loading, error } = useApiList<User>("/identity/users");

  return (
    <section>
      <PageHeader
        title="Usuarios"
        subtitle="M01 — Gestión de usuarios, organización y accesos (requerimiento funcional §7)"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay usuarios registrados."
          columns={[
            { key: "name", header: "Nombre", render: (r) => r.full_name },
            { key: "email", header: "Correo", render: (r) => r.email },
            { key: "active", header: "Estado", render: (r) => (r.is_active ? "Activo" : "Inactivo") },
          ]}
        />
      )}
    </section>
  );
}
