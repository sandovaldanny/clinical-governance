import { brandTokens } from "../theme/brand-tokens";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
};

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <header style={{ marginBottom: 28 }}>
      <h1 style={{ fontSize: 28, fontWeight: 500, color: brandTokens.colors.textPrimary }}>{title}</h1>
      {subtitle && (
        <p style={{ margin: "8px 0 0", fontSize: 14, color: brandTokens.colors.textSecondary, maxWidth: 760 }}>
          {subtitle}
        </p>
      )}
    </header>
  );
}
