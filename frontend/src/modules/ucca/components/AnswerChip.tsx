import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import type { AnswerValue } from "../types";

const STYLE: Record<AnswerValue, { bg: string; fg: string; glyph: string }> = {
  compliant: { bg: alkalma.turquoiseTint, fg: alkalma.turquoiseDark, glyph: "✓" },
  non_compliant: { bg: "#F8E3E1", fg: brandTokens.colors.danger, glyph: "✗" },
  not_applicable: { bg: alkalma.bgSoft, fg: brandTokens.colors.textSecondary, glyph: "N/A" },
};

/** Celda compacta Yes/No/N/A de la tabla tipo Excel. `undefined` → guion (sin respuesta). */
export function AnswerChip({ value }: { value: AnswerValue | undefined }) {
  const { t } = useTranslation();
  if (!value) return <span style={{ color: brandTokens.colors.textSecondary }}>—</span>;
  const s = STYLE[value];
  return (
    <span title={t(`ucca.answers.${value}`)} aria-label={t(`ucca.answers.${value}`)}
          style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", minWidth: 26, height: 22, padding: "0 4px",
                   borderRadius: 999, fontSize: 11, fontWeight: 700, background: s.bg, color: s.fg }}>
      {s.glyph}
    </span>
  );
}
