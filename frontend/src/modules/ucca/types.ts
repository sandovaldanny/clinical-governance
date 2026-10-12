export type AnswerValue = "compliant" | "non_compliant" | "not_applicable";
export type Outcome = "compliant" | "minor_improvement" | "improvement_required" | "priority_corrective_action";
export type AuditStatus = "draft" | "submitted" | "approved";
export type ActionStatus = "assigned" | "in_progress" | "closed";

export type Cycle = {
  id: string; facility_id: string; facility_name: string | null; template_version_id: string;
  period_label: string; year: number; quarter: string; status: string;
  audits_count: number; average_score: number | null;
};

export type Criterion = {
  id: string; code: string; domain: string; universal_question: string;
  profession_interpretation: string; examples_evidence: string; is_active: boolean;
};

export type Professional = {
  id: string; full_name: string; employee_number: string; profession_name: string;
  primary_facility_id: string; is_active?: boolean;
};

export type AnswerIn = { criterion_id: string; outcome: AnswerValue; not_applicable_reason: string | null; comment: string | null };
export type CorrectiveActionIn = {
  description: string; responsible_user_id: string; due_date: string; status: ActionStatus; closure_evidence: string | null;
};
export type FindingIn = { description: string; corrective_action: CorrectiveActionIn | null };
export type ChartAuditWrite = {
  professional_id: string; case_reference: string; audit_date: string; notes: string;
  answers: AnswerIn[]; finding: FindingIn | null;
};

export type AnswerOut = AnswerIn & { criterion_code: string };
export type CorrectiveActionOut = Omit<CorrectiveActionIn, "status"> & { id: string; responsible_name: string | null; status: ActionStatus | "cancelled" };
export type FindingOut = { id: string; description: string; status: string; corrective_action: CorrectiveActionOut | null };

export type ChartAudit = {
  id: string; cycle_id: string; facility_id: string; professional_id: string; professional_name: string;
  employee_number: string; profession_name: string | null; auditor_user_id: string; auditor_name: string | null;
  case_reference: string; audit_date: string; status: AuditStatus; applicable_count: number; yes_count: number;
  score: number | null; outcome: Outcome | null; notes: string; answers: AnswerOut[]; finding: FindingOut | null;
};

export type ChartAuditRow = {
  id: string; professional_id: string; professional_name: string; employee_number: string;
  profession_name: string | null; auditor_name: string | null; case_reference: string; audit_date: string;
  status: AuditStatus; applicable_count: number; yes_count: number; score: number | null; outcome: Outcome | null;
  answers: Record<string, AnswerValue>; has_finding: boolean;
};

export type Summary = {
  audits_count: number; draft_count: number; average_score: number | null;
  outcome_distribution: Record<Outcome, number>;
  criteria: { code: string; applicable: number; yes: number; yes_rate: number | null }[];
  professionals: {
    professional_id: string; employee_number: string; professional_name: string; profession_name: string | null;
    audits_count: number; average_score: number | null; outcome: Outcome | null; criteria: Record<string, number | null>;
  }[];
  trend: { year: number; quarter: string; audits_count: number; average_score: number | null }[];
  open_corrective_actions: {
    id: string; audit_id: string; case_reference: string; professional_name: string; finding: string;
    responsible_name: string | null; due_date: string; status: ActionStatus;
  }[];
};
