import { useTranslation } from "react-i18next";

import { PageHeader } from "../../components/PageHeader";
import { alkalma, brandTokens } from "../../theme/brand-tokens";
import { KpiCard } from "../ucca/components/KpiCard";
import {
  FRAMEWORK_ROWS,
  FRAMEWORK_SOURCE,
  RECOMMENDATIONS,
  type Bilingual,
  type FrameworkStatus,
} from "./framework-data";

const STATUS_TONES: Record<FrameworkStatus, { bg: string; fg: string }> = {
  compliant: { bg: alkalma.turquoiseTint, fg: alkalma.indigo },
  partial: { bg: "#FBEFD9", fg: alkalma.indigo },
  planned: { bg: alkalma.bgSoft, fg: brandTokens.colors.textPrimary },
  gap: { bg: "#F8E3E1", fg: brandTokens.colors.danger },
};

const STATUS_ORDER: FrameworkStatus[] = ["compliant", "partial", "planned", "gap"];

function StatusChip({ status }: { status: FrameworkStatus }) {
  const { t } = useTranslation();
  const tone = STATUS_TONES[status];
  return (
    <span style={{ display: "inline-block", padding: "3px 10px", borderRadius: 999, fontSize: 12, fontWeight: 600,
                   background: tone.bg, color: tone.fg, whiteSpace: "nowrap" }}>
      {t(`guides.statuses.${status}`)}
    </span>
  );
}

/** Gobierno clínico → Guías. Línea base de AEGIS contra el Clinical Governance Framework. */
export function GuidesPage() {
  const { t, i18n } = useTranslation();
  const lang: keyof Bilingual = i18n.language.startsWith("en") ? "en" : "es";
  const pick = (b: Bilingual) => b[lang];
  const counts = STATUS_ORDER.map((s) => ({ status: s, n: FRAMEWORK_ROWS.filter((r) => r.status === s).length }));

  const cell: React.CSSProperties = { padding: "12px 14px", fontSize: 13, verticalAlign: "top", lineHeight: 1.45 };
  const head: React.CSSProperties = { ...cell, fontSize: 11, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase",
                                      color: brandTokens.colors.textSecondary };

  return (
    <section>
      <PageHeader title={t("guides.title")} subtitle={t("guides.subtitle")} />

      <p style={{ color: brandTokens.colors.textSecondary, fontSize: 13, margin: "0 0 16px" }}>{pick(FRAMEWORK_SOURCE)}</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 20 }}>
        {counts.map(({ status, n }) => (
          <KpiCard key={status} label={t(`guides.statuses.${status}`)} value={n} hint={t(`guides.statusHints.${status}`)} />
        ))}
      </div>

      <div style={{ background: brandTokens.colors.surface, borderRadius: brandTokens.radius.lg, boxShadow: brandTokens.shadow.card,
                    border: `1px solid ${brandTokens.colors.border}`, overflow: "hidden", marginBottom: 24 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: brandTokens.colors.surfaceSoft, textAlign: "left" }}>
              <th style={{ ...head, width: 40 }}>§</th>
              <th style={{ ...head, width: 200 }}>{t("guides.columns.domain")}</th>
              <th style={{ ...head, width: 120 }}>{t("guides.columns.status")}</th>
              <th style={head}>{t("guides.columns.applied")}</th>
              <th style={head}>{t("guides.columns.pending")}</th>
            </tr>
          </thead>
          <tbody>
            {FRAMEWORK_ROWS.map((row) => (
              <tr key={row.section} style={{ borderTop: `1px solid ${brandTokens.colors.border}` }}>
                <td style={{ ...cell, color: brandTokens.colors.textSecondary, fontWeight: 600 }}>{row.section}</td>
                <td style={{ ...cell, fontWeight: 500 }}>{pick(row.title)}</td>
                <td style={cell}><StatusChip status={row.status} /></td>
                <td style={cell}>{pick(row.applied)}</td>
                <td style={{ ...cell, color: brandTokens.colors.textSecondary }}>{pick(row.pending)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 style={{ fontSize: 18, fontWeight: 600, margin: "0 0 10px" }}>{t("guides.recommendations")}</h2>
      <ol style={{ margin: 0, paddingLeft: 22, display: "grid", gap: 8, fontSize: 14, lineHeight: 1.5, maxWidth: 960 }}>
        {RECOMMENDATIONS.map((rec, i) => (
          <li key={i}>{pick(rec)}</li>
        ))}
      </ol>
    </section>
  );
}
