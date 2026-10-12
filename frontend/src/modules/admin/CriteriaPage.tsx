import { MasterDataPage } from "../../components/MasterDataPage";
import { brandTokens } from "../../theme/brand-tokens";

type Criterion = {
  id: string;
  code: string;
  domain: string;
  universal_question: string;
  profession_interpretation: string;
  examples_evidence: string;
  is_active: boolean;
};

/** Texto largo recortado a 2 líneas; el texto completo va en el tooltip. Evita que la tabla
 * crezca o necesite scroll horizontal. */
function Clamped({ text, muted }: { text: string; muted?: boolean }) {
  return (
    <span
      title={text}
      style={{
        display: "-webkit-box",
        WebkitLineClamp: 3,
        WebkitBoxOrient: "vertical",
        overflow: "hidden",
        fontSize: 13,
        lineHeight: 1.4,
        color: muted ? brandTokens.colors.textSecondary : undefined,
      }}
    >
      {text || "—"}
    </span>
  );
}

/** Administración → Criterios de evaluación (plantilla UCCA vigente). Mismo patrón que cargos,
 * profesiones y especialidades: tabla + drawer crear/editar + activar/inactivar. */
export function CriteriaPage() {
  return (
    <MasterDataPage<Criterion>
      titleKey="admin.criteria.title"
      subtitleKey="admin.criteria.subtitle"
      emptyKey="admin.criteria.empty"
      newKey="admin.criteria.new"
      editKey="admin.criteria.edit"
      listPath="/ucca/criteria"
      writePath="/ucca/criteria"
      managePermission="catalogs.manage"
      fields={[
        { key: "code", labelKey: "admin.criteria.code", type: "text", required: true, createOnly: true, hintKey: "admin.criteria.codeHint" },
        { key: "domain", labelKey: "admin.criteria.domain", type: "text", required: true },
        { key: "universal_question", labelKey: "admin.criteria.universalQuestion", type: "textarea", required: true, hintKey: "admin.criteria.universalQuestionHint" },
        { key: "profession_interpretation", labelKey: "admin.criteria.professionInterpretation", type: "textarea", hintKey: "admin.criteria.professionInterpretationHint" },
        { key: "examples_evidence", labelKey: "admin.criteria.examplesEvidence", type: "textarea", hintKey: "admin.criteria.examplesEvidenceHint" },
      ]}
      columns={[
        { key: "code", headerKey: "admin.criteria.code", width: 64, render: (r) => <code>{r.code}</code> },
        { key: "domain", headerKey: "admin.criteria.domain", width: 150, render: (r) => <strong style={{ fontWeight: 500, fontSize: 13 }}>{r.domain}</strong> },
        { key: "question", headerKey: "admin.criteria.universalQuestion", width: "22%", render: (r) => <Clamped text={r.universal_question} /> },
        { key: "interpretation", headerKey: "admin.criteria.professionInterpretation", width: "22%", render: (r) => <Clamped text={r.profession_interpretation} muted /> },
        { key: "evidence", headerKey: "admin.criteria.examplesEvidence", width: "22%", render: (r) => <Clamped text={r.examples_evidence} muted /> },
      ]}
      status={{ kind: "toggle", field: "is_active" }}
      rowLabel={(r) => `${r.code} — ${r.domain}`}
    />
  );
}
