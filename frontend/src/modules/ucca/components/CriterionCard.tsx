import { useState } from "react";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../../../theme/brand-tokens";
import type { AnswerValue, Criterion } from "../types";
import { AnswerSelector } from "./AnswerSelector";

export type AnswerState = { outcome: AnswerValue | null; reason: string; comment: string };

export function CriterionCard({ criterion, state, onChange, readOnly, invalid }: {
  criterion: Criterion; state: AnswerState; onChange: (next: AnswerState) => void; readOnly: boolean; invalid: boolean;
}) {
  const { t } = useTranslation();
  const [details, setDetails] = useState(false);
  const border = invalid ? brandTokens.colors.danger : state.outcome ? brandTokens.colors.accent : brandTokens.colors.border;
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${border}`, borderLeft: `4px solid ${border}`,
                  borderRadius: brandTokens.radius.md, padding: "16px 18px", display: "grid", gap: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.04em", color: brandTokens.colors.textSecondary }}>
            <code>{criterion.code}</code> · {criterion.domain}
          </div>
          <div style={{ fontSize: 15, fontWeight: 500, marginTop: 4 }}>{criterion.universal_question}</div>
        </div>
        <AnswerSelector name={criterion.code} value={state.outcome} disabled={readOnly} onChange={(outcome) => onChange({ ...state, outcome })} />
      </div>
      <button type="button" className="btn-ghost" style={{ justifySelf: "start", padding: "2px 8px", fontSize: 12 }} onClick={() => setDetails((d) => !d)}>
        {details ? t("ucca.form.hideDetails") : t("ucca.form.showDetails")}
      </button>
      {details && (
        <div style={{ fontSize: 13, color: brandTokens.colors.textSecondary, display: "grid", gap: 6 }}>
          <div><strong style={{ color: brandTokens.colors.textPrimary }}>{t("ucca.form.interpretation")}:</strong> {criterion.profession_interpretation || "—"}</div>
          <div><strong style={{ color: brandTokens.colors.textPrimary }}>{t("ucca.form.evidence")}:</strong> {criterion.examples_evidence || "—"}</div>
        </div>
      )}
      {state.outcome === "not_applicable" && (
        <label style={{ display: "grid", gap: 4, fontSize: 13, fontWeight: 500 }}>
          {t("ucca.form.naReason")}
          <input value={state.reason} disabled={readOnly} required placeholder={t("ucca.form.naReasonPlaceholder")}
                 onChange={(e) => onChange({ ...state, reason: e.target.value })} />
        </label>
      )}
      <label style={{ display: "grid", gap: 4, fontSize: 13, fontWeight: 500 }}>
        {t("ucca.form.comment")}
        <input value={state.comment} disabled={readOnly} onChange={(e) => onChange({ ...state, comment: e.target.value })} />
      </label>
    </div>
  );
}
