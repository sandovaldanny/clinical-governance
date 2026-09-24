"""
M04 — UCCA, implementado como el módulo de referencia completo. Muestra el patrón que TODO
módulo de auditoría/gobierno debe seguir: plantilla versionada, resultado inmutable una vez
aprobado, y hallazgos que alimentan Acciones Correctivas (M06) sin duplicar datos.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class AuditTemplate(Base):
    __tablename__ = "ucca_audit_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditTemplateVersion(Base):
    """Cada auditoría queda ligada a la versión exacta de plantilla usada (sección 5.3 de la
    arquitectura técnica) — aunque la plantilla evolucione después, el histórico no cambia."""

    __tablename__ = "ucca_audit_template_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_templates.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    published_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditCriterion(Base):
    """Criterio evaluable dentro de una versión de plantilla. Puede aplicar solo a ciertas
    profesiones (regla crítica del funcional, sección M02): la aplicabilidad la resuelve el
    motor de reglas, no una columna booleana embebida aquí."""

    __tablename__ = "ucca_audit_criteria"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    template_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ucca_audit_template_versions.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), default="standard")


class AuditCycle(Base):
    """Un ciclo/periodo de auditoría para un centro (multi-centro por diseño: facility_id
    obligatorio + política RLS, ver alembic/versions/0003_rls_policies.py)."""

    __tablename__ = "ucca_audit_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    template_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ucca_audit_template_versions.id"), nullable=False
    )
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditResult(Base):
    """Resultado por criterio/profesional. Inmutable una vez `status == approved`
    (regla global de negocio #1 del funcional) — aplicado a nivel de servicio y de permisos
    de base de datos, no solo de UI."""

    __tablename__ = "ucca_audit_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_cycles.id"), nullable=False)
    criterion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_criteria.id"), nullable=False)
    professional_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    auditor_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    outcome: Mapped[str] = mapped_column(String(30), nullable=False)  # compliant/non_compliant/not_applicable
    not_applicable_reason: Mapped[str | None] = mapped_column(String(500))
    evidence_reference: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft -> submitted -> approved

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Finding(Base):
    """Un resultado no conforme aprobado puede generar un hallazgo, que M06 (Acciones
    Correctivas) consume por finding_id — sin copiar los datos del resultado."""

    __tablename__ = "ucca_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    result_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_results.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
