import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../theme/brand-tokens";
import { NAV_GROUPS } from "./nav-config";

const linkStyle = ({ isActive }: { isActive: boolean }) => ({
  display: "block",
  padding: "10px 14px",
  borderRadius: brandTokens.radius.md,
  fontSize: 14,
  fontWeight: isActive ? 600 : 400,
  color: brandTokens.colors.textPrimary,
  background: isActive ? brandTokens.colors.accentSoft : "transparent",
  borderLeft: `3px solid ${isActive ? brandTokens.colors.accent : "transparent"}`,
  textDecoration: "none",
  transition: "background .15s",
});

export function Sidebar() {
  const { t } = useTranslation();

  return (
    <aside
      style={{
        width: 264,
        flexShrink: 0,
        background: brandTokens.colors.surface,
        borderRight: `1px solid ${brandTokens.colors.border}`,
        padding: "28px 16px",
        overflowY: "auto",
      }}
    >
      {NAV_GROUPS.map((group) => (
        <div key={group.titleKey} style={{ marginBottom: 32 }}>
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: brandTokens.colors.textSecondary,
              padding: "0 14px 10px",
              margin: 0,
            }}
          >
            {t(group.titleKey)}
          </p>
          <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {group.items.map((item) => (
              <NavLink key={item.path} to={item.path} style={linkStyle} end={item.path === "/ucca"}>
                {t(item.labelKey)}
              </NavLink>
            ))}
          </nav>
        </div>
      ))}
    </aside>
  );
}
