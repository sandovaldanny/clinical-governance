"""
Servicio de UCCA. Muestra el patrón obligatorio para cualquier módulo de auditoría:
1. Toda escritura relevante pasa por audit.record_event().
2. Un resultado "not_applicable" exige razón trazable (regla global de negocio #5).
3. Un resultado aprobado no se puede volver a modificar (regla global de negocio #1).
"""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import record_event
from app.domains.governance.ucca.models import (
    AuditCriterion,
    AuditCycle,
    AuditResult,
    AuditTemplateVersion,
    Finding,
)


def create_cycle(
    db: Session, *, actor_user_id: uuid.UUID, facility_id: uuid.UUID, template_version_id: uuid.UUID,
    period_label: str,
) -> AuditCycle:
    cycle = AuditCycle(
        facility_id=facility_id,
        template_version_id=template_version_id,
        period_label=period_label,
        status="draft",
        created_by_user_id=actor_user_id,
    )
    db.add(cycle)
    db.flush()
    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="ucca",
        entity_type="AuditCycle",
        entity_id=str(cycle.id),
        action="create",
        new_values={"facility_id": str(facility_id), "period_label": period_label},
    )
    db.commit()
    db.refresh(cycle)
    return cycle


def record_result(
    db: Session,
    *,
    actor_user_id: uuid.UUID,
    cycle: AuditCycle,
    criterion_id: uuid.UUID,
    professional_id: uuid.UUID,
    outcome: str,
    not_applicable_reason: str | None,
    evidence_reference: str | None,
) -> AuditResult:
    if outcome == "not_applicable" and not not_applicable_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Un resultado "No aplica" requiere una razón trazable (regla global #5).',
        )

    result = AuditResult(
        facility_id=cycle.facility_id,
        cycle_id=cycle.id,
        criterion_id=criterion_id,
        professional_id=professional_id,
        auditor_user_id=actor_user_id,
        outcome=outcome,
        not_applicable_reason=not_applicable_reason,
        evidence_reference=evidence_reference,
        status="draft",
    )
    db.add(result)
    db.flush()
    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="ucca",
        entity_type="AuditResult",
        entity_id=str(result.id),
        action="create",
        new_values={"outcome": outcome},
    )
    db.commit()
    db.refresh(result)
    return result


def approve_result(db: Session, *, actor_user_id: uuid.UUID, result: AuditResult) -> AuditResult:
    """Aprobar es la última escritura permitida sobre un resultado — después queda inmutable."""
    if result.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El resultado ya está aprobado y no puede modificarse (regla global #1).",
        )

    previous_status = result.status
    result.status = "approved"
    db.flush()

    if result.outcome == "non_compliant":
        finding = Finding(
            facility_id=result.facility_id,
            result_id=result.id,
            description="Hallazgo generado automáticamente desde un resultado UCCA no conforme.",
            status="open",
        )
        db.add(finding)

    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="ucca",
        entity_type="AuditResult",
        entity_id=str(result.id),
        action="approve",
        previous_values={"status": previous_status},
        new_values={"status": "approved"},
    )
    db.commit()
    db.refresh(result)
    return result


def get_result_or_404(db: Session, result_id: uuid.UUID) -> AuditResult:
    result = db.scalar(select(AuditResult).where(AuditResult.id == result_id))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    return result


def get_cycle_or_404(db: Session, cycle_id: uuid.UUID) -> AuditCycle:
    cycle = db.scalar(select(AuditCycle).where(AuditCycle.id == cycle_id))
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado")
    return cycle


def list_cycles(db: Session) -> list[AuditCycle]:
    return list(
        db.scalars(select(AuditCycle).order_by(AuditCycle.created_at.desc())).all()
    )


def list_results(db: Session, *, cycle_id: uuid.UUID) -> list[dict]:
    rows = db.execute(
        select(
            AuditResult,
            AuditCriterion.code,
            AuditCriterion.description,
        )
        .join(AuditCriterion, AuditResult.criterion_id == AuditCriterion.id)
        .where(AuditResult.cycle_id == cycle_id)
        .order_by(AuditCriterion.code)
    ).all()
    from app.domains.identity.models import Professional

    results: list[dict] = []
    for result, criterion_code, criterion_description in rows:
        professional = db.scalar(select(Professional).where(Professional.id == result.professional_id))
        results.append(
            {
                "id": result.id,
                "criterion_code": criterion_code,
                "criterion_description": criterion_description,
                "professional_name": professional.full_name if professional else "—",
                "outcome": result.outcome,
                "status": result.status,
                "evidence_reference": result.evidence_reference,
                "not_applicable_reason": result.not_applicable_reason,
            }
        )
    return results


def list_criteria(db: Session) -> list[AuditCriterion]:
    """Indicadores/criterios de la plantilla UCCA vigente (M04 + JAWDA/OMH001)."""
    current_version = db.scalar(
        select(AuditTemplateVersion).where(AuditTemplateVersion.is_current.is_(True))
    )
    if not current_version:
        return []
    return list(
        db.scalars(
            select(AuditCriterion)
            .where(AuditCriterion.template_version_id == current_version.id)
            .order_by(AuditCriterion.code)
        ).all()
    )
