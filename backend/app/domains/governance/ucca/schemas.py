from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class AuditCycleCreateRequest(BaseModel):
    facility_id: uuid.UUID
    template_version_id: uuid.UUID
    period_label: str


class AuditCycleOut(BaseModel):
    id: uuid.UUID
    facility_id: uuid.UUID
    period_label: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class AuditResultCreateRequest(BaseModel):
    cycle_id: uuid.UUID
    criterion_id: uuid.UUID
    professional_id: uuid.UUID
    outcome: str  # compliant | non_compliant | not_applicable
    not_applicable_reason: str | None = None
    evidence_reference: str | None = None


class AuditResultOut(BaseModel):
    id: uuid.UUID
    cycle_id: uuid.UUID
    criterion_id: uuid.UUID
    professional_id: uuid.UUID
    outcome: str
    status: str
    evidence_reference: str | None = None
    not_applicable_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditResultDetailOut(BaseModel):
    id: uuid.UUID
    criterion_code: str
    criterion_domain: str
    professional_name: str
    outcome: str
    status: str
    evidence_reference: str | None = None
    not_applicable_reason: str | None = None


class AuditResultApproveRequest(BaseModel):
    result_id: uuid.UUID


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
