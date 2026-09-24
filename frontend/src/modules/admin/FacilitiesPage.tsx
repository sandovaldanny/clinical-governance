import { MasterDataPage } from "../../components/MasterDataPage";

type Facility = {
  id: string;
  name: string;
  city: string;
  country: string;
  status: "active" | "closed";
  is_active: boolean;
  clinical_director_user_id: string | null;
  clinical_director_name: string | null;
};

export function FacilitiesPage() {
  return (
    <MasterDataPage<Facility>
      titleKey="admin.facilities.title"
      subtitleKey="admin.facilities.subtitle"
      emptyKey="admin.facilities.empty"
      newKey="admin.facilities.new"
      editKey="admin.facilities.edit"
      listPath="/identity/facilities"
      writePath="/identity/facilities"
      managePermission="facilities.manage"
      fields={[
        { key: "name", labelKey: "admin.facilities.name", type: "text", required: true },
        {
          key: "country", labelKey: "admin.facilities.country", type: "select", required: true,
          optionsFrom: { path: "/identity/catalogs?catalog_type=country", value: "code", label: "label", onlyActive: true },
        },
        {
          key: "city", labelKey: "admin.facilities.city", type: "select", required: true,
          optionsFrom: { path: "/identity/catalogs?catalog_type=city", value: "label", label: "label", onlyActive: true },
        },
        {
          key: "clinical_director_user_id", labelKey: "admin.facilities.director", type: "select", hintKey: "admin.facilities.directorHint",
          optionsFrom: { path: "/identity/users", value: "id", label: "full_name", onlyActive: true },
        },
      ]}
      columns={[
        { key: "name", headerKey: "admin.facilities.name", render: (r) => <strong style={{ fontWeight: 500 }}>{r.name}</strong> },
        { key: "city", headerKey: "admin.facilities.city", render: (r) => r.city },
        { key: "country", headerKey: "admin.facilities.country", render: (r) => r.country },
        { key: "director", headerKey: "admin.facilities.director", render: (r) => r.clinical_director_name ?? "—" },
      ]}
      status={{ kind: "select", field: "status", values: ["active", "closed"] }}
      rowLabel={(r) => r.name}
    />
  );
}
