import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import { brandTokens } from "../../theme/brand-tokens";
import { CriterionCard, type AnswerState } from "./components/CriterionCard";
import { EvaluationRules } from "./components/EvaluationRules";
import { EMPTY_FINDING, FindingSection, type FindingState } from "./components/FindingSection";
import { SaveNotice, type NoticeKind } from "./components/SaveNotice";
import { ScoreBar } from "./components/ScoreBar";
import { computeScore } from "./scoring";
import type { ActionStatus, AnswerValue, ChartAudit, ChartAuditWrite, Criterion, Cycle, Professional } from "./types";

type Owner = { id: string; full_name: string; status?: string };

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/** UCCA → Auditar expediente. Una pantalla: datos del expediente, 7 tarjetas (Yes / No / N/A),
 * barra fija con score/outcome en vivo (scoring.ts = scoring.py), hallazgo + acción correctiva.
 * Misma página para crear (`/ucca/cycles/:cycleId/audits/new`) y ver/editar (`/ucca/audits/:auditId`). */
export function ChartAuditPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { session } = useAuth();
  const me = useCurrentUser();
  const { cycleId: cycleParam, auditId } = useParams<{ cycleId?: string; auditId?: string }>();
  const isEdit = Boolean(auditId);

  const existing = useApiGet<ChartAudit>(auditId ? `/ucca/audits/${auditId}` : "");
  const cycleId = cycleParam ?? existing.data?.cycle_id ?? "";
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const cycle = cycles.data.find((c) => c.id === cycleId);
  const criteria = useApiList<Criterion>("/ucca/criteria?only_active=true");
  const professionals = useApiList<Professional>("/identity/professionals");
  const owners = useApiList<Owner>("/identity/users");

  const canCreate = me?.permissions.includes("ucca.create") ?? false;
  const canApprove = me?.permissions.includes("ucca.approve") ?? false;

  const [professionalId, setProfessionalId] = useState("");
  const [caseRef, setCaseRef] = useState("");
  const [auditDate, setAuditDate] = useState(today());
  const [notes, setNotes] = useState("");
  const [answers, setAnswers] = useState<Record<string, AnswerState>>({});
  const [finding, setFinding] = useState<FindingState>(EMPTY_FINDING);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ kind: NoticeKind; audit: ChartAudit } | null>(
    () => (location.state as { notice?: { kind: NoticeKind; audit: ChartAudit } } | null)?.notice ?? null,
  );
  const [saving, setSaving] = useState(false);
  const [showErrors, setShowErrors] = useState(false);

  // El aviso viaja en el history state al crear; se consume una vez para que reload/Back no lo repitan.
  useEffect(() => {
    if ((location.state as { notice?: unknown } | null)?.notice) {
      navigate(location.pathname, { replace: true, state: null });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Carga de una auditoría existente → estado del formulario.
  useEffect(() => {
    const a = existing.data;
    if (!a) return;
    setProfessionalId(a.professional_id);
    setCaseRef(a.case_reference);
    setAuditDate(a.audit_date);
    setNotes(a.notes);
    setAnswers(Object.fromEntries(a.answers.map((x) => [x.criterion_id, { outcome: x.outcome, reason: x.not_applicable_reason ?? "", comment: x.comment ?? "" }])));
    if (a.finding && a.finding.status !== "withdrawn") {
      const ca = a.finding.corrective_action && a.finding.corrective_action.status !== "cancelled" ? a.finding.corrective_action : null;
      setFinding({ enabled: true, description: a.finding.description, actionEnabled: Boolean(ca), actionDescription: ca?.description ?? "",
                   ownerId: ca?.responsible_user_id ?? "", dueDate: ca?.due_date ?? "", actionStatus: (ca?.status as ActionStatus | undefined) ?? "assigned",
                   closureEvidence: ca?.closure_evidence ?? "" });
    } else {
      setFinding(EMPTY_FINDING);
    }
  }, [existing.data]);

  const status = existing.data?.status ?? "draft";
  const readOnly = status !== "draft" || !canCreate;
  const professional = professionals.data.find((p) => p.id === professionalId);
  // En solo lectura (o sin permiso users.view) los datos del profesional vienen de la propia auditoría.
  const shown = {
    name: professional?.full_name ?? existing.data?.professional_name ?? "",
    employeeNumber: professional?.employee_number ?? existing.data?.employee_number ?? "",
    profession: professional?.profession_name ?? existing.data?.profession_name ?? "",
  };
  const facilityProfessionals = useMemo(
    () => professionals.data.filter((p) => p.primary_facility_id === cycle?.facility_id && p.is_active !== false),
    [professionals.data, cycle?.facility_id],
  );

  const answered = criteria.data.filter((c) => answers[c.id]?.outcome).length;
  const live = computeScore(criteria.data.map((c) => answers[c.id]?.outcome).filter((o): o is AnswerValue => Boolean(o)));
  const hasNo = criteria.data.some((c) => answers[c.id]?.outcome === "non_compliant");
  const findingRequired = live.outcome !== null && live.outcome !== "compliant" && hasNo;

  function validate(): string | null {
    const missing = criteria.data.length - answered;
    if (missing > 0) return t("ucca.form.missingAnswers", { count: missing });
    if (criteria.data.some((c) => answers[c.id]?.outcome === "not_applicable" && !answers[c.id].reason.trim())) return t("ucca.form.missingNaReason");
    if (findingRequired && !finding.description.trim()) return t("ucca.form.missingFinding");
    return null;
  }

  function payload(): ChartAuditWrite {
    const includeFinding = findingRequired || finding.enabled;
    return {
      professional_id: professionalId, case_reference: caseRef.trim(), audit_date: auditDate, notes,
      answers: criteria.data.map((c) => ({
        criterion_id: c.id, outcome: answers[c.id].outcome as AnswerValue,
        not_applicable_reason: answers[c.id].outcome === "not_applicable" ? answers[c.id].reason.trim() : null,
        comment: answers[c.id].comment.trim() || null,
      })),
      finding: includeFinding && finding.description.trim() ? {
        description: finding.description.trim(),
        corrective_action: finding.actionEnabled ? {
          description: finding.actionDescription.trim(), responsible_user_id: finding.ownerId, due_date: finding.dueDate,
          status: finding.actionStatus, closure_evidence: finding.closureEvidence.trim() || null,
        } : null,
      } : null,
    };
  }

  async function save(e?: FormEvent) {
    e?.preventDefault();
    setShowErrors(true);
    const problem = validate();
    if (problem) { setError(problem); return; }
    setSaving(true); setError(null); setNotice(null);
    try {
      const saved = isEdit
        ? await apiPatchJson<ChartAudit>(`/ucca/audits/${auditId}`, payload(), session?.token)
        : await apiPostJson<ChartAudit>(`/ucca/cycles/${cycleId}/audits`, payload(), session?.token);
      // Tras crear se navega al detalle: el aviso viaja en el estado de la ruta para sobrevivir al cambio.
      setNotice({ kind: "saved", audit: saved });
      if (!isEdit) navigate(`/ucca/audits/${saved.id}`, { replace: true, state: { notice: { kind: "saved", audit: saved } } });
      else existing.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ucca.form.saveError"));
    } finally { setSaving(false); }
  }

  async function transition(kind: "submit" | "approve") {
    if (!auditId) return;
    setSaving(true); setError(null); setNotice(null);
    try {
      const updated = await apiPostJson<ChartAudit>(`/ucca/audits/${auditId}/${kind}`, {}, session?.token);
      setNotice({ kind: kind === "submit" ? "submitted" : "approved", audit: updated });
      existing.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ucca.form.saveError"));
    } finally { setSaving(false); }
  }

  if (isEdit && existing.loading) return <p>{t("ucca.form.loading")}</p>;
  if (isEdit && !existing.loading && !existing.data) return <p>{t("ucca.form.notFound")}</p>;
  if (!cycleId) return <p>{t("ucca.cycleMissing")}</p>;

  return (
    <section>
      <p style={{ margin: "0 0 18px" }}>
        <Link to={`/ucca/cycles/${cycleId}`} style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 500 }}>← {t("ucca.backToCycle")}</Link>
      </p>
      <PageHeader title={isEdit ? t("ucca.form.editTitle", { mrn: existing.data?.case_reference ?? "" }) : t("ucca.form.newTitle")}
                  subtitle={`${cycle?.period_label ?? ""} · ${cycle?.facility_name ?? ""} — ${t("ucca.form.subtitle")}`} />
      {status === "approved" && <p role="status" style={{ color: brandTokens.colors.textSecondary, fontSize: 13 }}>{t("ucca.form.approvedNotice")}</p>}
      {status === "submitted" && <p role="status" style={{ color: brandTokens.colors.textSecondary, fontSize: 13 }}>{t("ucca.form.readOnly", { status: t("ucca.statuses.submitted") })}</p>}

      <form id="audit-form" onSubmit={save}>
        <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`, borderRadius: brandTokens.radius.lg, padding: 20 }}>
          <h2 style={{ fontSize: 17, margin: "0 0 14px" }}>{t("ucca.form.dataSection")}</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0 16px" }}>
            <FormField label={t("ucca.form.professional")} required>
              {readOnly ? (
                <input value={shown.name} readOnly />
              ) : (
                <select value={professionalId} required onChange={(e) => setProfessionalId(e.target.value)}>
                  <option value="">{t("ucca.form.professionalPlaceholder")}</option>
                  {facilityProfessionals.map((p) => <option key={p.id} value={p.id}>{p.full_name} · {p.profession_name}</option>)}
                </select>
              )}
            </FormField>
            <FormField label={t("ucca.form.cgId")}><input value={shown.employeeNumber} readOnly /></FormField>
            <FormField label={t("ucca.form.profession")}><input value={shown.profession} readOnly /></FormField>
            <FormField label={t("ucca.form.mrn")} required>
              <input value={caseRef} disabled={readOnly} required placeholder={t("ucca.form.mrnPlaceholder")} onChange={(e) => setCaseRef(e.target.value)} />
            </FormField>
            <FormField label={t("ucca.form.date")} required>
              <input type="date" value={auditDate} disabled={readOnly} required onChange={(e) => setAuditDate(e.target.value)} />
            </FormField>
            <FormField label={t("ucca.form.auditor")}><input value={existing.data?.auditor_name ?? me?.full_name ?? ""} readOnly /></FormField>
          </div>
        </div>

        <h2 style={{ fontSize: 17, margin: "24px 0 12px" }}>{t("ucca.form.criteriaSection")}</h2>
        <EvaluationRules />
        <div style={{ display: "grid", gap: 12 }}>
          {criteria.data.map((c) => (
            <CriterionCard key={c.id} criterion={c} readOnly={readOnly}
              state={answers[c.id] ?? { outcome: null, reason: "", comment: "" }}
              invalid={showErrors && (!answers[c.id]?.outcome || (answers[c.id]?.outcome === "not_applicable" && !answers[c.id].reason.trim()))}
              onChange={(next) => setAnswers((a) => ({ ...a, [c.id]: next }))} />
          ))}
        </div>

        <div style={{ marginTop: 16 }}>
          <FormField label={t("ucca.form.notes")}>
            <textarea rows={2} value={notes} disabled={readOnly} onChange={(e) => setNotes(e.target.value)} />
          </FormField>
        </div>

        <FindingSection state={finding} onChange={setFinding} required={findingRequired} owners={owners.data} readOnly={readOnly} />
      </form>

      {notice && <SaveNotice kind={notice.kind} audit={notice.audit} onClose={() => setNotice(null)} ownerName={(id) => owners.data.find((o) => o.id === id)?.full_name} />}
      {error && <p role="alert" style={{ color: brandTokens.colors.danger, marginTop: 12 }}>{error}</p>}

      <ScoreBar score={live} answered={answered} total={criteria.data.length} actions={
        <>
          {!readOnly && <button type="submit" form="audit-form" className="btn-primary" disabled={saving}>{saving ? t("ucca.form.saving") : t("ucca.form.saveDraft")}</button>}
          {isEdit && status === "draft" && canCreate && <button type="button" className="btn-ghost" disabled={saving} onClick={() => transition("submit")}>{t("ucca.form.submit")}</button>}
          {isEdit && status === "submitted" && canApprove && <button type="button" className="btn-primary" disabled={saving} onClick={() => transition("approve")}>{t("ucca.form.approve")}</button>}
        </>
      } />
    </section>
  );
}
