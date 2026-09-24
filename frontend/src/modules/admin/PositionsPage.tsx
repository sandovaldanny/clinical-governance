import { MasterDataPage } from "../../components/MasterDataPage";

type Position = { id: string; title: string; description: string; is_active: boolean };

export function PositionsPage() {
  return (
    <MasterDataPage<Position>
      titleKey="admin.positions.title"
      subtitleKey="admin.positions.subtitle"
      emptyKey="admin.positions.empty"
      newKey="admin.positions.new"
      editKey="admin.positions.edit"
      listPath="/identity/positions"
      writePath="/identity/positions"
      managePermission="catalogs.manage"
      fields={[
        { key: "title", labelKey: "admin.positions.name", type: "text", required: true },
        { key: "description", labelKey: "admin.positions.description", type: "textarea" },
      ]}
      columns={[
        { key: "title", headerKey: "admin.positions.name", render: (r) => <strong style={{ fontWeight: 500 }}>{r.title}</strong> },
        { key: "description", headerKey: "admin.positions.description", render: (r) => r.description || "—" },
      ]}
      status={{ kind: "toggle", field: "is_active" }}
      rowLabel={(r) => r.title}
    />
  );
}
