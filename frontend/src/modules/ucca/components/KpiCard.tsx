import type { ReactNode } from "react";

import { brandTokens } from "../../../theme/brand-tokens";

export function KpiCard({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`,
                  borderRadius: brandTokens.radius.lg, boxShadow: brandTokens.shadow.card, padding: "16px 20px", minWidth: 0 }}>
      <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", color: brandTokens.colors.textSecondary }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 600, color: brandTokens.colors.textPrimary, marginTop: 6, lineHeight: 1.1 }}>{value}</div>
      {hint && <div style={{ fontSize: 12, color: brandTokens.colors.textSecondary, marginTop: 6 }}>{hint}</div>}
    </div>
  );
}
