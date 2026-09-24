/** Navegación: Administración (M01/M02) primero, luego Gobierno clínico (M04/M05). Etiquetas vía i18n. */

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
      { labelKey: "nav.roles", path: "/admin/roles" },
    ],
  },
  {
    titleKey: "nav.governance",
    items: [
      { labelKey: "nav.uccaCycles", path: "/ucca" },
      { labelKey: "nav.indicators", path: "/indicators" },
    ],
  },
];
