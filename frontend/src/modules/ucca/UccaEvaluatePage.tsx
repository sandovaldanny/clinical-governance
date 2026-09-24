import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ApiError, apiPostJson } from "../../api/client";
import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { useApiList } from "../../hooks/useApiList";
import { useAuth } from "../../auth/AuthContext";
import { brandTokens } from "../../theme/brand-tokens";

type Cycle = { id: string; facility_id: string; period_label: string; status: string };
type Criterion = { id: string; code: string; description: string; severity: string };
type Professional = { id: string; full_name: string; profession_name: string; primary_facility_id: string };
type Facility = { id: string; name: string };
type ResultRow = {
  id: string;
  criterion_code: string;
  criterion_description: string;
  professional_name: string;
  outcome: string;
  status: string;
  evidence_reference: string | null;
};

const OUTCOMES = ["compliant", "non_compliant", "not_applicable"] as const;
const PHYSICIAN_PROFESSIONS = new Set(["Physician", "Psychiatrist"]);

const fieldLabel: React.CSSProperties = { display: "grid", gap: 6, fontSize: 13, fontWeight: 500 };

export function UccaEvaluatePage() {
  const { t } = useTranslation();
  const { cycleId } = useParams<{ cycleId: string }>();
  const { session } = useAuth();

  const cycles = useApiList<Cycle>("/ucca/cycles");
  const criteria = useApiList<Criterion>("/ucca/criteria");
  const professionals = useApiList<Professional>("/identity/professionals");
  const facilities = useApiList<Facility>("/identity/facilities");
  const results = useApiList<ResultRow>(`/ucca/results?cycle_id=${cycleId ?? ""}`);

  const cycle = cycles.data.find((c) => c.id === cycleId);
  const facilityName = facilities.data.find((f) => f.id === cycle?.facility_id)?.name ?? t("app.none");

  const physiciansAtCenter = useMemo(
    () =>
      professionals.data.filter(
        (p) => p.primary_facility_id === cycle?.facility_id && PHYSICIAN_PROFESSIONS.has(p.profession_name),
      ),
    [professionals.data, cycle?.facility_id],
  );

  const [criterionId, setCriterionId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [outcome, setOutcome] = useState<string>("compliant");
  const [evidence, setEvidence] = useState("");
  const [naReason, setNaReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!criterionId && criteria.data.length > 0) {
      const doc001 = criteria.data.find((c) => c.code === "DOC-001");
      setCriterionId(doc001?.id ?? criteria.data[0].id);
    }
  }, [criteria.data, criterionId]);

  useEffect(() => {
    if (!professionalId && physiciansAtCenter.length > 0) setProfessionalId(physiciansAtCenter[0].id);
  }, [physiciansAtCenter, professionalId]);

  const selectedCriterion = criteria.data.find((c) => c.id === criterionId);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!cycleId || !criterionId || !professionalId) return;

    setSubmitting(true);
    setError(null);
    setMessage(null);
    try {
      await apiPostJson(
        "/ucca/results",
        {
          cycle_id: cycleId,
          criterion_id: criterionId,
          professional_id: professionalId,
          outcome,
          evidence_reference: evidence || null,
          not_applicable_reason: outcome === "not_applicable" ? naReason : null,
        },
        session?.token,
      );
      setMessage(t("ucca.saved", { code: selectedCriterion?.code ?? "" }));
      setEvidence("");
      setNaReason("");
      results.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ucca.saveError"));
    } finally {
      setSubmitting(false);
    }
  }

  if (!cycleId) return <p>{t("ucca.cycleMissing")}</p>;
  if (cycles.loading) return <p>{t("ucca.loadingCycles")}</p>;
  if (!cycle) return <p>{t("ucca.cycleNotFound")}</p>;

  return (
    <section>
      <p style={{ margin: "0 0 18px" }}>
        <Link to="/ucca" style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 500 }}>
          ← {t("ucca.back")}
        </Link>
      </p>

      <PageHeader
        title={t("ucca.evaluateTitle", { period: cycle.period_label })}
        subtitle={t("ucca.evaluateSubtitle", { facility: facilityName })}
      />

      <div
        style={{
          background: brandTokens.colors.surface,
          padding: 32,
          borderRadius: brandTokens.radius.lg,
          boxShadow: brandTokens.shadow.card,
          border: `1px solid ${brandTokens.colors.border}`,
          marginBottom: 40,
        }}
      >
        <h2 style={{ fontSize: 18, marginBottom: 20 }}>{t("ucca.formTitle")}</h2>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 18, maxWidth: 600 }}>
          <label style={fieldLabel}>
            {t("ucca.criterion")}
            <select value={criterionId} onChange={(e) => setCriterionId(e.target.value)} required>
              {criteria.data.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} — {c.description}
                </option>
              ))}
            </select>
          </label>

          <label style={fieldLabel}>
            {t("ucca.professional")}
            <select value={professionalId} onChange={(e) => setProfessionalId(e.target.value)} required>
              {physiciansAtCenter.length === 0 && <option value="">{t("ucca.noPhysicians")}</option>}
              {physiciansAtCenter.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.full_name} ({p.profession_name})
                </option>
              ))}
            </select>
          </label>

          <label style={fieldLabel}>
            {t("ucca.outcome")}
            <select value={outcome} onChange={(e) => setOutcome(e.target.value)}>
              {OUTCOMES.map((o) => (
                <option key={o} value={o}>
                  {t(`ucca.outcomes.${o}`)}
                </option>
              ))}
            </select>
          </label>

          {outcome === "not_applicable" && (
            <label style={fieldLabel}>
              {t("ucca.naReason")}
              <textarea value={naReason} onChange={(e) => setNaReason(e.target.value)} required rows={2} />
            </label>
          )}

          <label style={fieldLabel}>
            {t("ucca.evidence")}
            <input
              type="text"
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              placeholder={t("ucca.evidencePlaceholder")}
            />
          </label>

          <div>
            <button type="submit" className="btn-primary" disabled={submitting || physiciansAtCenter.length === 0}>
              {submitting ? t("ucca.saving") : t("ucca.submit")}
            </button>
          </div>
        </form>

        {message && <p role="status" style={{ color: brandTokens.colors.success, marginTop: 16 }}>{message}</p>}
        {error && <p role="alert" style={{ color: brandTokens.colors.danger, marginTop: 16 }}>{error}</p>}
      </div>

      <h2 style={{ fontSize: 18, marginBottom: 14 }}>{t("ucca.resultsTitle")}</h2>
      {results.loading && <p>{t("ucca.loadingResults")}</p>}
      {results.error && <p>{results.error}</p>}
      {!results.loading && !results.error && (
        <DataTable
          rows={results.data}
          emptyMessage={t("ucca.resultsEmpty")}
          columns={[
            { key: "code", header: t("ucca.colCriterion"), render: (r) => <code>{r.criterion_code}</code> },
            { key: "pro", header: t("ucca.colProfessional"), render: (r) => r.professional_name },
            { key: "out", header: t("ucca.colOutcome"), render: (r) => <StatusBadge code={r.outcome} ns="ucca.outcomes" /> },
            { key: "status", header: t("ucca.colStatus"), render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            { key: "ev", header: t("ucca.colEvidence"), render: (r) => r.evidence_reference ?? t("app.none") },
          ]}
        />
      )}
    </section>
  );
}
