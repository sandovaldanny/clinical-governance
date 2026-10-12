import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import { outcomeFor } from "../scoring";

const COLOR: Record<string, string> = {
  compliant: alkalma.turquoise, minor_improvement: alkalma.amber, improvement_required: "#D98B2B",
  priority_corrective_action: brandTokens.colors.danger,
};

/** Barras horizontales 0–100 %; color según banda de outcome del valor. Sin librerías. */
export function RateBars({ items }: { items: { label: string; value: number | null; hint?: string }[] }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {items.map((it) => {
        const outcome = outcomeFor(it.value);
        return (
          <div key={it.label} style={{ display: "grid", gridTemplateColumns: "72px 1fr 64px", alignItems: "center", gap: 10, fontSize: 13 }}>
            <span style={{ fontWeight: 600 }}>{it.label}</span>
            <div style={{ background: alkalma.bgSoft, borderRadius: 999, height: 12, overflow: "hidden" }} title={it.hint}>
              <div style={{ width: `${it.value ?? 0}%`, height: "100%", background: outcome ? COLOR[outcome] : alkalma.bluegray, transition: "width .2s" }} />
            </div>
            <span style={{ textAlign: "right", color: brandTokens.colors.textSecondary }}>{it.value === null ? "—" : `${it.value} %`}</span>
          </div>
        );
      })}
    </div>
  );
}
