/** Navegación: Administración, Gobierno clínico, Dashboard y Documentación. Etiquetas vía i18n. */

export type NavItem = {
  labelKey: string;
  path: string;
};

export type NavGroup = {
  titleKey: string;
  items: NavItem[];
};

export const NAV_GROUPS: NavGroup[] = [
  {
    titleKey: "nav.admin",
    items: [
      { labelKey: "nav.users", path: "/admin/users" },
      { labelKey: "nav.positions", path: "/admin/positions" },
      { labelKey: "nav.facilities", path: "/admin/facilities" },
      { labelKey: "nav.professions", path: "/admin/professions" },
      { labelKey: "nav.specialties", path: "/admin/specialties" },
      { labelKey: "nav.criteria", path: "/admin/criteria" },
      { labelKey: "nav.roles", path: "/admin/roles" },
    ],
  },
  {
    titleKey: "nav.governance",
    items: [
      { labelKey: "nav.uccaCycles", path: "/ucca" },
      { labelKey: "nav.aegis", path: "/aegis" },
    ],
  },
  {
    titleKey: "nav.dashboard",
    items: [{ labelKey: "nav.uccaDashboard", path: "/ucca/dashboard" }],
  },
  {
    titleKey: "nav.documentation",
    items: [
      { labelKey: "nav.indicators", path: "/indicators" },
      { labelKey: "nav.guides", path: "/guides" },
    ],
  },
];
