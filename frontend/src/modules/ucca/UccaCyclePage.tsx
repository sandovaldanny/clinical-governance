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
          dense
          rows={audits.data}
          emptyMessage={t("ucca.table.empty")}
          columns={[
            { key: "cg", header: t("ucca.table.cgId"), width: 64, render: (r) => <code style={{ fontSize: 12, whiteSpace: "nowrap" }}>{r.employee_number}</code> },
            { key: "pro", header: t("ucca.table.professional"), width: 220, render: (r) => (
              <span style={{ display: "block", ...small }}>
                <strong style={{ fontWeight: 500 }}>{r.professional_name}</strong>
                <span style={{ display: "block", ...muted }}>{r.profession_name ?? "—"}</span>
              </span>
            ) },
            { key: "mrn", header: t("ucca.table.mrn"), width: 96, render: (r) => (
              <span style={{ display: "block" }}>
                <Link to={`/ucca/audits/${r.id}`} title={t("ucca.table.open")}
                      style={{ color: brandTokens.colors.link, fontWeight: 600, textDecoration: "none", fontFamily: "monospace", fontSize: 12 }}>
                  {r.case_reference}
                </Link>
                {r.has_finding && (
                  <span aria-label={t("ucca.table.finding")} title={t("ucca.table.finding")}
                        style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: brandTokens.colors.warning, marginLeft: 6 }} />
                )}
                <span style={{ display: "block", ...muted }}>{r.audit_date}</span>
              </span>
            ) },
            ...codes.map((code) => ({
              key: code, header: code, width: 34,
              render: (r: ChartAuditRow) => <AnswerChip value={r.answers[code]} />,
            })),
            { key: "yes", header: `${t("ucca.table.yes")}/${t("ucca.table.applicable")}`, width: 60, render: (r) => (
              <span style={small}>{r.yes_count}/{r.applicable_count}</span>
            ) },
            { key: "score", header: t("ucca.table.score"), width: 60, render: (r) => <strong style={{ ...small, fontWeight: 600, whiteSpace: "nowrap" }}>{formatScore(r.score)}</strong> },
            { key: "outcome", header: t("ucca.table.outcome"), render: (r) => (
              <span style={{ display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
                <OutcomeBadge outcome={r.outcome} />
                <StatusBadge code={r.status} ns="ucca.statuses" />
              </span>
            ) },
          ]}
        />
      )}
    </section>
  );
}
