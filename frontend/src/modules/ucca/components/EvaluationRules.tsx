import { useState } from "react";
import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import { OUTCOME_BANDS, PRIORITY_OUTCOME } from "../scoring";

/** Panel plegable "Reglas de evaluación": fórmula del score, bandas de outcome y reglas de negocio
 * (N/A con razón, hallazgo obligatorio, inmutabilidad). Mismo contenido que
 * docs/AEGIS_M04_UCCA_Chart_Audit.md; los umbrales se leen de scoring.ts para no divergir. */
export function EvaluationRules() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  return (
    <div data-testid="evaluation-rules"
         style={{ background: alkalma.bgSoft, border: `1px solid ${brandTokens.colors.border}`, borderRadius: brandTokens.radius.md, padding: "10px 16px", marginBottom: 12 }}>
      <button type="button" onClick={() => setOpen((o) => !o)} aria-expanded={open}
              style={{ background: "transparent", border: 0, padding: 0, cursor: "pointer", fontFamily: "inherit", fontSize: 13, fontWeight: 600, color: brandTokens.colors.link }}>
        {open ? "▾" : "▸"} {t("ucca.rules.title")}
      </button>
      {open && (
        <div style={{ fontSize: 13, color: brandTokens.colors.textPrimary, marginTop: 10, display: "grid", gap: 8 }}>
          <div><strong>{t("ucca.rules.scoreLabel")}:</strong> {t("ucca.rules.score")}</div>
          <div>
            <strong>{t("ucca.rules.outcomeLabel")}:</strong>
            <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
              {OUTCOME_BANDS.map(([outcome, threshold]) => (
                <li key={outcome}>≥ {threshold} % → {t(`ucca.outcomes.${outcome}`)}</li>
              ))}
              <li>&lt; {OUTCOME_BANDS[OUTCOME_BANDS.length - 1][1]} % → {t(`ucca.outcomes.${PRIORITY_OUTCOME}`)}</li>
            </ul>
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, color: brandTokens.colors.textSecondary }}>
            <li>{t("ucca.rules.na")}</li>
            <li>{t("ucca.rules.finding")}</li>
            <li>{t("ucca.rules.workflow")}</li>
            <li>{t("ucca.rules.dashboard")}</li>
          </ul>
        </div>
      )}
    </div>
  );
}
