import { brandTokens } from "../theme/brand-tokens";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
};

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <header style={{ marginBottom: 20 }}>
      <h1 style={{ fontSize: 22, margin: 0, color: brandTokens.colors.textPrimary }}>{title}</h1>
      {subtitle && (
        <p style={{ margin: "6px 0 0", fontSize: 14, color: brandTokens.colors.textSecondary }}>
          {subtitle}
        </p>
      )}
    </header>
  );
}
