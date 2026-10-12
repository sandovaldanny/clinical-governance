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
from app.core.master_data import create_audited, get_or_404, update_audited
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
            AuditCriterion.domain,
        )
        .join(AuditCriterion, AuditResult.criterion_id == AuditCriterion.id)
        .where(AuditResult.cycle_id == cycle_id)
        .order_by(AuditCriterion.code)
    ).all()
    from app.domains.identity.models import Professional

    results: list[dict] = []
    for result, criterion_code, criterion_domain in rows:
        professional = db.scalar(select(Professional).where(Professional.id == result.professional_id))
        results.append(
            {
                "id": result.id,
                "criterion_code": criterion_code,
                "criterion_domain": criterion_domain,
                "professional_name": professional.full_name if professional else "—",
                "outcome": result.outcome,
                "status": result.status,
                "evidence_reference": result.evidence_reference,
                "not_applicable_reason": result.not_applicable_reason,
            }
        )
    return results


def _current_template_version(db: Session) -> AuditTemplateVersion | None:
    return db.scalar(select(AuditTemplateVersion).where(AuditTemplateVersion.is_current.is_(True)))


def list_criteria(db: Session, *, only_active: bool = False) -> list[AuditCriterion]:
    """Criterios de evaluación de la plantilla UCCA vigente. `only_active` para formularios de
    evaluación; Administración lista todos para poder reactivarlos."""
    current_version = _current_template_version(db)
    if not current_version:
        return []
    stmt = select(AuditCriterion).where(AuditCriterion.template_version_id == current_version.id)
    if only_active:
        stmt = stmt.where(AuditCriterion.is_active.is_(True))
    return list(db.scalars(stmt.order_by(AuditCriterion.code)).all())


def create_criterion(
    db: Session,
    *,
    actor_user_id: uuid.UUID,
    code: str,
    domain: str,
    universal_question: str,
    profession_interpretation: str,
    examples_evidence: str,
) -> AuditCriterion:
    """Crea un criterio en la versión de plantilla vigente. Código único por versión."""
    current_version = _current_template_version(db)
    if not current_version:
        raise ValueError("No hay una versión de plantilla UCCA vigente; ejecute el seed primero.")
    code = code.strip().upper()
    duplicate = db.scalar(
        select(AuditCriterion).where(
            AuditCriterion.template_version_id == current_version.id,
            AuditCriterion.code == code,
        )
    )
    if duplicate:
        raise PermissionError("Ya existe un criterio con ese código en la plantilla vigente.")
    obj = AuditCriterion(
        template_version_id=current_version.id,
        code=code,
        domain=domain.strip(),
        universal_question=universal_question.strip(),
        profession_interpretation=profession_interpretation.strip(),
        examples_evidence=examples_evidence.strip(),
        is_active=True,
    )
    return create_audited(
        db, obj, actor_user_id=actor_user_id, module="ucca", entity_type="AuditCriterion",
        new_values={
            "template_version_id": str(current_version.id),
            "code": code,
            "domain": obj.domain,
            "universal_question": obj.universal_question,
        },
    )


def update_criterion(db: Session, *, actor_user_id: uuid.UUID, criterion_id: uuid.UUID, data: dict) -> AuditCriterion:
    obj = get_or_404(db, AuditCriterion, criterion_id, "Criterio")
    return update_audited(db, obj, actor_user_id=actor_user_id, module="ucca", entity_type="AuditCriterion", data=data)
