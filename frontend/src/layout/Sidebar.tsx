import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../theme/brand-tokens";
import { NAV_GROUPS, type NavGroup } from "./nav-config";

const STORAGE_KEY = "aegis.sidebar.open";

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

/** `/ucca` cubre ciclos y auditorías (`/ucca/cycles/…`, `/ucca/audits/…`) pero no `/ucca/dashboard`,
 * que pertenece al bloque Dashboard. */
function itemMatches(path: string, pathname: string) {
  if (path === "/ucca") return pathname === "/ucca" || (pathname.startsWith("/ucca/") && !pathname.startsWith("/ucca/dashboard"));
  return pathname === path || pathname.startsWith(`${path}/`);
}

function groupContains(group: NavGroup, pathname: string) {
  return group.items.some((item) => itemMatches(item.path, pathname));
}

/** Estado inicial: lo guardado por el usuario; si no hay nada, solo el bloque de la ruta actual abierto. */
function initialOpen(pathname: string): Record<string, boolean> {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Record<string, boolean>;
  } catch {
    /* almacenamiento no disponible: se usa el valor por defecto */
  }
  return Object.fromEntries(NAV_GROUPS.map((g) => [g.titleKey, groupContains(g, pathname)]));
}

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ transform: open ? "rotate(90deg)" : "rotate(0deg)", transition: "transform .15s" }}
    >
      <polyline points="9 6 15 12 9 18" />
    </svg>
  );
}

function persist(next: Record<string, boolean>) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* sin persistencia */
  }
}

/** Barra lateral: tres bloques (Administración, Gobierno clínico, Dashboard) plegables. Cada título
 * abre/cierra sus accesos, incluido el bloque activo. Al navegar a una ruta cuyo bloque está cerrado,
 * ese bloque se abre. La preferencia se recuerda en el navegador. */
export function Sidebar() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const [open, setOpen] = useState<Record<string, boolean>>(() => initialOpen(pathname));

  // Al cambiar de ruta, abrir el bloque que la contiene (sin cerrar los demás).
  useEffect(() => {
    const owner = NAV_GROUPS.find((g) => groupContains(g, pathname));
    if (!owner) return;
    setOpen((prev) => {
      if (prev[owner.titleKey]) return prev;
      const next = { ...prev, [owner.titleKey]: true };
      persist(next);
      return next;
    });
  }, [pathname]);

  const toggle = (key: string) => {
    setOpen((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      persist(next);
      return next;
    });
  };

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
      {NAV_GROUPS.map((group) => {
        const active = groupContains(group, pathname);
        const isOpen = Boolean(open[group.titleKey]);
        const panelId = `nav-${group.titleKey.replace(/\W/g, "-")}`;
        return (
          <div key={group.titleKey} style={{ marginBottom: 20 }}>
            <button
              type="button"
              onClick={() => toggle(group.titleKey)}
              aria-expanded={isOpen}
              aria-controls={panelId}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 8,
                background: "transparent",
                border: 0,
                cursor: "pointer",
                fontFamily: "inherit",
                fontSize: 11,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: active ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary,
                padding: "8px 14px",
                borderRadius: brandTokens.radius.md,
                textAlign: "left",
              }}
            >
              <span>{t(group.titleKey)}</span>
              <Chevron open={isOpen} />
            </button>
            {isOpen && (
              <nav id={panelId} style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: 4 }}>
                {group.items.map((item) => (
                  <NavLink key={item.path} to={item.path} style={() => linkStyle({ isActive: itemMatches(item.path, pathname) })}>
                    {t(item.labelKey)}
                  </NavLink>
                ))}
              </nav>
            )}
          </div>
        );
      })}
    </aside>
  );
}
