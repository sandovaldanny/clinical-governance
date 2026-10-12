import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../../../theme/brand-tokens";
import { formatScore, type ScoreResult } from "../scoring";
import { OutcomeBadge } from "./OutcomeBadge";

function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div style={{ display: "grid", gap: 2 }}>
      <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", color: brandTokens.colors.textSecondary }}>{label}</span>
      <span style={{ fontSize: 18, fontWeight: 600 }}>{value}</span>
    </div>
  );
}

/** Barra fija inferior: aplicables · Yes · score · outcome en vivo + acciones (guardar / enviar / aprobar). */
export function ScoreBar({ score, answered, total, actions }: { score: ScoreResult; answered: number; total: number; actions: ReactNode }) {
  const { t } = useTranslation();
  return (
    <div data-testid="score-bar"
         style={{ position: "sticky", bottom: 0, zIndex: 5, background: brandTokens.colors.surface, borderTop: `1px solid ${brandTokens.colors.border}`,
                  boxShadow: "0 -6px 24px rgba(22, 69, 92, 0.08)", padding: "12px 20px", display: "flex", alignItems: "center",
                  justifyContent: "space-between", gap: 20, flexWrap: "wrap", marginTop: 24, borderRadius: `${brandTokens.radius.md}px ${brandTokens.radius.md}px 0 0` }}>
      <div style={{ display: "flex", gap: 28, alignItems: "center", flexWrap: "wrap" }}>
        <Stat label={t("ucca.form.answered", { done: answered, total })} value={`${answered}/${total}`} />
        <Stat label={t("ucca.form.applicable")} value={score.applicable} />
        <Stat label={t("ucca.form.yesCount")} value={score.yes} />
        <Stat label={t("ucca.form.score")} value={formatScore(score.score)} />
        <Stat label={t("ucca.form.outcome")} value={<OutcomeBadge outcome={score.outcome} size="lg" />} />
      </div>
      <div style={{ display: "flex", gap: 10 }}>{actions}</div>
    </div>
  );
}
