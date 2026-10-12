import { useTranslation } from "react-i18next";

import { PageHeader } from "../../components/PageHeader";

/** Gobierno clínico → AEGIS. Marcador de posición: módulo aún sin contenido. */
export function AegisPage() {
  const { t } = useTranslation();
  return (
    <section>
      <PageHeader title={t("aegis.title")} subtitle={t("aegis.subtitle")} />
    </section>
  );
}
