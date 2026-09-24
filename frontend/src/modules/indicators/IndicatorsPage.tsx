import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { useApiList } from "../../hooks/useApiList";
import { brandTokens } from "../../theme/brand-tokens";

type Criterion = { id: string; code: string; description: string; severity: string };
type Catalog = { id: string; code: string; label: string; catalog_type: string };

function SectionTitle({ children }: { children: string }) {
  return <h2 style={{ fontSize: 18, margin: "36px 0 14px" }}>{children}</h2>;
}

export function IndicatorsPage() {
  const { t } = useTranslation();
  const ucca = useApiList<Criterion>("/ucca/criteria");
  const omh001 = useApiList<Catalog>("/identity/catalogs?catalog_type=omh001_investigation");
  const medication = useApiList<Catalog>("/identity/catalogs?catalog_type=medication_class");

  const loading = ucca.loading || omh001.loading || medication.loading;

  return (
    <section>
      <PageHeader title={t("indicators.title")} subtitle={t("indicators.subtitle")} />

      <SectionTitle>{t("indicators.uccaTitle")}</SectionTitle>
      {ucca.loading && <p>{t("indicators.uccaLoading")}</p>}
      {ucca.error && <p>{ucca.error}</p>}
      {!ucca.loading && !ucca.error && (
        <DataTable
          rows={ucca.data}
          emptyMessage={t("indicators.uccaEmpty")}
          columns={[
            { key: "code", header: t("indicators.code"), render: (r) => <code>{r.code}</code> },
            { key: "desc", header: t("indicators.criterion"), render: (r) => r.description },
            { key: "sev", header: t("indicators.severity"), render: (r) => <StatusBadge code={r.severity} ns="indicators.severities" /> },
          ]}
        />
      )}

      <SectionTitle>{t("indicators.omhTitle")}</SectionTitle>
      {omh001.loading && <p>{t("app.loading")}</p>}
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
