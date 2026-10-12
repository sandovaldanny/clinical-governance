import { useTranslation } from "react-i18next";

import { PageHeader } from "../../components/PageHeader";

/** Dashboard → Resumen. Marcador de posición hasta definir los indicadores a mostrar. */
export function DashboardPage() {
  const { t } = useTranslation();
  return (
    <section>
      <PageHeader title={t("dashboard.title")} subtitle={t("dashboard.subtitle")} />
    </section>
  );
}
