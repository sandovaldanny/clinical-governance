import { FormEvent, useMemo, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson, apiPostJson } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { useApiList } from "../hooks/useApiList";
import { useCanManage } from "../hooks/useCanManage";
import { alkalma, brandTokens } from "../theme/brand-tokens";
import { DataTable } from "./DataTable";
import { Drawer } from "./Drawer";
import { FormField } from "./FormField";
import { PageHeader } from "./PageHeader";
import { StatusToggle } from "./StatusToggle";
import { Toolbar } from "./Toolbar";

/**
 * Página genérica de datos maestros (M02): tabla + drawer crear/editar + estado.
 * Cada tabla admin (cargos, centros, profesiones, especialidades) la configura con `fields`,
 * `columns` y `status`; así todas comparten el mismo comportamiento y estilo.
 */

export type FieldOption = { value: string; label: string };

export type FieldSpec = {
  key: string;
  labelKey: string;
  type: "text" | "textarea" | "select";
  required?: boolean;
  hintKey?: string;
  /** Opciones estáticas o resueltas desde una lista cargada (ver `optionsFrom`). */
  options?: FieldOption[];
  /** Ruta API de la que se leen las opciones; se mapea con `optionLabel`/`optionValue`. */
  optionsFrom?: { path: string; value: string; label: string; onlyActive?: boolean };
  /** Solo editable al crear (ej. tipo de catálogo fijo). */
  createOnly?: boolean;
  /** Valor fijo inyectado en el payload (no se muestra). */
  fixed?: string;
};

export type ColumnSpec<T> = { key: string; headerKey: string; render: (row: T) => ReactNode; width?: number | string };

export type StatusSpec =
  | { kind: "toggle"; field: "is_active" }
  | { kind: "select"; field: string; values: string[] };

export type MasterDataPageProps<T extends { id: string }> = {
  titleKey: string;
  subtitleKey: string;
  emptyKey: string;
  newKey: string;
  editKey: string;
  listPath: string;
  writePath: string;
  managePermission: string;
  fields: FieldSpec[];
  columns: ColumnSpec<T>[];
  status: StatusSpec;
  /** Nombre visible de una fila (subtítulo del drawer en edición). */
  rowLabel: (row: T) => string;
};

type Values = Record<string, string>;

function OptionsSelect({ spec, value, onChange, dynamic }: { spec: FieldSpec; value: string; onChange: (v: string) => void; dynamic: FieldOption[] }) {
  const { t } = useTranslation();
  const options = spec.options ?? dynamic;
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} required={spec.required}>
      <option value="">{t("admin.users.selectPlaceholder")}</option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}

function DynamicOptions({ spec, children }: { spec: FieldSpec; children: (opts: FieldOption[]) => ReactNode }) {
  const src = spec.optionsFrom;
  const list = useApiList<Record<string, unknown>>(src ? src.path : "");
  const opts = useMemo<FieldOption[]>(() => {
    if (!src) return [];
    return list.data
      .filter((row) => !src.onlyActive || row["is_active"] !== false)
      .map((row) => ({ value: String(row[src.value]), label: String(row[src.label]) }));
  }, [list.data, src]);
  return <>{children(opts)}</>;
}

export function MasterDataPage<T extends { id: string }>(props: MasterDataPageProps<T>) {
  const { t } = useTranslation();
  const { session } = useAuth();
  const canManage = useCanManage(props.managePermission);
  const list = useApiList<T>(props.listPath);

  const [drawer, setDrawer] = useState<{ mode: "create" } | { mode: "edit"; row: T } | null>(null);
  const [values, setValues] = useState<Values>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  function emptyValues(): Values {
    return Object.fromEntries(props.fields.map((f) => [f.key, f.fixed ?? ""]));
  }
  function valuesFrom(row: T): Values {
    const r = row as unknown as Record<string, unknown>;
    return Object.fromEntries(props.fields.map((f) => [f.key, f.fixed ?? (r[f.key] == null ? "" : String(r[f.key]))]));
  }
  function openCreate() {
    setValues(emptyValues());
    setFormError(null);
    setDrawer({ mode: "create" });
  }
  function openEdit(row: T) {
    setValues(valuesFrom(row));
    setFormError(null);
    setDrawer({ mode: "edit", row });
  }
  function closeDrawer() {
    if (!submitting) setDrawer(null);
  }

  function payload(): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    for (const f of props.fields) {
      if (drawer?.mode === "edit" && f.createOnly) continue;
      const v = (values[f.key] ?? "").trim();
      if (f.type === "select") out[f.key] = v || null;
      else if (f.type === "textarea") out[f.key] = v;
      else out[f.key] = f.required ? v : v || null;
    }
    return out;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!drawer) return;
    setSubmitting(true);
    setFormError(null);
    setNotice(null);
    try {
      if (drawer.mode === "create") {
        await apiPostJson(props.writePath, payload(), session?.token);
        setNotice(t("app.created"));
      } else {
        await apiPatchJson(`${props.writePath}/${drawer.row.id}`, payload(), session?.token);
        setNotice(t("app.updated"));
      }
      setDrawer(null);
      list.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setSubmitting(false);
    }
  }

  async function changeStatus(row: T, body: Record<string, unknown>) {
    setPendingId(row.id);
    setActionError(null);
    try {
      await apiPatchJson(`${props.writePath}/${row.id}`, body, session?.token);
      list.reload();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setPendingId(null);
    }
  }

  const isActiveRow = (row: T) => (row as unknown as Record<string, unknown>)["is_active"] !== false;

  const statusColumn: ColumnSpec<T> = {
    key: "__status",
    headerKey: "app.statusLabel",
    width: 130,
    render: (row) => {
      const r = row as unknown as Record<string, unknown>;
      if (props.status.kind === "toggle") {
        const active = isActiveRow(row);
        return (
          <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            {canManage && (
              <StatusToggle
                checked={active}
                disabled={pendingId === row.id}
                label={active ? t("app.deactivate") : t("app.activate")}
                onChange={(next) => changeStatus(row, { is_active: next })}
              />
            )}
            <span style={{ fontSize: 13, color: active ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary }}>
              {active ? t("app.status.active") : t("app.status.inactive")}
            </span>
          </span>
        );
      }
      const spec = props.status;
      const current = String(r[spec.field] ?? spec.values[0]);
      const active = current === spec.values[0];
      return (
        <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          <span aria-hidden style={{ width: 8, height: 8, borderRadius: "50%", background: active ? alkalma.turquoise : alkalma.bluegray }} />
          {canManage ? (
            <select
              aria-label={t("app.statusLabel")}
              value={current}
              disabled={pendingId === row.id}
              onChange={(e) => changeStatus(row, { [spec.field]: e.target.value })}
              style={{ width: "auto", padding: "4px 26px 4px 8px", fontSize: 13, borderRadius: 999 }}
            >
              {spec.values.map((v) => (
                <option key={v} value={v}>{t(`app.status.${v}`)}</option>
              ))}
            </select>
          ) : (
            <span style={{ fontSize: 13 }}>{t(`app.status.${current}`)}</span>
          )}
        </span>
      );
    },
  };

  const editColumn: ColumnSpec<T> = {
    key: "__edit",
    headerKey: "",
    width: 72,
    render: (row) =>
      canManage ? (
        <button type="button" className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => openEdit(row)}>
          {t("app.edit")}
        </button>
      ) : null,
  };

  const visibleFields = props.fields.filter((f) => f.fixed === undefined && !(drawer?.mode === "edit" && f.createOnly));

  return (
    <section>
      <PageHeader title={t(props.titleKey)} subtitle={t(props.subtitleKey)} />
      {notice && <p role="status" style={{ color: brandTokens.colors.success, fontSize: 13 }}>{notice}</p>}
      {actionError && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{actionError}</p>}

      <Toolbar
        right={
          canManage && (
            <button type="button" className="btn-primary" onClick={openCreate}>
              + {t(props.newKey)}
            </button>
          )
        }
      />

      {list.loading && <p>{t("app.loading")}</p>}
      {list.error && <p>{list.error}</p>}
      {!list.loading && !list.error && (
        <DataTable
          rows={list.data.map((row) => ({ ...row, __muted: !isActiveRow(row) }))}
          emptyMessage={t(props.emptyKey)}
          columns={[...props.columns, statusColumn, editColumn].map((c) => ({
            key: c.key,
            header: c.headerKey ? t(c.headerKey) : "",
            width: c.width,
            render: (row: T & { __muted: boolean }) => (
              <span style={{ color: row.__muted && c.key !== "__status" ? brandTokens.colors.textSecondary : undefined }}>
                {c.render(row)}
              </span>
            ),
          }))}
        />
      )}

      <Drawer
        open={drawer !== null}
        title={drawer?.mode === "edit" ? t(props.editKey) : t(props.newKey)}
        subtitle={drawer?.mode === "edit" ? props.rowLabel(drawer.row) : undefined}
        onClose={closeDrawer}
        footer={
          <>
            <button type="button" className="btn-ghost" onClick={closeDrawer} disabled={submitting}>{t("app.cancel")}</button>
            <button type="submit" form="master-form" className="btn-primary" disabled={submitting}>
              {submitting ? t("app.saving") : t("app.save")}
            </button>
          </>
        }
      >
        <form id="master-form" onSubmit={handleSubmit}>
          {visibleFields.map((f) => (
            <FormField key={f.key} label={t(f.labelKey)} required={f.required} hint={f.hintKey ? t(f.hintKey) : undefined}>
              {f.type === "text" && (
                <input value={values[f.key] ?? ""} onChange={(e) => setValues((v) => ({ ...v, [f.key]: e.target.value }))} required={f.required} />
              )}
              {f.type === "textarea" && (
                <textarea rows={3} value={values[f.key] ?? ""} onChange={(e) => setValues((v) => ({ ...v, [f.key]: e.target.value }))} required={f.required} />
              )}
              {f.type === "select" && f.optionsFrom && (
                <DynamicOptions spec={f}>
                  {(opts) => (
                    <OptionsSelect spec={f} dynamic={opts} value={values[f.key] ?? ""} onChange={(v) => setValues((s) => ({ ...s, [f.key]: v }))} />
                  )}
                </DynamicOptions>
              )}
              {f.type === "select" && !f.optionsFrom && (
                <OptionsSelect spec={f} dynamic={[]} value={values[f.key] ?? ""} onChange={(v) => setValues((s) => ({ ...s, [f.key]: v }))} />
              )}
            </FormField>
          ))}
          {formError && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{formError}</p>}
        </form>
      </Drawer>
    </section>
  );
}
