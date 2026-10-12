import type { CSSProperties } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { Toolbar } from "../../components/Toolbar";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { useCanManage } from "../../hooks/useCanManage";
import { brandTokens } from "../../theme/brand-tokens";
import { AnswerChip } from "./components/AnswerChip";
import { KpiCard } from "./components/KpiCard";
import { OutcomeBadge } from "./components/OutcomeBadge";
import { formatScore } from "./scoring";
import type { ChartAuditRow, Criterion, Cycle, Summary } from "./types";

const small: CSSProperties = { fontSize: 13 };
const muted: CSSProperties = { fontSize: 12, color: brandTokens.colors.textSecondary };

/** UCCA → Ciclo: KPIs del ciclo + tabla tipo Excel (una fila por expediente auditado, una columna
 * por criterio con ✓ / ✗ / N/A, score y outcome). */
export function UccaCyclePage() {
  const { t } = useTranslation();
  const { cycleId = "" } = useParams<{ cycleId: string }>();
  const canCreate = useCanManage("ucca.create");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const audits = useApiList<ChartAuditRow>(cycleId ? `/ucca/cycles/${cycleId}/audits` : "");
  const summary = useApiGet<Summary>(cycleId ? `/ucca/cycles/${cycleId}/summary` : "");
  const criteria = useApiList<Criterion>("/ucca/criteria?only_active=true");

  const cycle = cycles.data.find((c) => c.id === cycleId);
  if (!cycleId) return <p>{t("ucca.cycleMissing")}</p>;
  if (cycles.loading) return <p>{t("ucca.loadingCycles")}</p>;
  if (!cycle) return <p>{t("ucca.cycleNotFound")}</p>;

  const s = summary.data;
  const compliantRate = s && s.audits_count > 0 ? Math.round((s.outcome_distribution.compliant / s.audits_count) * 100) : null;
  const codes = criteria.data.map((c) => c.code);

  return (
    <section>
      <p style={{ margin: "0 0 18px" }}>
        <Link to="/ucca" style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 500 }}>← {t("ucca.back")}</Link>
      </p>
      <PageHeader title={t("ucca.cycleTitle", { period: cycle.period_label })}
                  subtitle={t("ucca.cycleSubtitle", { facility: cycle.facility_name ?? "—" })} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 20 }}>
        <KpiCard label={t("ucca.kpi.audits")} value={s?.audits_count ?? "—"}
                 hint={s && s.draft_count > 0 ? t("ucca.kpi.drafts", { count: s.draft_count }) : undefined} />
        <KpiCard label={t("ucca.kpi.averageScore")} value={formatScore(s?.average_score ?? null)} />
        <KpiCard label={t("ucca.kpi.compliantRate")} value={compliantRate === null ? "—" : `${compliantRate} %`} />
        <KpiCard label={t("ucca.kpi.openActions")} value={s?.open_corrective_actions.length ?? "—"} />
      </div>

      <Toolbar right={canCreate && (
        <Link to={`/ucca/cycles/${cycleId}/audits/new`} className="btn-primary" style={{ textDecoration: "none" }}>+ {t("ucca.newAudit")}</Link>
      )} />

      {audits.loading && <p>{t("app.loading")}</p>}
      {audits.error && <p>{audits.error}</p>}
      {!audits.loading && !audits.error && (
        <DataTable
          rows={audits.data.map((r, i) => ({ ...r, num: i + 1 }))}
          emptyMessage={t("ucca.table.empty")}
          columns={[
            { key: "num", header: t("ucca.table.num"), width: 36, render: (r) => <span style={muted}>{r.num}</span> },
            { key: "cg", header: t("ucca.table.cgId"), width: 80, render: (r) => <code style={{ fontSize: 12 }}>{r.employee_number}</code> },
            { key: "pro", header: t("ucca.table.professional"), render: (r) => (
              <span style={{ display: "block", ...small }}>
                <strong style={{ fontWeight: 500 }}>{r.professional_name}</strong>
                <span style={{ display: "block", ...muted }}>{r.profession_name ?? "—"}</span>
              </span>
            ) },
            { key: "mrn", header: t("ucca.table.mrn"), width: 110, render: (r) => (
              <>
                <code style={{ fontSize: 12 }}>{r.case_reference}</code>
                {r.has_finding && (
                  <span aria-label={t("ucca.table.finding")} title={t("ucca.table.finding")}
                        style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: brandTokens.colors.warning, marginLeft: 6 }} />
                )}
              </>
            ) },
            { key: "date", header: t("ucca.table.date"), width: 96, render: (r) => <span style={small}>{r.audit_date}</span> },
            ...codes.map((code) => ({
              key: code, header: code, width: 44,
              render: (r: ChartAuditRow) => <AnswerChip value={r.answers[code]} />,
            })),
            { key: "app", header: t("ucca.table.applicable"), width: 52, render: (r) => <span style={small}>{r.applicable_count}</span> },
            { key: "yes", header: t("ucca.table.yes"), width: 44, render: (r) => <span style={small}>{r.yes_count}</span> },
            { key: "score", header: t("ucca.table.score"), width: 70, render: (r) => <strong style={{ ...small, fontWeight: 600 }}>{formatScore(r.score)}</strong> },
            { key: "outcome", header: t("ucca.table.outcome"), width: 140, render: (r) => <OutcomeBadge outcome={r.outcome} /> },
            { key: "status", header: t("ucca.table.status"), width: 90, render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            { key: "open", header: "", width: 64, render: (r) => (
              <Link to={`/ucca/audits/${r.id}`} className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12, textDecoration: "none" }}>{t("ucca.table.open")}</Link>
            ) },
          ]}
        />
      )}
    </section>
  );
}
