import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";
import { brandTokens } from "../../theme/brand-tokens";

type Catalog = { id: string; code: string; label: string; catalog_type: string };

function SectionTitle({ children }: { children: string }) {
  return <h2 style={{ fontSize: 18, margin: "36px 0 14px" }}>{children}</h2>;
}

/** Gobierno clínico → Indicadores a evaluar. Catálogos regulatorios M05 (JAWDA/OMH001) en solo
 * lectura. Los criterios UCCA se administran en Administración → Criterios de evaluación. */
export function IndicatorsPage() {
  const { t } = useTranslation();
  const omh001 = useApiList<Catalog>("/identity/catalogs?catalog_type=omh001_investigation");
  const medication = useApiList<Catalog>("/identity/catalogs?catalog_type=medication_class");

  const loading = omh001.loading || medication.loading;

  return (
    <section>
      <PageHeader title={t("indicators.title")} subtitle={t("indicators.subtitle")} />

      <SectionTitle>{t("indicators.omhTitle")}</SectionTitle>
      {omh001.loading && <p>{t("app.loading")}</p>}
      {omh001.error && <p>{omh001.error}</p>}
      {!omh001.loading && !omh001.error && (
        <DataTable
          rows={omh001.data}
          emptyMessage={t("indicators.omhEmpty")}
          columns={[
            { key: "code", header: t("indicators.code"), render: (r) => <code>{r.code}</code> },
            { key: "label", header: t("indicators.investigation"), render: (r) => r.label },
          ]}
        />
      )}

      <SectionTitle>{t("indicators.medTitle")}</SectionTitle>
      {medication.loading && <p>{t("app.loading")}</p>}
      {medication.error && <p>{medication.error}</p>}
      {!medication.loading && !medication.error && (
        <DataTable
          rows={medication.data}
          emptyMessage={t("indicators.medEmpty")}
          columns={[
            { key: "code", header: t("indicators.code"), render: (r) => <code>{r.code}</code> },
            { key: "label", header: t("indicators.medClass"), render: (r) => r.label },
          ]}
        />
      )}

      {loading && <p style={{ marginTop: 16, color: brandTokens.colors.textSecondary }}>{t("app.refreshing")}</p>}
    </section>
  );
}
