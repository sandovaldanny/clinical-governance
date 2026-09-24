/** Navegación alineada a M01/M02 (admin) y M04/M05 (gobierno clínico). Etiquetas vía i18n. */

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
    titleKey: "nav.governance",
    items: [
      { labelKey: "nav.uccaCycles", path: "/ucca" },
      { labelKey: "nav.indicators", path: "/indicators" },
    ],
  },
  {
    titleKey: "nav.admin",
    items: [
      { labelKey: "nav.users", path: "/admin/users" },
      { labelKey: "nav.facilities", path: "/admin/facilities" },
      { labelKey: "nav.professions", path: "/admin/professions" },
      { labelKey: "nav.specialties", path: "/admin/specialties" },
      { labelKey: "nav.roles", path: "/admin/roles" },
    ],
  },
];
