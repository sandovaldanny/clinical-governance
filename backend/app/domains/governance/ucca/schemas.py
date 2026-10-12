from __future__ import annotations

import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Quarter = Literal["Q1", "Q2", "Q3", "Q4"]


class AuditCycleCreateRequest(BaseModel):
    facility_id: uuid.UUID
    year: int = Field(ge=2020, le=2100)
    quarter: Quarter


class AuditCycleOut(BaseModel):
    id: uuid.UUID
    facility_id: uuid.UUID
    facility_name: str | None = None
    template_version_id: uuid.UUID
    period_label: str
    year: int
    quarter: str
    status: str
    audits_count: int = 0
    average_score: float | None = None


AnswerValue = Literal["compliant", "non_compliant", "not_applicable"]
ActionStatus = Literal["assigned", "in_progress", "closed"]


class AnswerIn(BaseModel):
    criterion_id: uuid.UUID
    outcome: AnswerValue
    not_applicable_reason: str | None = Field(default=None, max_length=500)
    comment: str | None = Field(default=None, max_length=500)


class CorrectiveActionIn(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    responsible_user_id: uuid.UUID
    due_date: date
    status: ActionStatus = "assigned"
    closure_evidence: str | None = Field(default=None, max_length=1000)


class FindingIn(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    corrective_action: CorrectiveActionIn | None = None


class ChartAuditWriteRequest(BaseModel):
    professional_id: uuid.UUID
    case_reference: str = Field(min_length=1, max_length=80)
    audit_date: date
    notes: str = Field(default="", max_length=1000)
    answers: list[AnswerIn]
    finding: FindingIn | None = None


class AnswerOut(BaseModel):
    criterion_id: uuid.UUID
    criterion_code: str
    outcome: str
    not_applicable_reason: str | None = None
    comment: str | None = None


class CorrectiveActionOut(BaseModel):
    id: uuid.UUID
    description: str
    responsible_user_id: uuid.UUID
    responsible_name: str | None = None
    due_date: date
    status: str
    closure_evidence: str | None = None


class FindingOut(BaseModel):
    id: uuid.UUID
    description: str
    status: str
    corrective_action: CorrectiveActionOut | None = None


class ChartAuditOut(BaseModel):
    id: uuid.UUID
    cycle_id: uuid.UUID
    facility_id: uuid.UUID
    professional_id: uuid.UUID
    professional_name: str
    employee_number: str
    profession_name: str | None = None
    auditor_user_id: uuid.UUID
    auditor_name: str | None = None
    case_reference: str
    audit_date: date
    status: str
    applicable_count: int
    yes_count: int
    score: float | None = None
    outcome: str | None = None
    notes: str = ""
    answers: list[AnswerOut]
    finding: FindingOut | None = None


class ChartAuditRowOut(BaseModel):
    """Fila de la tabla tipo Excel: respuestas como {codigo: outcome}."""
    id: uuid.UUID
    professional_id: uuid.UUID
    professional_name: str
    employee_number: str
    profession_name: str | None = None
    auditor_name: str | None = None
    case_reference: str
    audit_date: date
    status: str
    applicable_count: int
    yes_count: int
    score: float | None = None
    outcome: str | None = None
    answers: dict[str, str]
    has_finding: bool


class AuditCriterionOut(BaseModel):
    id: uuid.UUID
    code: str
    domain: str
    universal_question: str
    profession_interpretation: str
    examples_evidence: str
    is_active: bool
    template_version_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AuditCriterionCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    domain: str = Field(min_length=1, max_length=120)
    universal_question: str = Field(min_length=1, max_length=500)
    profession_interpretation: str = Field(default="", max_length=1000)
    examples_evidence: str = Field(default="", max_length=1000)


class AuditCriterionUpdateRequest(BaseModel):
    domain: str | None = Field(default=None, min_length=1, max_length=120)
    universal_question: str | None = Field(default=None, min_length=1, max_length=500)
    profession_interpretation: str | None = Field(default=None, max_length=1000)
    examples_evidence: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None
