from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


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
    criterion_description: str
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
    description: str
    severity: str
    template_version_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
