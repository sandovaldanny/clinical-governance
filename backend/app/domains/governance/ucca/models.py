"""
M04 — UCCA, implementado como el módulo de referencia completo. Muestra el patrón que TODO
módulo de auditoría/gobierno debe seguir: plantilla versionada, resultado inmutable una vez
aprobado, y hallazgos que alimentan Acciones Correctivas (M06) sin duplicar datos.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
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
    """Criterio de evaluación dentro de una versión de plantilla (dominio clínico + pregunta
    universal + interpretación por profesión + evidencia esperada). Administrable desde
    Administración → Criterios. Puede aplicar solo a ciertas profesiones (regla crítica del
    funcional, sección M02): la aplicabilidad la resuelve el motor de reglas, no una columna
    booleana embebida aquí. `is_active=False` lo oculta de nuevas evaluaciones sin borrar
    el histórico que lo referencia."""

    __tablename__ = "ucca_audit_criteria"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    template_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ucca_audit_template_versions.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    domain: Mapped[str] = mapped_column(String(120), nullable=False)
    universal_question: Mapped[str] = mapped_column(String(500), nullable=False)
    profession_interpretation: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    examples_evidence: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditCycle(Base):
    """Un ciclo/periodo de auditoría para un centro (multi-centro por diseño: facility_id
    obligatorio + política RLS, ver alembic/versions/0003_rls_policies.py). `year`/`quarter`
    formalizan el periodo para filtros del dashboard; `period_label` = f"{quarter}-{year}"."""

    __tablename__ = "ucca_audit_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    template_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ucca_audit_template_versions.id"), nullable=False
    )
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[str] = mapped_column(String(2), nullable=False)  # Q1..Q4
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChartAudit(Base):
    """Auditoría de UN expediente (MRN) de UN profesional dentro de un ciclo = una fila de la
    hoja Excel UCCA. Las respuestas por criterio viven en AuditResult (chart_audit_id).
    Score/outcome se guardan calculados (ver scoring.py) y se recalculan en cada guardado
    mientras status == draft. Aprobada → inmutable (regla global #1)."""

    __tablename__ = "ucca_chart_audits"
    __table_args__ = (
        UniqueConstraint("cycle_id", "professional_id", "case_reference", name="uq_chart_audit_case"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_cycles.id"), nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    professional_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("professionals.id"), nullable=False)
    auditor_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    case_reference: Mapped[str] = mapped_column(String(80), nullable=False)
    audit_date: Mapped["Date"] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft -> submitted -> approved
    applicable_count: Mapped[int] = mapped_column(Integer, default=0)
    yes_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditResult(Base):
    """Respuesta a UN criterio dentro de una auditoría por expediente (celda CCA…CMC del Excel).
    facility/cycle/professional/auditor se copian de la cabecera para RLS y consultas por
    criterio. Inmutable una vez `status == approved` (regla global #1)."""

    __tablename__ = "ucca_audit_results"
    __table_args__ = (UniqueConstraint("chart_audit_id", "criterion_id", name="uq_result_audit_criterion"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    chart_audit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_chart_audits.id"), nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_cycles.id"), nullable=False)
    criterion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ucca_audit_criteria.id"), nullable=False)
    professional_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    auditor_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    outcome: Mapped[str] = mapped_column(String(30), nullable=False)  # compliant/non_compliant/not_applicable
    not_applicable_reason: Mapped[str | None] = mapped_column(String(500))
    comment: Mapped[str | None] = mapped_column(String(500))
    evidence_reference: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="draft")  # sincronizado con la cabecera

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Finding(Base):
    """Hallazgo principal (Key Finding) de una auditoría por expediente, o de un resultado
    concreto. M06 (Acciones Correctivas) lo consume por finding_id sin copiar datos."""

    __tablename__ = "ucca_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    facility_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    chart_audit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ucca_chart_audits.id"), nullable=True)
    result_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ucca_audit_results.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
