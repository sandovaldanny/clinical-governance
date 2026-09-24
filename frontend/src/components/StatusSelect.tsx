import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../theme/brand-tokens";

export type UserStatus = "active" | "inactive" | "suspended";
const STATUSES: UserStatus[] = ["active", "inactive", "suspended"];

const DOT: Record<UserStatus, string> = {
  active: alkalma.turquoise,
  inactive: alkalma.bluegray,
  suspended: alkalma.amber,
};

type StatusSelectProps = {
  value: UserStatus;
  onChange: (next: UserStatus) => void;
  disabled?: boolean;
  label: string;
};

/** Selector compacto de estado (Activo / Inactivo / Suspendido) con punto de color. */
export function StatusSelect({ value, onChange, disabled, label }: StatusSelectProps) {
  const { t } = useTranslation();
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      <span aria-hidden style={{ width: 8, height: 8, borderRadius: "50%", background: DOT[value] }} />
      <select
        aria-label={label}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value as UserStatus)}
        style={{
          width: "auto",
          padding: "4px 26px 4px 8px",
          fontSize: 13,
          borderRadius: 999,
          border: `1px solid ${brandTokens.colors.border}`,
          background: brandTokens.colors.surface,
          color: value === "active" ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary,
        }}
      >
        {STATUSES.map((s) => (
          <option key={s} value={s}>
            {t(`app.status.${s}`)}
          </option>
        ))}
      </select>
    </span>
  );
}
