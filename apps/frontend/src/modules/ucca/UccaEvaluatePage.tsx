import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, apiPostJson } from "../../api/client";
import { brandTokens } from "../../theme/brand-tokens";
import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { useApiList } from "../../hooks/useApiList";
import { useAuth } from "../../auth/AuthContext";

type Cycle = { id: string; facility_id: string; period_label: string; status: string };
type Criterion = { id: string; code: string; description: string; severity: string };
type Professional = {
  id: string;
  full_name: string;
  profession_name: string;
  primary_facility_id: string;
};
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

const OUTCOMES = [
  { value: "compliant", label: "Cumple" },
  { value: "non_compliant", label: "No cumple" },
  { value: "not_applicable", label: "No aplica" },
];

const PHYSICIAN_PROFESSIONS = new Set(["Physician", "Psychiatrist"]);

export function UccaEvaluatePage() {
  const { cycleId } = useParams<{ cycleId: string }>();
  const { session } = useAuth();

  const cycles = useApiList<Cycle>("/ucca/cycles");
  const criteria = useApiList<Criterion>("/ucca/criteria");
  const professionals = useApiList<Professional>("/identity/professionals");
  const facilities = useApiList<Facility>("/identity/facilities");
  const results = useApiList<ResultRow>(`/ucca/results?cycle_id=${cycleId ?? ""}`);

  const cycle = cycles.data.find((c) => c.id === cycleId);
  const facilityName = facilities.data.find((f) => f.id === cycle?.facility_id)?.name ?? "—";

  const physiciansAtCenter = useMemo(
    () =>
      professionals.data.filter(
        (p) =>
          p.primary_facility_id === cycle?.facility_id &&
          PHYSICIAN_PROFESSIONS.has(p.profession_name),
      ),
    [professionals.data, cycle?.facility_id],
  );

  const [criterionId, setCriterionId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [outcome, setOutcome] = useState("compliant");
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
    if (!professionalId && physiciansAtCenter.length > 0) {
      setProfessionalId(physiciansAtCenter[0].id);
    }
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
      setMessage(`Evaluación registrada para ${selectedCriterion?.code ?? "criterio"}.`);
      setEvidence("");
      setNaReason("");
      results.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No fue posible registrar la evaluación.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!cycleId) return <p>Ciclo no especificado.</p>;
  if (cycles.loading) return <p>Cargando ciclo…</p>;
  if (!cycle) return <p>Ciclo no encontrado.</p>;

  return (
    <section>
      <PageHeader
        title={`Evaluar criterios — ${cycle.period_label}`}
        subtitle={`Centro: ${facilityName} · M04 UCCA — registrar cumplimiento por profesional y criterio (DOC-001, DOC-002, …)`}
      />

      <p style={{ marginBottom: 16 }}>
        <Link to="/ucca" style={{ color: brandTokens.colors.primary }}>
          ← Volver a ciclos
        </Link>
      </p>

      <div
        style={{
          background: brandTokens.colors.surface,
          padding: 20,
          borderRadius: 8,
          boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
          marginBottom: 28,
        }}
      >
        <h2 style={{ fontSize: 16, marginTop: 0 }}>Registrar evaluación</h2>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 14, maxWidth: 560 }}>
          <label style={{ display: "grid", gap: 4, fontSize: 14 }}>
            Criterio / indicador
            <select
              value={criterionId}
              onChange={(e) => setCriterionId(e.target.value)}
              required
              style={{ padding: 8 }}
            >
              {criteria.data.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} — {c.description}
                </option>
              ))}
            </select>
          </label>

          <label style={{ display: "grid", gap: 4, fontSize: 14 }}>
            Profesional (médicos del centro)
            <select
              value={professionalId}
              onChange={(e) => setProfessionalId(e.target.value)}
              required
              style={{ padding: 8 }}
            >
              {physiciansAtCenter.length === 0 && (
                <option value="">No hay médicos en este centro</option>
              )}
              {physiciansAtCenter.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.full_name} ({p.profession_name})
                </option>
              ))}
            </select>
          </label>

          <label style={{ display: "grid", gap: 4, fontSize: 14 }}>
            Resultado
            <select value={outcome} onChange={(e) => setOutcome(e.target.value)} style={{ padding: 8 }}>
              {OUTCOMES.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>

          {outcome === "not_applicable" && (
            <label style={{ display: "grid", gap: 4, fontSize: 14 }}>
              Razón de &quot;No aplica&quot; (obligatorio)
              <textarea
                value={naReason}
                onChange={(e) => setNaReason(e.target.value)}
                required
                rows={2}
                style={{ padding: 8 }}
              />
            </label>
          )}

          <label style={{ display: "grid", gap: 4, fontSize: 14 }}>
            Referencia de evidencia (opcional)
            <input
              type="text"
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              placeholder="Ej. expediente #12345, nota clínica del 2026-08-01"
              style={{ padding: 8 }}
            />
          </label>

          <button
            type="submit"
            disabled={submitting || physiciansAtCenter.length === 0}
            style={{
              padding: "10px 16px",
              background: brandTokens.colors.primary,
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            {submitting ? "Guardando…" : "Registrar evaluación"}
          </button>
        </form>

        {message && <p style={{ color: brandTokens.colors.success }}>{message}</p>}
        {error && <p style={{ color: brandTokens.colors.danger }}>{error}</p>}
      </div>

      <h2 style={{ fontSize: 16 }}>Evaluaciones registradas en este ciclo</h2>
      {results.loading && <p>Cargando resultados…</p>}
      {results.error && <p>{results.error}</p>}
      {!results.loading && !results.error && (
        <DataTable
          rows={results.data}
          emptyMessage="Aún no hay evaluaciones en este ciclo."
          columns={[
            { key: "code", header: "Criterio", render: (r) => r.criterion_code },
            { key: "pro", header: "Profesional", render: (r) => r.professional_name },
            {
              key: "out",
              header: "Resultado",
              render: (r) =>
                r.outcome === "compliant"
                  ? "Cumple"
                  : r.outcome === "non_compliant"
                    ? "No cumple"
                    : "No aplica",
            },
            { key: "status", header: "Estado", render: (r) => r.status },
            { key: "ev", header: "Evidencia", render: (r) => r.evidence_reference ?? "—" },
          ]}
        />
      )}
    </section>
  );
}
