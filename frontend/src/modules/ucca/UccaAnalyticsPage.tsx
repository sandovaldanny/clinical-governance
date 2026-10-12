import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { brandTokens } from "../../theme/brand-tokens";
import { KpiCard } from "./components/KpiCard";
import { OutcomeBadge } from "./components/OutcomeBadge";
import { RateBars } from "./components/RateBars";
import { formatScore } from "./scoring";
import type { Cycle, Summary } from "./types";

type Facility = { id: string; name: string };
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`, borderRadius: brandTokens.radius.lg,
                  boxShadow: brandTokens.shadow.card, padding: 20, minWidth: 0 }}>
      <h2 style={{ fontSize: 16, margin: "0 0 14px" }}>{title}</h2>
      {children}
    </div>
  );
}

/** Dashboard → UCCA. Agregados multi-ciclo (solo auditorías enviadas/aprobadas) con filtros por
 * centro, año y trimestre: KPIs, % Yes por criterio, tendencia, tabla por profesional y acciones
 * correctivas abiertas. */
export function UccaAnalyticsPage() {
  const { t } = useTranslation();
  const facilities = useApiList<Facility>("/identity/facilities");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const [facilityId, setFacilityId] = useState("");
  const [year, setYear] = useState("");
  const [quarter, setQuarter] = useState("");

  const query = useMemo(() => {
    const q = new URLSearchParams();
    if (facilityId) q.set("facility_id", facilityId);
    if (year) q.set("year", year);
    if (quarter) q.set("quarter", quarter);
    const s = q.toString();
    return `/ucca/dashboard${s ? `?${s}` : ""}`;
  }, [facilityId, year, quarter]);
  const summary = useApiGet<Summary>(query);
  const years = Array.from(new Set(cycles.data.map((c) => c.year))).sort((a, b) => b - a);
  const s = summary.data;
  const compliantRate = s && s.audits_count > 0 ? Math.round((s.outcome_distribution.compliant / s.audits_count) * 100) : null;
  const codes = s?.criteria.map((c) => c.code) ?? [];

  const select = (value: string, onChange: (v: string) => void, options: { value: string; label: string }[], label: string) => (
    <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600, color: brandTokens.colors.textSecondary }}>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)} style={{ minWidth: 160 }}>
        <option value="">{t("ucca.dashboard.filters.all")}</option>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  );

  return (
    <section>
      <PageHeader title={t("ucca.dashboard.title")} subtitle={t("ucca.dashboard.subtitle")} />
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
        {select(facilityId, setFacilityId, facilities.data.map((f) => ({ value: f.id, label: f.name })), t("ucca.dashboard.filters.facility"))}
        {select(year, setYear, years.map((y) => ({ value: String(y), label: String(y) })), t("ucca.dashboard.filters.year"))}
        {select(quarter, setQuarter, QUARTERS.map((q) => ({ value: q, label: q })), t("ucca.dashboard.filters.quarter"))}
      </div>

      {summary.loading && <p>{t("app.loading")}</p>}
      {summary.error && <p>{summary.error}</p>}
      {s && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 20 }}>
            <KpiCard label={t("ucca.kpi.audits")} value={s.audits_count} hint={s.draft_count > 0 ? t("ucca.kpi.drafts", { count: s.draft_count }) : undefined} />
            <KpiCard label={t("ucca.kpi.averageScore")} value={formatScore(s.average_score)} />
            <KpiCard label={t("ucca.kpi.compliantRate")} value={compliantRate === null ? "—" : `${compliantRate} %`} />
            <KpiCard label={t("ucca.kpi.openActions")} value={s.open_corrective_actions.length} />
          </div>
          {s.audits_count === 0 && <p style={{ color: brandTokens.colors.textSecondary }}>{t("ucca.dashboard.empty")}</p>}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16, marginBottom: 20 }}>
            <Card title={t("ucca.dashboard.byCriterion")}>
              <RateBars items={s.criteria.map((c) => ({ label: c.code, value: c.yes_rate, hint: `${c.yes}/${c.applicable}` }))} />
            </Card>
            <Card title={t("ucca.dashboard.trend")}>
              <RateBars items={s.trend.map((p) => ({ label: `${p.quarter}-${p.year}`, value: p.average_score, hint: `${p.audits_count}` }))} />
            </Card>
          </div>

          <Card title={t("ucca.dashboard.byProfessional")}>
            <DataTable
              dense
              rows={s.professionals.map((p) => ({ ...p, id: p.professional_id }))}
              emptyMessage={t("ucca.dashboard.empty")}
              columns={[
                { key: "cg", header: t("ucca.table.cgId"), width: 64, render: (r) => <code style={{ fontSize: 12, whiteSpace: "nowrap" }}>{r.employee_number}</code> },
                { key: "name", header: t("ucca.table.professional"), render: (r) => (
                  <span style={{ display: "block", fontSize: 13 }}><strong style={{ fontWeight: 500 }}>{r.professional_name}</strong>
                    <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>{r.profession_name ?? "—"}</span></span>
                ) },
                { key: "n", header: t("ucca.auditsCount"), width: 70, render: (r) => r.audits_count },
                { key: "score", header: t("ucca.table.score"), width: 64, render: (r) => <strong style={{ fontSize: 13, whiteSpace: "nowrap" }}>{formatScore(r.average_score)}</strong> },
                { key: "outcome", header: t("ucca.table.outcome"), width: 132, render: (r) => <OutcomeBadge outcome={r.outcome} /> },
                ...codes.map((code) => ({ key: code, header: code, width: 44,
                  render: (r: Summary["professionals"][number]) => <span style={{ fontSize: 12 }}>{r.criteria[code] === null ? "—" : `${r.criteria[code]}%`}</span> })),
              ]}
            />
          </Card>

          <div style={{ marginTop: 20 }}>
            <Card title={t("ucca.dashboard.openActions")}>
              <DataTable
                dense
                rows={s.open_corrective_actions}
                emptyMessage={t("ucca.dashboard.noActions")}
                columns={[
                  { key: "mrn", header: t("ucca.table.mrn"), width: 100, render: (r) => (
                    <Link to={`/ucca/audits/${r.audit_id}`} style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 600 }}>{r.case_reference}</Link>
                  ) },
                  { key: "pro", header: t("ucca.table.professional"), width: 160, render: (r) => r.professional_name },
                  { key: "finding", header: t("ucca.dashboard.finding"), render: (r) => <span style={{ fontSize: 13 }}>{r.finding}</span> },
                  { key: "owner", header: t("ucca.dashboard.owner"), width: 140, render: (r) => r.responsible_name ?? "—" },
                  { key: "due", header: t("ucca.dashboard.due"), width: 96, render: (r) => r.due_date },
                  { key: "st", header: t("ucca.table.status"), width: 90, render: (r) => <StatusBadge code={r.status} ns="ucca.actionStatuses" /> },
                ]}
              />
            </Card>
          </div>
        </>
      )}
    </section>
  );
}
