import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ApiError, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { DataTable } from "../../components/DataTable";
import { Drawer } from "../../components/Drawer";
import { FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { Toolbar } from "../../components/Toolbar";
import { useApiList } from "../../hooks/useApiList";
import { useCanManage } from "../../hooks/useCanManage";
import { brandTokens } from "../../theme/brand-tokens";
import { formatScore, nextQuarter } from "./scoring";
import type { Cycle } from "./types";

type Facility = { id: string; name: string; is_active: boolean };
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

/** Gobierno clínico → UCCA. Lista de ciclos (centro + trimestre) y drawer "Nuevo ciclo". Al elegir
 * centro se precarga el siguiente trimestre libre de ese centro. */
export function UccaCyclesPage() {
  const { t } = useTranslation();
  const { session } = useAuth();
  const canCreate = useCanManage("ucca.create");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const facilities = useApiList<Facility>("/identity/facilities");

  const [open, setOpen] = useState(false);
  const [facilityId, setFacilityId] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [quarter, setQuarter] = useState(`Q${Math.floor(new Date().getMonth() / 3) + 1}`);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!facilityId) return;
    const next = nextQuarter(cycles.data.filter((c) => c.facility_id === facilityId));
    setYear(String(next.year));
    setQuarter(next.quarter);
  }, [facilityId, cycles.data]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await apiPostJson("/ucca/cycles", { facility_id: facilityId, year: Number(year), quarter }, session?.token);
      setOpen(false);
      cycles.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section>
      <PageHeader title={t("ucca.title")} subtitle={t("ucca.subtitle")} />
      <Toolbar right={canCreate && <button type="button" className="btn-primary" onClick={() => setOpen(true)}>+ {t("ucca.newCycle")}</button>} />
      {cycles.loading && <p>{t("ucca.loadingCycles")}</p>}
      {cycles.error && <p>{cycles.error}</p>}
      {!cycles.loading && !cycles.error && (
        <DataTable
          rows={cycles.data}
          emptyMessage={t("ucca.empty")}
          columns={[
            { key: "period", header: t("ucca.period"), render: (r) => (
              <Link to={`/ucca/cycles/${r.id}`} style={{ color: brandTokens.colors.link, fontWeight: 600, textDecoration: "none" }}>{r.period_label}</Link>
            ) },
            { key: "facility", header: t("ucca.facility"), render: (r) => r.facility_name ?? "—" },
            { key: "audits", header: t("ucca.auditsCount"), render: (r) => r.audits_count },
            { key: "score", header: t("ucca.averageScore"), render: (r) => formatScore(r.average_score) },
            { key: "status", header: t("ucca.status"), render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            { key: "open", header: "", width: 110, render: (r) => (
              <Link to={`/ucca/cycles/${r.id}`} className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12, textDecoration: "none" }}>{t("ucca.open")} →</Link>
            ) },
          ]}
        />
      )}

      <Drawer open={open} title={t("ucca.newCycle")} onClose={() => !saving && setOpen(false)}
        footer={<>
          <button type="button" className="btn-ghost" onClick={() => setOpen(false)} disabled={saving}>{t("app.cancel")}</button>
          <button type="submit" form="cycle-form" className="btn-primary" disabled={saving || !facilityId}>{saving ? t("app.saving") : t("app.save")}</button>
        </>}>
        <form id="cycle-form" onSubmit={submit}>
          <FormField label={t("ucca.cycleFacility")} required>
            <select value={facilityId} onChange={(e) => setFacilityId(e.target.value)} required>
              <option value="">{t("admin.users.selectPlaceholder")}</option>
              {facilities.data.filter((f) => f.is_active !== false).map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </FormField>
          <FormField label={t("ucca.cycleYear")} required hint={facilityId ? t("ucca.nextQuarterHint") : undefined}>
            <input type="number" min={2020} max={2100} value={year} onChange={(e) => setYear(e.target.value)} required />
          </FormField>
          <FormField label={t("ucca.cycleQuarter")} required>
            <select value={quarter} onChange={(e) => setQuarter(e.target.value)}>
              {QUARTERS.map((q) => <option key={q} value={q}>{q}</option>)}
            </select>
          </FormField>
          {error && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{error}</p>}
        </form>
      </Drawer>
    </section>
  );
}
