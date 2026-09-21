import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";

type Facility = { id: string; name: string; city: string; country: string; is_active: boolean };

export function FacilitiesPage() {
  const { data, loading, error } = useApiList<Facility>("/identity/facilities");

  return (
    <section>
      <PageHeader
        title="Centros médicos"
        subtitle="M02 — Facilities / centros de Alkalma (Al Bateen, Al Falah, …)"
      />
      {loading && <p>Cargando…</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <DataTable
          rows={data}
          emptyMessage="No hay centros registrados."
          columns={[
            { key: "name", header: "Centro", render: (r) => r.name },
            { key: "city", header: "Ciudad", render: (r) => r.city },
            { key: "country", header: "País", render: (r) => r.country },
            { key: "active", header: "Estado", render: (r) => (r.is_active ? "Activo" : "Inactivo") },
          ]}
        />
      )}
    </section>
  );
}
