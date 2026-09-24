import { FormEvent, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { DataTable } from "../../components/DataTable";
import { Drawer } from "../../components/Drawer";
import { CheckboxGroup, FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { StatusSelect, type UserStatus } from "../../components/StatusSelect";
import { TempPasswordCallout } from "../../components/TempPasswordCallout";
import { Toolbar } from "../../components/Toolbar";
import { useApiList } from "../../hooks/useApiList";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import { brandTokens } from "../../theme/brand-tokens";

type User = {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  employee_number: string | null;
  mobile: string | null;
  status: UserStatus;
  is_active: boolean;
  organizational_position_id: string | null;
  position_name: string | null;
  profession_id: string | null;
  profession_name: string | null;
  specialty: string | null;
  facility_ids: string[];
  is_corporate_scope: boolean;
  role_ids: string[];
};
type Named = { id: string; name: string; is_active: boolean };
type Position = { id: string; title: string; is_active: boolean };
type Role = { id: string; code: string; name: string; is_active: boolean };

type FormState = {
  first_name: string;
  last_name: string;
  employee_number: string;
  email: string;
  mobile: string;
  organizational_position_id: string;
  profession_id: string;
  facility_ids: string[];
  is_corporate_scope: boolean;
  role_ids: string[];
};

const EMPTY_FORM: FormState = {
  first_name: "",
  last_name: "",
  employee_number: "",
  email: "",
  mobile: "",
  organizational_position_id: "",
  profession_id: "",
  facility_ids: [],
  is_corporate_scope: false,
  role_ids: [],
};

function formFromUser(u: User): FormState {
  return {
    first_name: u.first_name ?? "",
    last_name: u.last_name ?? "",
    employee_number: u.employee_number ?? "",
    email: u.email,
    mobile: u.mobile ?? "",
    organizational_position_id: u.organizational_position_id ?? "",
    profession_id: u.profession_id ?? "",
    facility_ids: u.facility_ids,
    is_corporate_scope: u.is_corporate_scope,
    role_ids: u.role_ids,
  };
}

function toPayload(f: FormState) {
  return {
    first_name: f.first_name.trim(),
    last_name: f.last_name.trim(),
    employee_number: f.employee_number.trim(),
    email: f.email.trim(),
    mobile: f.mobile.trim() || null,
    organizational_position_id: f.organizational_position_id || null,
    profession_id: f.profession_id || null,
    facility_ids: f.facility_ids,
    is_corporate_scope: f.is_corporate_scope,
    role_ids: f.role_ids,
  };
}

const sectionTitle: React.CSSProperties = {
  fontSize: 11,
  fontWeight: 700,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: brandTokens.colors.textSecondary,
  margin: "6px 0 12px",
};

export function UsersPage() {
  const { t } = useTranslation();
  const { session } = useAuth();
  const me = useCurrentUser();
  const canManage = me?.permissions.includes("users.manage") ?? false;

  const users = useApiList<User>("/identity/users");
  const positions = useApiList<Position>("/identity/positions");
  const facilities = useApiList<Named>("/identity/facilities");
  const professions = useApiList<Named>("/identity/professions");
  const roles = useApiList<Role>("/identity/roles");

  const facilityName = useMemo(() => new Map(facilities.data.map((f) => [f.id, f.name])), [facilities.data]);
  const roleName = useMemo(() => new Map(roles.data.map((r) => [r.id, r.name])), [roles.data]);

  const [drawer, setDrawer] = useState<{ mode: "create" } | { mode: "edit"; user: User } | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<{ email: string; password: string } | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  function openCreate() {
    setForm(EMPTY_FORM);
    setFormError(null);
    setDrawer({ mode: "create" });
  }
  function openEdit(user: User) {
    setForm(formFromUser(user));
    setFormError(null);
    setDrawer({ mode: "edit", user });
  }
  function closeDrawer() {
    if (!submitting) setDrawer(null);
  }
  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => setForm((f) => ({ ...f, [key]: value }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!drawer) return;
    setSubmitting(true);
    setFormError(null);
    setNotice(null);
    try {
      if (drawer.mode === "create") {
        const result = await apiPostJson<{ user: User; temporary_password: string }>(
          "/identity/users",
          toPayload(form),
          session?.token,
        );
        setCreated({ email: result.user.email, password: result.temporary_password });
      } else {
        await apiPatchJson<User>(`/identity/users/${drawer.user.id}`, toPayload(form), session?.token);
        setNotice(t("admin.users.updated"));
      }
      setDrawer(null);
      users.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setSubmitting(false);
    }
  }

  async function changeStatus(user: User, next: UserStatus) {
    setPendingId(user.id);
    setActionError(null);
    try {
      await apiPatchJson<User>(`/identity/users/${user.id}/status`, { status: next }, session?.token);
      users.reload();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t("admin.users.statusError"));
    } finally {
      setPendingId(null);
    }
  }

  const muted = (u: User) => (u.status === "active" ? undefined : brandTokens.colors.textSecondary);

  return (
    <section>
      <PageHeader title={t("admin.users.title")} subtitle={t("admin.users.subtitle")} />

      {created && (
        <TempPasswordCallout email={created.email} password={created.password} onDismiss={() => setCreated(null)} />
      )}
      {notice && <p role="status" style={{ color: brandTokens.colors.success, fontSize: 13 }}>{notice}</p>}
      {actionError && (
        <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{actionError}</p>
      )}

      <Toolbar
        right={
          canManage && (
            <button type="button" className="btn-primary" onClick={openCreate}>
              + {t("admin.users.newUser")}
            </button>
          )
        }
      />

      {users.loading && <p>{t("app.loading")}</p>}
      {users.error && <p>{users.error}</p>}
      {!users.loading && !users.error && (
        <DataTable
          rows={users.data}
          emptyMessage={t("admin.users.empty")}
          columns={[
            {
              key: "name",
              header: t("admin.users.name"),
              render: (r) => (
                <span style={{ color: muted(r) }}>
                  <span style={{ display: "block", fontWeight: 500 }}>{r.full_name}</span>
                  <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>
                    {r.email}
                    {r.employee_number ? ` · ${r.employee_number}` : ""}
                  </span>
                </span>
              ),
            },
            { key: "position", header: t("admin.users.colPosition"), render: (r) => r.position_name ?? t("app.none") },
            {
              key: "prof",
              header: t("admin.users.profession"),
              render: (r) => (
                <span>
                  {r.profession_name ?? t("app.none")}
                  {r.specialty && (
                    <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>{r.specialty}</span>
                  )}
                </span>
              ),
            },
            {
              key: "facilities",
              header: t("admin.users.colFacilities"),
              render: (r) => (
                <span style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {r.facility_ids.map((id) => (
                    <span key={id} className="chip">{facilityName.get(id) ?? "…"}</span>
                  ))}
                  {r.is_corporate_scope && (
                    <span className="chip" style={{ background: brandTokens.colors.surfaceSoft }}>{t("admin.users.corporateChip")}</span>
                  )}
                </span>
              ),
            },
            {
              key: "roles",
              header: t("admin.users.colRoles"),
              render: (r) => (
                <span style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {r.role_ids.map((id) => (
                    <span key={id} className="chip">{roleName.get(id) ?? "…"}</span>
                  ))}
                </span>
              ),
            },
            {
              key: "status",
              header: t("admin.users.status"),
              render: (r) =>
                canManage ? (
                  <StatusSelect
                    value={r.status}
                    disabled={pendingId === r.id || r.id === me?.id}
                    label={t("admin.users.status")}
                    onChange={(next) => changeStatus(r, next)}
                  />
                ) : (
                  <span style={{ color: muted(r) }}>{t(`app.status.${r.status}`)}</span>
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
        title={drawer?.mode === "edit" ? t("admin.users.editUser") : t("admin.users.newUser")}
        subtitle={drawer?.mode === "edit" ? drawer.user.email : t("admin.users.createSubtitle")}
        onClose={closeDrawer}
        footer={
          <>
            <button type="button" className="btn-ghost" onClick={closeDrawer} disabled={submitting}>
              {t("app.cancel")}
            </button>
            <button type="submit" form="user-form" className="btn-primary" disabled={submitting}>
              {submitting ? t("app.saving") : t("app.save")}
            </button>
          </>
        }
      >
        <form id="user-form" onSubmit={handleSubmit}>
          <p style={sectionTitle}>{t("admin.users.identitySection")}</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 12px" }}>
            <FormField label={t("admin.users.firstName")} required>
              <input value={form.first_name} onChange={(e) => set("first_name", e.target.value)} required />
            </FormField>
            <FormField label={t("admin.users.lastName")} required>
              <input value={form.last_name} onChange={(e) => set("last_name", e.target.value)} required />
            </FormField>
          </div>
          <FormField label={t("admin.users.employeeNumber")} required>
            <input value={form.employee_number} onChange={(e) => set("employee_number", e.target.value)} required />
          </FormField>
          <FormField label={t("admin.users.email")} required>
            <input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required />
          </FormField>
          <FormField label={t("admin.users.mobile")}>
            <input value={form.mobile} onChange={(e) => set("mobile", e.target.value)} />
          </FormField>

          <p style={sectionTitle}>{t("admin.users.orgSection")}</p>
          <FormField label={t("admin.users.position")}>
            <select value={form.organizational_position_id} onChange={(e) => set("organizational_position_id", e.target.value)}>
              <option value="">{t("admin.users.noPosition")}</option>
              {positions.data.filter((p) => p.is_active || p.id === form.organizational_position_id).map((p) => (
                <option key={p.id} value={p.id}>{p.title}</option>
              ))}
            </select>
          </FormField>
          <CheckboxGroup
            label={t("admin.users.facilities")}
            required
            options={facilities.data.filter((f) => f.is_active || form.facility_ids.includes(f.id)).map((f) => ({ value: f.id, label: f.name }))}
            value={form.facility_ids}
            onChange={(v) => set("facility_ids", v)}
            columns={2}
          />
          <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontSize: 13, marginBottom: 16, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={form.is_corporate_scope}
              onChange={(e) => set("is_corporate_scope", e.target.checked)}
              style={{ width: "auto", margin: "3px 0 0", accentColor: brandTokens.colors.primary }}
            />
            <span>
              <span style={{ fontWeight: 500 }}>{t("admin.users.corporateScope")}</span>
              <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>{t("admin.users.corporateHint")}</span>
            </span>
          </label>
          <FormField label={t("admin.users.profession")} hint={t("admin.users.professionHint")}>
            <select value={form.profession_id} onChange={(e) => set("profession_id", e.target.value)}>
              <option value="">{t("admin.users.selectPlaceholder")}</option>
              {professions.data.filter((p) => p.is_active || p.id === form.profession_id).map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </FormField>

          <p style={sectionTitle}>{t("admin.users.accessSection")}</p>
          <CheckboxGroup
            label={t("admin.users.roles")}
            required
            options={roles.data.filter((r) => r.is_active || form.role_ids.includes(r.id)).map((r) => ({ value: r.id, label: r.name, hint: r.code }))}
            value={form.role_ids}
            onChange={(v) => set("role_ids", v)}
            columns={2}
          />
          <p style={{ fontSize: 12, color: brandTokens.colors.textSecondary, margin: "-8px 0 12px" }}>{t("admin.users.rolesHint")}</p>

          {formError && (
            <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{formError}</p>
          )}
        </form>
      </Drawer>
    </section>
  );
}
