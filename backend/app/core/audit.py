"""
Audit ledger inmutable (M10 — sección 7 de la arquitectura técnica).

`record_event()` es la ÚNICA forma soportada de escribir en `audit_events`. La tabla no otorga
permisos de UPDATE/DELETE a ningún rol de aplicación (ver migración 0002), ni siquiera al usuario
de base de datos que usa el backend, así que un bug en el código no puede alterar el historial —
solo puede fallar al insertar, nunca corromper lo ya escrito.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


def record_event(
    db: Session,
    *,
    actor_user_id: str,
    module: str,
    entity_type: str,
    entity_id: str,
    action: str,
    previous_values: dict | None = None,
    new_values: dict | None = None,
    is_retrospective: bool = False,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO audit_events
                (occurred_at, actor_user_id, module, entity_type, entity_id, action,
                 previous_values, new_values, is_retrospective)
            VALUES
                (:occurred_at, :actor_user_id, :module, :entity_type, :entity_id, :action,
                 :previous_values, :new_values, :is_retrospective)
            """
        ),
        {
            "occurred_at": datetime.now(timezone.utc),
            "actor_user_id": actor_user_id,
            "module": module,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "previous_values": previous_values,
            "new_values": new_values,
            "is_retrospective": is_retrospective,
        },
    )
