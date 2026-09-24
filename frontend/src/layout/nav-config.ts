/** Navegación alineada a M01/M02 (admin) y M04/M05 (gobierno clínico) del requerimiento funcional. */

export type NavItem = {
  label: string;
  path: string;
};

export type NavGroup = {
  title: string;
  items: NavItem[];
};

export const NAV_GROUPS: NavGroup[] = [
  {
    title: "Gobierno clínico",
    items: [
      { label: "UCCA — Ciclos", path: "/ucca" },
      { label: "Indicadores a evaluar", path: "/indicators" },
    ],
  },
  {
    title: "Administración (M01–M02)",
    items: [
      { label: "Usuarios", path: "/admin/users" },
      { label: "Centros médicos", path: "/admin/facilities" },
      { label: "Profesiones", path: "/admin/professions" },
      { label: "Especialidades", path: "/admin/specialties" },
      { label: "Roles AEGIS", path: "/admin/roles" },
      { label: "Profesionales", path: "/admin/professionals" },
    ],
  },
];
