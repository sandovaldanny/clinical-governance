"""
Helpers genéricos de datos maestros (M02): crear/editar con auditoría y traducción de errores de
dominio a HTTP. Los usan identity (cargos, centros, profesiones, catálogos, roles) y ucca
(criterios de evaluación) para que toda tabla administrable se comporte igual.

Convención de errores de dominio: LookupError → 404, ValueError → 422, PermissionError → 409.
"""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import record_event


def apply_changes(obj, data: dict) -> tuple[dict, dict]:
    """Asigna solo los campos presentes en `data` y devuelve (previos, nuevos) de los que cambiaron,
    listos para record_event. Los valores se normalizan a str para el JSON del audit ledger."""
    previous: dict = {}
    new: dict = {}
    for field, value in data.items():
        current = getattr(obj, field)
        if current == value:
            continue
        previous[field] = str(current) if current is not None else None
        new[field] = str(value) if value is not None else None
        setattr(obj, field, value)
    return previous, new


def create_audited(db: Session, obj, *, actor_user_id: uuid.UUID, module: str, entity_type: str, new_values: dict):
    db.add(obj)
    db.flush()
    record_event(
        db, actor_user_id=str(actor_user_id), module=module, entity_type=entity_type,
        entity_id=str(obj.id), action="create", new_values=new_values,
    )
    db.commit()
    db.refresh(obj)
    return obj


def update_audited(db: Session, obj, *, actor_user_id: uuid.UUID, module: str, entity_type: str, data: dict):
    previous, new = apply_changes(obj, data)
    if new:
        record_event(
            db, actor_user_id=str(actor_user_id), module=module, entity_type=entity_type,
            entity_id=str(obj.id), action="update", previous_values=previous, new_values=new,
        )
    db.commit()
    db.refresh(obj)
    return obj


def get_or_404(db: Session, model, row_id: uuid.UUID, label: str):
    row = db.scalar(select(model).where(model.id == row_id))
    if not row:
        raise LookupError(f"{label} no encontrado")
    return row


def domain_errors(fn):
    """Envuelve la llamada al servicio traduciendo excepciones de dominio a HTTP."""
    try:
        return fn()
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
