import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../theme/brand-tokens";

type Tone = "neutral" | "success" | "warning" | "danger";

const TONES: Record<Tone, { bg: string; fg: string }> = {
  neutral: { bg: alkalma.bgSoft, fg: brandTokens.colors.textPrimary },
  success: { bg: alkalma.turquoiseTint, fg: alkalma.indigo },
  warning: { bg: "#FBEFD9", fg: alkalma.indigo },
  danger: { bg: "#F8E3E1", fg: brandTokens.colors.danger },
};

function toneFor(code: string): Tone {
  if (code === "compliant" || code === "approved" || code === "closed") return "success";
  if (code === "non_compliant" || code === "critical") return "danger";
  if (code === "major" || code === "submitted" || code === "in_progress") return "warning";
  return "neutral";
}

/** Chip traducido para estados/resultados/severidades. `ns` indica la rama i18n. */
export function StatusBadge({ code, ns }: { code: string; ns: "ucca.statuses" | "ucca.outcomes" | "ucca.answers" | "ucca.actionStatuses" | "indicators.severities" }) {
  const { t } = useTranslation();
  const tone = TONES[toneFor(code)];
  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 10px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 600,
        background: tone.bg,
        color: tone.fg,
      }}
    >
      {t(`${ns}.${code}`, { defaultValue: code })}
    </span>
  );
}
