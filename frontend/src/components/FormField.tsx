import type { ReactNode } from "react";

import { brandTokens } from "../theme/brand-tokens";

type FormFieldProps = {
  label: string;
  required?: boolean;
  hint?: string;
  error?: string | null;
  children: ReactNode;
};

/** Etiqueta + control + ayuda/error. El control se pasa como hijo (input/select/textarea). */
export function FormField({ label, required, hint, error, children }: FormFieldProps) {
  return (
    <label style={{ display: "grid", gap: 6, fontSize: 13, fontWeight: 500, marginBottom: 16 }}>
      <span>
        {label}
        {required && <span aria-hidden style={{ color: brandTokens.colors.accent, marginLeft: 4 }}>*</span>}
      </span>
      {children}
      {hint && !error && (
        <span style={{ fontSize: 12, fontWeight: 400, color: brandTokens.colors.textSecondary }}>{hint}</span>
      )}
      {error && (
        <span role="alert" style={{ fontSize: 12, fontWeight: 400, color: brandTokens.colors.danger }}>
          {error}
        </span>
      )}
    </label>
  );
}

export type Option = { value: string; label: string; hint?: string };

type CheckboxGroupProps = {
  label: string;
  required?: boolean;
  options: Option[];
  value: string[];
  onChange: (next: string[]) => void;
  error?: string | null;
  columns?: number;
};

/** Selección múltiple (centros, roles, permisos) como lista de casillas con fondo suave. */
export function CheckboxGroup({ label, required, options, value, onChange, error, columns = 1 }: CheckboxGroupProps) {
  function toggle(v: string) {
    onChange(value.includes(v) ? value.filter((x) => x !== v) : [...value, v]);
  }
  return (
    <fieldset style={{ border: "none", padding: 0, margin: "0 0 16px" }}>
      <legend style={{ fontSize: 13, fontWeight: 500, marginBottom: 6, padding: 0 }}>
        {label}
        {required && <span aria-hidden style={{ color: brandTokens.colors.accent, marginLeft: 4 }}>*</span>}
      </legend>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
          gap: 6,
          background: brandTokens.colors.surfaceSoft,
          borderRadius: brandTokens.radius.md,
          padding: 10,
        }}
      >
        {options.map((opt) => (
          <label
            key={opt.value}
            style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 13, fontWeight: 400, cursor: "pointer" }}
          >
            <input
              type="checkbox"
              checked={value.includes(opt.value)}
              onChange={() => toggle(opt.value)}
              style={{ width: "auto", margin: "3px 0 0", accentColor: brandTokens.colors.primary }}
            />
            <span>
              {opt.label}
              {opt.hint && (
                <span style={{ display: "block", fontSize: 11, color: brandTokens.colors.textSecondary }}>{opt.hint}</span>
              )}
            </span>
          </label>
        ))}
        {options.length === 0 && (
          <span style={{ fontSize: 12, color: brandTokens.colors.textSecondary }}>—</span>
        )}
      </div>
      {error && (
        <span role="alert" style={{ display: "block", marginTop: 6, fontSize: 12, color: brandTokens.colors.danger }}>
          {error}
        </span>
      )}
    </fieldset>
  );
}
