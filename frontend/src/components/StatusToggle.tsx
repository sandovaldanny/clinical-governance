import { brandTokens } from "../theme/brand-tokens";

type StatusToggleProps = {
  checked: boolean;
  label: string;
  disabled?: boolean;
  onChange: (next: boolean) => void;
};

/** Switch discreto (pill 34×18) para activar/desactivar. Turquoise = activo, Blue Gray = inactivo. */
export function StatusToggle({ checked, label, disabled, onChange }: StatusToggleProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      style={{
        width: 34,
        height: 18,
        borderRadius: 999,
        border: "none",
        padding: 2,
        background: checked ? brandTokens.colors.accent : brandTokens.colors.textSecondary,
        opacity: disabled ? 0.5 : 1,
        transition: "background .15s",
        display: "inline-flex",
        alignItems: "center",
        verticalAlign: "middle",
      }}
    >
      <span
        aria-hidden
        style={{
          width: 14,
          height: 14,
          borderRadius: "50%",
          background: "#fff",
          transform: checked ? "translateX(16px)" : "translateX(0)",
          transition: "transform .15s",
          boxShadow: "0 1px 2px rgba(22,69,92,0.25)",
        }}
      />
    </button>
  );
}
