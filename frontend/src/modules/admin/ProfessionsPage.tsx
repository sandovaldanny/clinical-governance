import { MasterDataPage } from "../../components/MasterDataPage";

type Profession = { id: string; name: string; is_active: boolean };

export function ProfessionsPage() {
  return (
    <MasterDataPage<Profession>
      titleKey="admin.professions.title"
      subtitleKey="admin.professions.subtitle"
      emptyKey="admin.professions.empty"
      newKey="admin.professions.new"
      editKey="admin.professions.edit"
      listPath="/identity/professions"
      writePath="/identity/professions"
      managePermission="catalogs.manage"
      fields={[{ key: "name", labelKey: "admin.professions.name", type: "text", required: true }]}
      columns={[{ key: "name", headerKey: "admin.professions.name", render: (r) => <strong style={{ fontWeight: 500 }}>{r.name}</strong> }]}
      status={{ kind: "toggle", field: "is_active" }}
      rowLabel={(r) => r.name}
    />
  );
}
