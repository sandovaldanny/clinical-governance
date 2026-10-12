"""
Servicio de UCCA. Muestra el patrón obligatorio para cualquier módulo de auditoría:
1. Toda escritura relevante pasa por audit.record_event().
2. Una respuesta "not_applicable" exige razón trazable (regla global de negocio #5).
3. Una auditoría aprobada no se puede volver a modificar (regla global de negocio #1).
4. Score y outcome se calculan con scoring.py (fórmulas del Excel UCCA) en cada guardado.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import record_event
from app.core.master_data import create_audited, get_or_404, update_audited
from app.domains.governance.corrective_actions.models import CorrectiveAction
from app.domains.governance.ucca.models import (
    AuditCriterion,
    AuditCycle,
    AuditResult,
    AuditTemplateVersion,
    ChartAudit,
    Finding,
)
from app.domains.governance.ucca.schemas import ChartAuditWriteRequest
from app.domains.governance.ucca.scoring import ANSWER_NA, ANSWER_NO, compute_score
from app.domains.identity.models import Facility, Profession, Professional, User


def _cycle_out(cycle: AuditCycle, facility_name: str | None, audits_count: int, average_score) -> dict:
    return {
        "id": cycle.id, "facility_id": cycle.facility_id, "facility_name": facility_name,
        "template_version_id": cycle.template_version_id, "period_label": cycle.period_label,
        "year": cycle.year, "quarter": cycle.quarter, "status": cycle.status,
        "audits_count": int(audits_count or 0),
        "average_score": None if average_score is None else round(float(average_score), 2),
    }


def create_cycle(db: Session, *, actor_user_id: uuid.UUID, facility_id: uuid.UUID, year: int, quarter: str) -> dict:
    """Un ciclo por centro + año + trimestre; `period_label` se deriva ("Q2-2026").
    Orden de consultas: duplicado · versión vigente · nombre del centro."""
    duplicate = db.scalar(
        select(AuditCycle).where(AuditCycle.facility_id == facility_id, AuditCycle.year == year, AuditCycle.quarter == quarter)
    )
    if duplicate:
        raise PermissionError(f"Ya existe un ciclo {quarter}-{year} para este centro.")
    version = _current_template_version(db)
    if not version:
        raise ValueError("No hay una versión de plantilla UCCA vigente; ejecute el seed primero.")
    facility_name = db.scalar(select(Facility.name).where(Facility.id == facility_id))
    cycle = AuditCycle(
        facility_id=facility_id, template_version_id=version.id, period_label=f"{quarter}-{year}",
        year=year, quarter=quarter, status="draft", created_by_user_id=actor_user_id,
    )
    db.add(cycle)
    db.flush()
    record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="AuditCycle",
                 entity_id=str(cycle.id), action="create",
                 new_values={"facility_id": str(facility_id), "period_label": cycle.period_label})
    db.commit()
    db.refresh(cycle)
    return _cycle_out(cycle, facility_name, 0, None)


def get_cycle_or_404(db: Session, cycle_id: uuid.UUID) -> AuditCycle:
    cycle = db.scalar(select(AuditCycle).where(AuditCycle.id == cycle_id))
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado")
    return cycle


def list_cycles(db: Session) -> list[dict]:
    """Un execute(): (ciclo, nombre centro, nº auditorías no borrador, score medio no borrador)."""
    counted = (
        select(
            ChartAudit.cycle_id.label("cycle_id"),
            func.count(ChartAudit.id).label("audits_count"),
            func.avg(ChartAudit.score).label("average_score"),
        )
        .where(ChartAudit.status != "draft")
        .group_by(ChartAudit.cycle_id)
        .subquery()
    )
    rows = db.execute(
        select(AuditCycle, Facility.name, counted.c.audits_count, counted.c.average_score)
        .join(Facility, Facility.id == AuditCycle.facility_id, isouter=True)
        .join(counted, counted.c.cycle_id == AuditCycle.id, isouter=True)
        .order_by(AuditCycle.year.desc(), AuditCycle.quarter.desc(), AuditCycle.created_at.desc())
    ).all()
    return [_cycle_out(cycle, name, count, avg) for cycle, name, count, avg in rows]


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


# ---------------------------------------------------------------------------
# Auditoría por expediente (chart audit)
# ---------------------------------------------------------------------------


def get_chart_audit_or_404(db: Session, audit_id: uuid.UUID) -> ChartAudit:
    return get_or_404(db, ChartAudit, audit_id, "Auditoría")


def _active_criteria(db: Session, template_version_id: uuid.UUID) -> list[AuditCriterion]:
    return list(
        db.scalars(
            select(AuditCriterion)
            .where(AuditCriterion.template_version_id == template_version_id, AuditCriterion.is_active.is_(True))
            .order_by(AuditCriterion.code)
        ).all()
    )


def _validate_answers(criteria: list[AuditCriterion], payload: ChartAuditWriteRequest) -> dict[uuid.UUID, AuditCriterion]:
    by_id = {c.id: c for c in criteria}
    seen: set[uuid.UUID] = set()
    for answer in payload.answers:
        if answer.criterion_id not in by_id:
            raise ValueError("Respuesta para un criterio que no pertenece a la plantilla vigente del ciclo.")
        if answer.criterion_id in seen:
            raise ValueError(f"Criterio {by_id[answer.criterion_id].code} respondido más de una vez.")
        seen.add(answer.criterion_id)
        if answer.outcome == ANSWER_NA and not (answer.not_applicable_reason or "").strip():
            raise ValueError(
                f'{by_id[answer.criterion_id].code}: un "No aplica" requiere una razón trazable (regla global #5).'
            )
    missing = [c.code for c in criteria if c.id not in seen]
    if missing:
        raise ValueError(f"Faltan respuestas para: {', '.join(missing)}.")
    return by_id


def _validate_professional(db: Session, cycle: AuditCycle, professional_id: uuid.UUID) -> Professional:
    professional = db.scalar(select(Professional).where(Professional.id == professional_id))  # scalar: profesional
    if not professional or not professional.is_active:
        raise ValueError("El profesional no existe o está inactivo.")
    if professional.primary_facility_id != cycle.facility_id:
        raise ValueError("El profesional no pertenece al centro del ciclo.")
    return professional


def _ensure_no_duplicate(db: Session, cycle: AuditCycle, professional_id: uuid.UUID, case_reference: str, exclude_id=None) -> None:
    stmt = select(ChartAudit).where(
        ChartAudit.cycle_id == cycle.id, ChartAudit.professional_id == professional_id,
        ChartAudit.case_reference == case_reference,
    )
    if exclude_id is not None:
        stmt = stmt.where(ChartAudit.id != exclude_id)
    if db.scalar(stmt):  # scalar: duplicado
        raise PermissionError("Ya existe una auditoría de ese expediente para este profesional en el ciclo.")


def _require_finding_if_needed(score, payload: ChartAuditWriteRequest) -> None:
    has_no = any(a.outcome == ANSWER_NO for a in payload.answers)
    if score.outcome is not None and score.outcome != "compliant" and has_no and payload.finding is None:
        raise ValueError("El outcome no es Compliant: registre el hallazgo principal (Key Finding).")


def _write_answers(db: Session, audit: ChartAudit, by_id: dict, payload: ChartAuditWriteRequest) -> None:
    for answer in payload.answers:
        db.add(
            AuditResult(
                chart_audit_id=audit.id, facility_id=audit.facility_id, cycle_id=audit.cycle_id,
                criterion_id=answer.criterion_id, professional_id=audit.professional_id,
                auditor_user_id=audit.auditor_user_id, outcome=answer.outcome,
                not_applicable_reason=(answer.not_applicable_reason or "").strip() or None,
                comment=(answer.comment or "").strip() or None, status=audit.status,
            )
        )


def _sync_finding(db: Session, *, actor_user_id: uuid.UUID, audit: ChartAudit, payload: ChartAuditWriteRequest,
                  existing: Finding | None) -> None:
    """Crea/actualiza el hallazgo de expediente y su acción correctiva según el payload.
    Si el payload no trae hallazgo y existía uno, se cierra como 'withdrawn' (no se borra)."""
    if payload.finding is None:
        if existing is not None and existing.status != "withdrawn":
            existing.status = "withdrawn"
            record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="Finding",
                         entity_id=str(existing.id), action="withdraw", new_values={"status": "withdrawn"})
        return
    finding = existing
    if finding is None:
        finding = Finding(facility_id=audit.facility_id, chart_audit_id=audit.id,
                          description=payload.finding.description.strip(), status="open")
        db.add(finding)
        db.flush()
        record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="Finding",
                     entity_id=str(finding.id), action="create", new_values={"description": finding.description})
    else:
        previous = finding.description
        finding.description = payload.finding.description.strip()
        finding.status = "open"
        if previous != finding.description:
            record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="Finding",
                         entity_id=str(finding.id), action="update",
                         previous_values={"description": previous}, new_values={"description": finding.description})
    action_in = payload.finding.corrective_action
    action = db.scalar(select(CorrectiveAction).where(CorrectiveAction.source_finding_id == finding.id))  # scalar: acción previa
    if action_in is None:
        return
    closed_at = datetime.now(timezone.utc) if action_in.status == "closed" else None
    if action is None:
        action = CorrectiveAction(
            facility_id=audit.facility_id, source_module="ucca", source_finding_id=finding.id,
            responsible_user_id=action_in.responsible_user_id, due_date=action_in.due_date,
            status=action_in.status, description=action_in.description.strip(),
            closure_evidence=action_in.closure_evidence, closed_at=closed_at,
        )
        db.add(action)
        db.flush()
        record_event(db, actor_user_id=str(actor_user_id), module="corrective_actions", entity_type="CorrectiveAction",
                     entity_id=str(action.id), action="create",
                     new_values={"description": action.description, "status": action.status,
                                 "responsible_user_id": str(action.responsible_user_id), "due_date": str(action.due_date)})
    else:
        previous = {"description": action.description, "status": action.status,
                    "responsible_user_id": str(action.responsible_user_id), "due_date": str(action.due_date)}
        action.description = action_in.description.strip()
        action.status = action_in.status
        action.responsible_user_id = action_in.responsible_user_id
        action.due_date = action_in.due_date
        action.closure_evidence = action_in.closure_evidence
        action.closed_at = closed_at
        new = {"description": action.description, "status": action.status,
               "responsible_user_id": str(action.responsible_user_id), "due_date": str(action.due_date)}
        if new != previous:
            record_event(db, actor_user_id=str(actor_user_id), module="corrective_actions", entity_type="CorrectiveAction",
                         entity_id=str(action.id), action="update", previous_values=previous, new_values=new)
    if finding.status == "open" and action.status == "closed":
        finding.status = "closed"


def _score_values(score) -> dict:
    return {"applicable_count": str(score.applicable_count), "yes_count": str(score.yes_count),
            "score": None if score.score is None else f"{score.score:.2f}", "outcome": score.outcome}


def create_chart_audit(db: Session, *, actor_user_id: uuid.UUID, cycle: AuditCycle, payload: ChartAuditWriteRequest) -> dict:
    """Orden de consultas (los tests con FakeSession dependen de él): el router ya consumió
    scalar #1 (ciclo). Aquí: scalar #2 profesional · scalar #3 duplicado · scalars #1 criterios."""
    professional = _validate_professional(db, cycle, payload.professional_id)          # scalar #2
    _ensure_no_duplicate(db, cycle, professional.id, payload.case_reference.strip())    # scalar #3
    criteria = _active_criteria(db, cycle.template_version_id)                          # scalars #1
    by_id = _validate_answers(criteria, payload)
    score = compute_score(a.outcome for a in payload.answers)
    _require_finding_if_needed(score, payload)

    audit = ChartAudit(
        cycle_id=cycle.id, facility_id=cycle.facility_id, professional_id=professional.id,
        auditor_user_id=actor_user_id, case_reference=payload.case_reference.strip(),
        audit_date=payload.audit_date, status="draft", applicable_count=score.applicable_count,
        yes_count=score.yes_count, score=score.score, outcome=score.outcome, notes=payload.notes.strip(),
    )
    db.add(audit)
    db.flush()
    _write_answers(db, audit, by_id, payload)
    record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="ChartAudit",
                 entity_id=str(audit.id), action="create",
                 new_values={"cycle_id": str(cycle.id), "professional_id": str(professional.id),
                             "case_reference": audit.case_reference, **_score_values(score)})
    _sync_finding(db, actor_user_id=actor_user_id, audit=audit, payload=payload, existing=None)
    db.commit()
    db.refresh(audit)
    return _detail_from_parts(audit, professional, None, by_id, payload, None)


def update_chart_audit(db: Session, *, actor_user_id: uuid.UUID, audit: ChartAudit, payload: ChartAuditWriteRequest) -> dict:
    """Solo en borrador. Reemplaza TODAS las respuestas y recalcula score/outcome. Orden de
    consultas: router scalar #1 auditoría · scalar #2 ciclo · #3 profesional · #4 duplicado ·
    scalars #1 criterios · scalars #2 respuestas previas · scalar #5 hallazgo previo."""
    if audit.status != "draft":
        raise PermissionError("Solo se puede editar una auditoría en borrador (regla global #1).")
    cycle = get_cycle_or_404(db, audit.cycle_id)                                        # scalar #2
    professional = _validate_professional(db, cycle, payload.professional_id)          # scalar #3
    _ensure_no_duplicate(db, cycle, professional.id, payload.case_reference.strip(), exclude_id=audit.id)  # scalar #4
    criteria = _active_criteria(db, cycle.template_version_id)                          # scalars #1
    by_id = _validate_answers(criteria, payload)
    score = compute_score(a.outcome for a in payload.answers)
    _require_finding_if_needed(score, payload)

    for old in db.scalars(select(AuditResult).where(AuditResult.chart_audit_id == audit.id)).all():  # scalars #2
        db.delete(old)
    previous = {"professional_id": str(audit.professional_id), "case_reference": audit.case_reference,
                "audit_date": str(audit.audit_date), "notes": audit.notes,
                "applicable_count": str(audit.applicable_count), "yes_count": str(audit.yes_count),
                "score": None if audit.score is None else f"{float(audit.score):.2f}", "outcome": audit.outcome}
    audit.professional_id = professional.id
    audit.case_reference = payload.case_reference.strip()
    audit.audit_date = payload.audit_date
    audit.notes = payload.notes.strip()
    audit.applicable_count, audit.yes_count = score.applicable_count, score.yes_count
    audit.score, audit.outcome = score.score, score.outcome
    db.flush()
    _write_answers(db, audit, by_id, payload)
    new = {"professional_id": str(audit.professional_id), "case_reference": audit.case_reference,
           "audit_date": str(audit.audit_date), "notes": audit.notes, **_score_values(score)}
    record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="ChartAudit",
                 entity_id=str(audit.id), action="update", previous_values=previous, new_values=new)
    existing = db.scalar(select(Finding).where(Finding.chart_audit_id == audit.id))      # scalar #5
    _sync_finding(db, actor_user_id=actor_user_id, audit=audit, payload=payload, existing=existing)
    db.commit()
    db.refresh(audit)
    return _detail_from_parts(audit, professional, None, by_id, payload, None)


def _transition(db: Session, *, actor_user_id: uuid.UUID, audit: ChartAudit, from_status: str, to_status: str, action: str) -> dict:
    """Orden: scalars #1 respuestas (se sincroniza su estado) → luego chart_audit_detail()."""
    if audit.status != from_status:
        raise PermissionError(f"La auditoría está en estado '{audit.status}'; se esperaba '{from_status}'.")
    audit.status = to_status
    for result in db.scalars(select(AuditResult).where(AuditResult.chart_audit_id == audit.id)).all():  # scalars #1
        result.status = to_status
    db.flush()
    record_event(db, actor_user_id=str(actor_user_id), module="ucca", entity_type="ChartAudit",
                 entity_id=str(audit.id), action=action,
                 previous_values={"status": from_status}, new_values={"status": to_status})
    db.commit()
    db.refresh(audit)
    return chart_audit_detail(db, audit)


def submit_chart_audit(db: Session, *, actor_user_id: uuid.UUID, audit: ChartAudit) -> dict:
    return _transition(db, actor_user_id=actor_user_id, audit=audit, from_status="draft", to_status="submitted", action="submit")


def approve_chart_audit(db: Session, *, actor_user_id: uuid.UUID, audit: ChartAudit) -> dict:
    return _transition(db, actor_user_id=actor_user_id, audit=audit, from_status="submitted", to_status="approved", action="approve")


def _finding_out(db: Session, finding: Finding | None) -> dict | None:
    if finding is None:
        return None
    action = db.scalar(select(CorrectiveAction).where(CorrectiveAction.source_finding_id == finding.id))
    action_out = None
    if action is not None:
        responsible = db.scalar(select(User.full_name).where(User.id == action.responsible_user_id))
        action_out = {"id": action.id, "description": action.description, "responsible_user_id": action.responsible_user_id,
                      "responsible_name": responsible, "due_date": action.due_date, "status": action.status,
                      "closure_evidence": action.closure_evidence}
    return {"id": finding.id, "description": finding.description, "status": finding.status, "corrective_action": action_out}


def _detail_from_parts(audit: ChartAudit, professional: Professional, profession_name: str | None,
                       by_id: dict, payload: ChartAuditWriteRequest, auditor_name: str | None) -> dict:
    """Respuesta inmediata tras crear/editar, sin releer la DB (los tests con fakes dependen de esto)."""
    answers = [
        {"criterion_id": a.criterion_id, "criterion_code": by_id[a.criterion_id].code, "outcome": a.outcome,
         "not_applicable_reason": a.not_applicable_reason, "comment": a.comment}
        for a in sorted(payload.answers, key=lambda a: by_id[a.criterion_id].code)
    ]
    finding = None
    if payload.finding is not None:
        action = payload.finding.corrective_action
        finding = {"id": audit.id, "description": payload.finding.description, "status": "open",
                   "corrective_action": None if action is None else {
                       "id": audit.id, "description": action.description, "responsible_user_id": action.responsible_user_id,
                       "responsible_name": None, "due_date": action.due_date, "status": action.status,
                       "closure_evidence": action.closure_evidence}}
    return {
        "id": audit.id, "cycle_id": audit.cycle_id, "facility_id": audit.facility_id,
        "professional_id": professional.id, "professional_name": professional.full_name,
        "employee_number": professional.employee_number, "profession_name": profession_name,
        "auditor_user_id": audit.auditor_user_id, "auditor_name": auditor_name,
        "case_reference": audit.case_reference, "audit_date": audit.audit_date, "status": audit.status,
        "applicable_count": audit.applicable_count, "yes_count": audit.yes_count,
        "score": None if audit.score is None else float(audit.score), "outcome": audit.outcome,
        "notes": audit.notes, "answers": answers, "finding": finding,
    }


def chart_audit_detail(db: Session, audit: ChartAudit) -> dict:
    """Detalle completo desde DB. Orden: scalar profesional · scalar nombre auditor · scalar nombre
    profesión (si hay profession_id) · scalars respuestas · scalars criterios (si hay respuestas) ·
    scalar hallazgo (· scalar acción · scalar responsable si hay hallazgo)."""
    professional = db.scalar(select(Professional).where(Professional.id == audit.professional_id))
    auditor_name = db.scalar(select(User.full_name).where(User.id == audit.auditor_user_id))
    profession_name = None
    if professional is not None and getattr(professional, "profession_id", None) is not None:
        profession_name = db.scalar(select(Profession.name).where(Profession.id == professional.profession_id))
    rows = db.scalars(
        select(AuditResult).where(AuditResult.chart_audit_id == audit.id)
    ).all()
    codes = {c.id: c.code for c in db.scalars(select(AuditCriterion).where(AuditCriterion.id.in_([r.criterion_id for r in rows]))).all()} if rows else {}
    answers = sorted(
        [{"criterion_id": r.criterion_id, "criterion_code": codes.get(r.criterion_id, "?"), "outcome": r.outcome,
          "not_applicable_reason": r.not_applicable_reason, "comment": r.comment} for r in rows],
        key=lambda a: a["criterion_code"],
    )
    finding = db.scalar(select(Finding).where(Finding.chart_audit_id == audit.id))
    return {
        "id": audit.id, "cycle_id": audit.cycle_id, "facility_id": audit.facility_id,
        "professional_id": audit.professional_id,
        "professional_name": professional.full_name if professional else "—",
        "employee_number": professional.employee_number if professional else "—",
        "profession_name": profession_name, "auditor_user_id": audit.auditor_user_id, "auditor_name": auditor_name,
        "case_reference": audit.case_reference, "audit_date": audit.audit_date, "status": audit.status,
        "applicable_count": audit.applicable_count, "yes_count": audit.yes_count,
        "score": None if audit.score is None else float(audit.score), "outcome": audit.outcome,
        "notes": audit.notes, "answers": answers, "finding": _finding_out(db, finding),
    }


def list_chart_audits(db: Session, *, cycle_id: uuid.UUID) -> list[dict]:
    """Filas tipo Excel. Orden de execute(): cabeceras · respuestas · hallazgos."""
    headers = db.execute(
        select(ChartAudit, Professional.full_name, Professional.employee_number, Profession.name, User.full_name)
        .join(Professional, Professional.id == ChartAudit.professional_id)
        .join(Profession, Profession.id == Professional.profession_id, isouter=True)
        .join(User, User.id == ChartAudit.auditor_user_id, isouter=True)
        .where(ChartAudit.cycle_id == cycle_id)
        .order_by(ChartAudit.audit_date, ChartAudit.created_at)
    ).all()
    answer_rows = db.execute(
        select(AuditResult.chart_audit_id, AuditCriterion.code, AuditResult.outcome)
        .join(AuditCriterion, AuditCriterion.id == AuditResult.criterion_id)
        .where(AuditResult.cycle_id == cycle_id)
    ).all()
    finding_rows = db.execute(
        select(Finding.chart_audit_id).where(Finding.chart_audit_id.is_not(None), Finding.status != "withdrawn")
    ).all()
    answers: dict[uuid.UUID, dict[str, str]] = {}
    for audit_id, code, outcome in answer_rows:
        answers.setdefault(audit_id, {})[code] = outcome
    with_finding = {row[0] for row in finding_rows}
    out = []
    for audit, pro_name, employee_number, profession_name, auditor_name in headers:
        out.append({
            "id": audit.id, "professional_id": audit.professional_id, "professional_name": pro_name,
            "employee_number": employee_number, "profession_name": profession_name, "auditor_name": auditor_name,
            "case_reference": audit.case_reference, "audit_date": audit.audit_date, "status": audit.status,
            "applicable_count": audit.applicable_count, "yes_count": audit.yes_count,
            "score": None if audit.score is None else float(audit.score), "outcome": audit.outcome,
            "answers": answers.get(audit.id, {}), "has_finding": audit.id in with_finding,
        })
    return out
