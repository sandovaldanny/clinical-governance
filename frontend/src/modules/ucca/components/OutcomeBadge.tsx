import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import type { Outcome } from "../types";

const STYLES: Record<Outcome, { bg: string; fg: string }> = {
  compliant: { bg: alkalma.turquoiseTint, fg: alkalma.indigo },
  minor_improvement: { bg: "#FBEFD9", fg: alkalma.indigo },
  improvement_required: { bg: "#F6DFB8", fg: alkalma.indigoDark },
  priority_corrective_action: { bg: "#F8E3E1", fg: brandTokens.colors.danger },
};

/** Badge de outcome (bandas del Excel). `null` → guion gris (sin aplicables). */
export function OutcomeBadge({ outcome, size = "sm" }: { outcome: Outcome | null; size?: "sm" | "lg" }) {
  const { t } = useTranslation();
  if (!outcome) return <span style={{ color: brandTokens.colors.textSecondary }}>—</span>;
  const s = STYLES[outcome];
  return (
    <span style={{ display: "inline-block", padding: size === "lg" ? "6px 14px" : "3px 10px", borderRadius: 999,
                   fontSize: size === "lg" ? 14 : 12, fontWeight: 600, background: s.bg, color: s.fg, whiteSpace: "nowrap" }}>
      {t(`ucca.outcomes.${outcome}`)}
    </span>
  );
}
