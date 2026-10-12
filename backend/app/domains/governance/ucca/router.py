from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.master_data import domain_errors
from app.core.rbac import require_facility_access, require_permission
from app.domains.governance.ucca import schemas, service

router = APIRouter(prefix="/ucca", tags=["ucca"])


@router.get("/cycles", response_model=list[schemas.AuditCycleOut])
def list_cycles(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> list[schemas.AuditCycleOut]:
    return service.list_cycles(db)


@router.get("/criteria", response_model=list[schemas.AuditCriterionOut])
def list_criteria(
    only_active: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> list[schemas.AuditCriterionOut]:
    return service.list_criteria(db, only_active=only_active)


@router.post("/criteria", response_model=schemas.AuditCriterionOut, status_code=status.HTTP_201_CREATED)
def create_criterion(
    payload: schemas.AuditCriterionCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.AuditCriterionOut:
    return domain_errors(
        lambda: service.create_criterion(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump())
    )


@router.patch("/criteria/{criterion_id}", response_model=schemas.AuditCriterionOut)
def update_criterion(
    criterion_id: uuid.UUID,
    payload: schemas.AuditCriterionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.AuditCriterionOut:
    return domain_errors(
        lambda: service.update_criterion(
            db, actor_user_id=uuid.UUID(current_user.id), criterion_id=criterion_id,
            data=payload.model_dump(exclude_unset=True),
        )
    )


@router.get("/results", response_model=list[schemas.AuditResultDetailOut])
def list_results(
    cycle_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> list[schemas.AuditResultDetailOut]:
    cycle = service.get_cycle_or_404(db, cycle_id)
    require_facility_access(str(cycle.facility_id), current_user)
    rows = service.list_results(db, cycle_id=cycle_id)
    return [schemas.AuditResultDetailOut.model_validate(row) for row in rows]


@router.post("/cycles", response_model=schemas.AuditCycleOut, status_code=201)
def create_cycle(
    payload: schemas.AuditCycleCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.AuditCycleOut:
    require_facility_access(str(payload.facility_id), current_user)
    return service.create_cycle(
        db,
        actor_user_id=uuid.UUID(current_user.id),
        facility_id=payload.facility_id,
        template_version_id=payload.template_version_id,
        period_label=payload.period_label,
    )


@router.post("/results", response_model=schemas.AuditResultOut, status_code=201)
def record_result(
    payload: schemas.AuditResultCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.AuditResultOut:
    cycle = service.get_cycle_or_404(db, payload.cycle_id)
    require_facility_access(str(cycle.facility_id), current_user)
    return service.record_result(
        db,
        actor_user_id=uuid.UUID(current_user.id),
        cycle=cycle,
        criterion_id=payload.criterion_id,
        professional_id=payload.professional_id,
        outcome=payload.outcome,
        not_applicable_reason=payload.not_applicable_reason,
        evidence_reference=payload.evidence_reference,
    )


@router.post("/results/{result_id}/approve", response_model=schemas.AuditResultOut)
def approve_result(
    result_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.approve")),
) -> schemas.AuditResultOut:
    result = service.get_result_or_404(db, result_id)
    require_facility_access(str(result.facility_id), current_user)
    return service.approve_result(db, actor_user_id=uuid.UUID(current_user.id), result=result)
