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
    return [schemas.AuditCycleOut.model_validate(row) for row in service.list_cycles(db)]


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


@router.post("/cycles", response_model=schemas.AuditCycleOut, status_code=201)
def create_cycle(
    payload: schemas.AuditCycleCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.AuditCycleOut:
    require_facility_access(str(payload.facility_id), current_user)
    return domain_errors(
        lambda: service.create_cycle(
            db, actor_user_id=uuid.UUID(current_user.id), facility_id=payload.facility_id,
            year=payload.year, quarter=payload.quarter,
        )
    )


@router.get("/cycles/{cycle_id}/audits", response_model=list[schemas.ChartAuditRowOut])
def list_chart_audits(
    cycle_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> list[schemas.ChartAuditRowOut]:
    cycle = service.get_cycle_or_404(db, cycle_id)
    require_facility_access(str(cycle.facility_id), current_user)
    return [schemas.ChartAuditRowOut.model_validate(r) for r in service.list_chart_audits(db, cycle_id=cycle_id)]


@router.post("/cycles/{cycle_id}/audits", response_model=schemas.ChartAuditOut, status_code=status.HTTP_201_CREATED)
def create_chart_audit(
    cycle_id: uuid.UUID,
    payload: schemas.ChartAuditWriteRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.ChartAuditOut:
    cycle = service.get_cycle_or_404(db, cycle_id)
    require_facility_access(str(cycle.facility_id), current_user)
    return domain_errors(
        lambda: service.create_chart_audit(db, actor_user_id=uuid.UUID(current_user.id), cycle=cycle, payload=payload)
    )


@router.get("/audits/{audit_id}", response_model=schemas.ChartAuditOut)
def get_chart_audit(
    audit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> schemas.ChartAuditOut:
    audit = domain_errors(lambda: service.get_chart_audit_or_404(db, audit_id))
    require_facility_access(str(audit.facility_id), current_user)
    return schemas.ChartAuditOut.model_validate(service.chart_audit_detail(db, audit))


@router.patch("/audits/{audit_id}", response_model=schemas.ChartAuditOut)
def update_chart_audit(
    audit_id: uuid.UUID,
    payload: schemas.ChartAuditWriteRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.ChartAuditOut:
    audit = domain_errors(lambda: service.get_chart_audit_or_404(db, audit_id))
    require_facility_access(str(audit.facility_id), current_user)
    return domain_errors(
        lambda: service.update_chart_audit(db, actor_user_id=uuid.UUID(current_user.id), audit=audit, payload=payload)
    )


@router.post("/audits/{audit_id}/submit", response_model=schemas.ChartAuditOut)
def submit_chart_audit(
    audit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.create")),
) -> schemas.ChartAuditOut:
    audit = domain_errors(lambda: service.get_chart_audit_or_404(db, audit_id))
    require_facility_access(str(audit.facility_id), current_user)
    return domain_errors(lambda: service.submit_chart_audit(db, actor_user_id=uuid.UUID(current_user.id), audit=audit))


@router.post("/audits/{audit_id}/approve", response_model=schemas.ChartAuditOut)
def approve_chart_audit(
    audit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.approve")),
) -> schemas.ChartAuditOut:
    audit = domain_errors(lambda: service.get_chart_audit_or_404(db, audit_id))
    require_facility_access(str(audit.facility_id), current_user)
    return domain_errors(lambda: service.approve_chart_audit(db, actor_user_id=uuid.UUID(current_user.id), audit=audit))
