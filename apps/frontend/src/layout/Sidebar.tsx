import { NavLink } from "react-router-dom";

import { brandTokens } from "../theme/brand-tokens";
import { NAV_GROUPS } from "./nav-config";

const linkStyle = ({ isActive }: { isActive: boolean }) => ({
  display: "block",
  padding: "8px 16px",
  borderRadius: 6,
  fontSize: 14,
  color: isActive ? brandTokens.colors.primary : brandTokens.colors.textPrimary,
  background: isActive ? "#E6F2F0" : "transparent",
  textDecoration: "none",
  fontWeight: isActive ? 600 : 400,
});

export function Sidebar() {
  return (
    <aside
      style={{
        width: 260,
        flexShrink: 0,
        background: brandTokens.colors.surface,
        borderRight: "1px solid #E2E8EC",
        padding: "16px 12px",
        overflowY: "auto",
      }}
    >
      {NAV_GROUPS.map((group) => (
        <div key={group.title} style={{ marginBottom: 24 }}>
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: brandTokens.colors.textSecondary,
              padding: "0 8px 8px",
              margin: 0,
            }}
          >
            {group.title}
          </p>
          <nav style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {group.items.map((item) => (
              <NavLink key={item.path} to={item.path} style={linkStyle} end={item.path === "/ucca"}>
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      ))}
    </aside>
  );
}
