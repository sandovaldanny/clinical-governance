import { FormEvent, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { DataTable } from "../../components/DataTable";
import { Drawer } from "../../components/Drawer";
import { FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { StatusToggle } from "../../components/StatusToggle";
import { Toolbar } from "../../components/Toolbar";
import { useApiList } from "../../hooks/useApiList";
import { useCanManage } from "../../hooks/useCanManage";
import { brandTokens } from "../../theme/brand-tokens";

type Role = {
  id: string;
  code: string;
  name: string;
  description: string;
  is_system_defined: boolean;
  is_active: boolean;
  permission_ids: string[];
  user_count: number;
};
type Permission = { id: string; code: string; module: string; name: string; description: string };
type PermissionGroup = { module: string; permissions: Permission[] };

type Form = { code: string; name: string; description: string; permission_ids: string[] };
const EMPTY: Form = { code: "", name: "", description: "", permission_ids: [] };

export function RolesPage() {
  const { t } = useTranslation();
  const { session } = useAuth();
  const canManage = useCanManage("roles.manage");
  const roles = useApiList<Role>("/identity/roles");
  const groups = useApiList<PermissionGroup>("/identity/permissions");
  const totalPermissions = useMemo(() => groups.data.reduce((n, g) => n + g.permissions.length, 0), [groups.data]);

  const [drawer, setDrawer] = useState<{ mode: "create" } | { mode: "edit"; role: Role } | null>(null);
  const [form, setForm] = useState<Form>(EMPTY);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const editingSysadmin = drawer?.mode === "edit" && drawer.role.code === "system_administrator";

  function openCreate() {
    setForm(EMPTY);
    setFormError(null);
    setDrawer({ mode: "create" });
  }
  function openEdit(role: Role) {
    setForm({ code: role.code, name: role.name, description: role.description, permission_ids: role.permission_ids });
    setFormError(null);
    setDrawer({ mode: "edit", role });
  }
  function closeDrawer() {
    if (!submitting) setDrawer(null);
  }
  function togglePermission(id: string) {
    setForm((f) => ({
      ...f,
      permission_ids: f.permission_ids.includes(id) ? f.permission_ids.filter((x) => x !== id) : [...f.permission_ids, id],
    }));
  }
  function toggleModule(group: PermissionGroup) {
    const ids = group.permissions.map((p) => p.id);
    const allOn = ids.every((id) => form.permission_ids.includes(id));
    setForm((f) => ({
      ...f,
      permission_ids: allOn ? f.permission_ids.filter((id) => !ids.includes(id)) : Array.from(new Set([...f.permission_ids, ...ids])),
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!drawer) return;
    setSubmitting(true);
    setFormError(null);
    setNotice(null);
    try {
      if (drawer.mode === "create") {
        await apiPostJson("/identity/roles", form, session?.token);
        setNotice(t("app.created"));
      } else {
        const body: Record<string, unknown> = { name: form.name, description: form.description };
        if (!editingSysadmin) body.permission_ids = form.permission_ids;
        await apiPatchJson(`/identity/roles/${drawer.role.id}`, body, session?.token);
        setNotice(t("app.updated"));
      }
      setDrawer(null);
      roles.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleActive(role: Role, next: boolean) {
    setPendingId(role.id);
    setActionError(null);
    try {
      await apiPatchJson(`/identity/roles/${role.id}`, { is_active: next }, session?.token);
      roles.reload();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setPendingId(null);
    }
  }

  return (
    <section>
      <PageHeader title={t("admin.roles.title")} subtitle={t("admin.roles.subtitle")} />
      {notice && <p role="status" style={{ color: brandTokens.colors.success, fontSize: 13 }}>{notice}</p>}
      {actionError && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{actionError}</p>}

      <Toolbar
        right={
          canManage && (
            <button type="button" className="btn-primary" onClick={openCreate}>
              + {t("admin.roles.new")}
            </button>
          )
        }
      />

      {roles.loading && <p>{t("app.loading")}</p>}
      {roles.error && <p>{roles.error}</p>}
      {!roles.loading && !roles.error && (
        <DataTable
          rows={roles.data}
          emptyMessage={t("admin.roles.empty")}
          columns={[
            {
              key: "name",
              header: t("admin.roles.role"),
              render: (r) => (
                <span style={{ color: r.is_active ? undefined : brandTokens.colors.textSecondary }}>
                  <span style={{ display: "block", fontWeight: 500 }}>{r.name}</span>
                  <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>
                    <code>{r.code}</code>
                    {r.is_system_defined ? ` · ${t("admin.roles.system")}` : ""}
                  </span>
                </span>
              ),
            },
            { key: "desc", header: t("admin.roles.description"), render: (r) => r.description || "—" },
            {
              key: "perms",
              header: t("admin.roles.colPermissions"),
              render: (r) => (
                <span style={{ fontSize: 13 }}>
                  {r.permission_ids.length} / {totalPermissions}
                  <span
                    aria-hidden
                    style={{
                      display: "block",
                      height: 4,
                      width: 96,
                      marginTop: 6,
                      borderRadius: 999,
                      background: brandTokens.colors.surfaceSoft,
                      overflow: "hidden",
                    }}
                  >
                    <span
                      style={{
                        display: "block",
                        height: "100%",
                        width: `${totalPermissions ? (100 * r.permission_ids.length) / totalPermissions : 0}%`,
                        background: brandTokens.colors.accent,
                      }}
                    />
                  </span>
                </span>
              ),
            },
            { key: "users", header: t("admin.roles.users"), render: (r) => t("admin.roles.usersCount", { count: r.user_count }) },
            {
              key: "status",
              header: t("app.statusLabel"),
              render: (r) => (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
                  {canManage && (
                    <StatusToggle
                      checked={r.is_active}
                      disabled={pendingId === r.id || r.code === "system_administrator"}
                      label={r.is_active ? t("app.deactivate") : t("app.activate")}
                      onChange={(next) => toggleActive(r, next)}
                    />
                  )}
                  <span style={{ fontSize: 13, color: r.is_active ? undefined : brandTokens.colors.textSecondary }}>
                    {r.is_active ? t("app.status.active") : t("app.status.inactive")}
                  </span>
                </span>
              ),
            },
            {
              key: "edit",
              header: "",
              render: (r) =>
                canManage ? (
                  <button type="button" className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => openEdit(r)}>
                    {t("app.edit")}
                  </button>
                ) : null,
            },
          ]}
        />
      )}

      <Drawer
        open={drawer !== null}
        title={drawer?.mode === "edit" ? t("admin.roles.edit") : t("admin.roles.new")}
        subtitle={drawer?.mode === "edit" ? drawer.role.name : undefined}
        onClose={closeDrawer}
        width={560}
        footer={
          <>
            <button type="button" className="btn-ghost" onClick={closeDrawer} disabled={submitting}>{t("app.cancel")}</button>
            <button type="submit" form="role-form" className="btn-primary" disabled={submitting}>
              {submitting ? t("app.saving") : t("app.save")}
            </button>
          </>
        }
      >
        <form id="role-form" onSubmit={handleSubmit}>
          {drawer?.mode === "create" && (
            <FormField label={t("admin.roles.code")} required hint={t("admin.roles.codeHint")}>
              <input value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))} required pattern="^[a-z][a-z0-9_]*$" />
            </FormField>
          )}
          <FormField label={t("admin.roles.role")} required>
            <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
          </FormField>
          <FormField label={t("admin.roles.description")}>
            <textarea rows={2} value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
          </FormField>

          <p style={{ fontSize: 13, fontWeight: 500, margin: "6px 0 4px" }}>{t("admin.roles.permissions")}</p>
          <p style={{ fontSize: 12, color: brandTokens.colors.textSecondary, margin: "0 0 12px" }}>
            {editingSysadmin ? t("admin.roles.sysadminLocked") : t("admin.roles.permissionsHint")}
          </p>

          <div style={{ display: "grid", gap: 10, opacity: editingSysadmin ? 0.6 : 1 }}>
            {groups.data.map((group) => {
              const ids = group.permissions.map((p) => p.id);
              const onCount = ids.filter((id) => form.permission_ids.includes(id)).length;
              return (
                <fieldset
                  key={group.module}
                  disabled={editingSysadmin}
                  style={{
                    border: `1px solid ${brandTokens.colors.border}`,
                    borderRadius: brandTokens.radius.md,
                    padding: "10px 14px 12px",
                    margin: 0,
                  }}
                >
                  <legend style={{ padding: "0 6px", fontSize: 12, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", color: brandTokens.colors.textSecondary }}>
                    <label style={{ display: "inline-flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={onCount === ids.length}
                        ref={(el) => {
                          if (el) el.indeterminate = onCount > 0 && onCount < ids.length;
                        }}
                        onChange={() => toggleModule(group)}
                        style={{ width: "auto", margin: 0, accentColor: brandTokens.colors.primary }}
                      />
                      {group.module} · {onCount}/{ids.length}
                    </label>
                  </legend>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                    {group.permissions.map((p) => (
                      <label key={p.id} style={{ display: "flex", gap: 8, alignItems: "flex-start", fontSize: 13, cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={form.permission_ids.includes(p.id)}
                          onChange={() => togglePermission(p.id)}
                          style={{ width: "auto", margin: "3px 0 0", accentColor: brandTokens.colors.primary }}
                        />
                        <span>
                          <code style={{ fontSize: 12 }}>{p.code}</code>
                          {p.description && (
                            <span style={{ display: "block", fontSize: 11, color: brandTokens.colors.textSecondary }}>{p.description}</span>
                          )}
                        </span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              );
            })}
          </div>

          {formError && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13, marginTop: 14 }}>{formError}</p>}
        </form>
      </Drawer>
    </section>
  );
}
