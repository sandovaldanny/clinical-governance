"""
M06 — stub. Muestra cómo un SEGUNDO módulo consume hallazgos de UCCA sin duplicar datos:
CorrectiveAction referencia `source_finding_id` en lugar de copiar la descripción del hallazgo.
El mismo patrón aplica para CPG, medicación/JAWDA, incidentes, quejas, OPPE, FPPE o Peer Review
como origen (sección M06 del funcional).
"""
from __future__ import annotations

import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    source_module: Mapped[str] = mapped_column(String(50), nullable=False)  # "ucca", "cpg", ...
    source_finding_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    responsible_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    due_date: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
