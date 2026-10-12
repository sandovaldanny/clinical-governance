import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import { formatScore } from "../scoring";
import type { ChartAudit } from "../types";
import { OutcomeBadge } from "./OutcomeBadge";

export type NoticeKind = "saved" | "submitted" | "approved";

/** Resumen destacado tras guardar / enviar / aprobar: qué se guardó, con qué resultado y cuál es el
 * siguiente paso. Sustituye al mensaje de una línea. */
export function SaveNotice({ kind, audit, onClose, ownerName }: { kind: NoticeKind; audit: ChartAudit; onClose: () => void; ownerName?: (id: string) => string | undefined }) {
  const { t } = useTranslation();
  const action = audit.finding?.corrective_action && audit.finding.corrective_action.status !== "cancelled" ? audit.finding.corrective_action : null;
  const next = kind === "saved" ? t("ucca.notice.nextSubmit") : kind === "submitted" ? t("ucca.notice.nextApprove") : t("ucca.notice.nextDone");
  return (
    <div role="status" data-testid="save-notice"
         style={{ background: alkalma.turquoiseTint, border: `1px solid ${brandTokens.colors.accent}`, borderLeft: `5px solid ${brandTokens.colors.accent}`,
                  borderRadius: brandTokens.radius.md, padding: "14px 18px", marginTop: 20, display: "grid", gap: 8, fontSize: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <strong style={{ fontSize: 15 }}>✓ {t(`ucca.notice.${kind}`)}</strong>
        <button type="button" className="btn-ghost" onClick={onClose} style={{ padding: "2px 10px", fontSize: 12 }}>{t("app.close")}</button>
      </div>
      <div>
        {t("ucca.notice.summary", { mrn: audit.case_reference, name: audit.professional_name, cg: audit.employee_number,
                                     yes: audit.yes_count, applicable: audit.applicable_count, score: formatScore(audit.score) })}{" "}
        <OutcomeBadge outcome={audit.outcome} />
      </div>
      {audit.finding && audit.finding.status !== "withdrawn" && (
        <div style={{ color: brandTokens.colors.textPrimary }}>
          {t("ucca.notice.finding", { finding: audit.finding.description })}
          {action && (
            <> {t("ucca.notice.action", { description: action.description, owner: action.responsible_name ?? ownerName?.(action.responsible_user_id) ?? t("ucca.notice.ownerAssigned"),
                                            due: action.due_date, status: t(`ucca.actionStatuses.${action.status}`) })}</>
          )}
        </div>
      )}
      <div style={{ color: brandTokens.colors.textSecondary, fontSize: 13 }}>{next}</div>
    </div>
  );
}
