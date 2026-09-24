import { MasterDataPage } from "../../components/MasterDataPage";

type Catalog = { id: string; catalog_type: string; code: string; label: string; is_active: boolean };

export function SpecialtiesPage() {
  return (
    <MasterDataPage<Catalog>
      titleKey="admin.specialties.title"
      subtitleKey="admin.specialties.subtitle"
      emptyKey="admin.specialties.empty"
      newKey="admin.specialties.new"
      editKey="admin.specialties.edit"
      listPath="/identity/catalogs?catalog_type=specialty"
      writePath="/identity/catalogs"
      managePermission="catalogs.manage"
      fields={[
        { key: "catalog_type", labelKey: "", type: "text", fixed: "specialty" },
        { key: "code", labelKey: "admin.specialties.code", type: "text", required: true, createOnly: true, hintKey: "admin.specialties.codeHint" },
        { key: "label", labelKey: "admin.specialties.name", type: "text", required: true },
      ]}
      columns={[
        { key: "code", headerKey: "admin.specialties.code", render: (r) => <code>{r.code}</code> },
        { key: "label", headerKey: "admin.specialties.name", render: (r) => r.label },
      ]}
      status={{ kind: "toggle", field: "is_active" }}
      rowLabel={(r) => r.label}
    />
  );
}
