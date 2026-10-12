# UCCA Chart Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** El director médico audita un expediente (MRN) de un profesional respondiendo Yes/No/N/A a los 7 criterios en una pantalla; AEGIS calcula score y outcome, registra hallazgo + acción correctiva, muestra el ciclo como la hoja Excel y un dashboard consolidado.

**Architecture:** Nueva cabecera `ucca_chart_audits` (una fila por expediente) con celdas en `ucca_audit_results` (una por criterio). El score/outcome lo calcula una función pura (`scoring.py`) replicada en el cliente para feedback en vivo. Hallazgos se guardan en `ucca_findings` + `corrective_actions` (M06). Agregados en `summary.py` (función pura sobre filas simples) expuestos como `summary` por ciclo y `dashboard` multi-ciclo.

**Tech Stack:** FastAPI 0.115 · SQLAlchemy 2 · Alembic · PostgreSQL 16 · pydantic v2 · pytest con `tests/_fakes.py` (sin Postgres) · React 18 + TypeScript 5.6 + Vite 5 · react-router 6 · react-i18next · tokens Alkalma (`frontend/src/theme/brand-tokens.ts`).

**Spec:** `docs/superpowers/specs/2026-10-12-ucca-chart-audit-design.md`

## Global Constraints

- Toda escritura pasa por `app.core.audit.record_event(db, actor_user_id=str, module=str, entity_type=str, entity_id=str, action=str, previous_values=dict|None, new_values=dict|None)`.
- Errores de dominio: `LookupError`→404, `ValueError`→422, `PermissionError`→409 vía `app.core.master_data.domain_errors`.
- Permisos: `ucca.view` leer · `ucca.create` crear/editar borrador/enviar · `ucca.approve` aprobar · `corrective_actions.manage` no se exige aparte (el hallazgo viaja en el payload de auditoría bajo `ucca.create`).
- Outcome bands exactos: `>= 90 compliant`, `>= 80 minor_improvement`, `>= 70 improvement_required`, else `priority_corrective_action`. Score = `round(yes / applicable * 100, 2)`; `None` si `applicable == 0`.
- Respuestas: `compliant | non_compliant | not_applicable`. N/A exige `not_applicable_reason` no vacío.
- Auditoría `approved` es inmutable (409 en cualquier escritura).
- Texto de UI vía i18n ES/EN (`frontend/src/i18n/{es,en}.json`); colores solo desde `brandTokens`/`alkalma`; sin scroll horizontal en tablas (`width: 100%`, textos recortados).
- Nunca `cd` en comandos Bash en paralelo: usar rutas absolutas, `git -C`, `npm --prefix`.
- Commits en `master`, mensaje termina con `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Comandos: tests `backend/.venv/bin/python -m pytest -q`; build `npm --prefix frontend run build`; migración `backend/.venv/bin/alembic upgrade head` (cwd `backend/`); seed `backend/.venv/bin/python -m app.scripts.seed_demo_data` (cwd `backend/`).

## Review Focus

1. Payload con un criterio repetido o con un criterio inactivo/ajeno a la plantilla del ciclo → 422 claro, nunca fila huérfana (Task 3 `test_create_rejects_unknown_or_duplicate_criterion`).
2. Editar un borrador reemplaza TODAS las respuestas y recalcula; no deja respuestas viejas (Task 3 `test_update_replaces_answers_and_recomputes`).
3. Score con todos N/A → `score None`, `outcome None`, y la auditoría se guarda sin exigir hallazgo (Task 1 `test_all_not_applicable`, Task 3 `test_create_all_na_no_finding_required`).
4. Summary/dashboard ignoran borradores pero los cuentan en `draft_count`; con 0 auditorías devuelve ceros y `average_score None`, no división por cero (Task 5 `test_summarize_empty`, `test_summarize_ignores_drafts`).
5. Ciclo duplicado centro+año+trimestre → 409; `period_label` derivado `Q2-2026` (Task 4 `test_create_cycle_duplicate_409`).

---

### Task 1: Scoring puro (`scoring.py`)

**Files:**
- Create: `backend/app/domains/governance/ucca/scoring.py`
- Test: `backend/tests/test_ucca_scoring.py`

**Interfaces:**
- Produces: `compute_score(outcomes: Iterable[str]) -> ScoreResult` con `ScoreResult(applicable_count: int, yes_count: int, score: float | None, outcome: str | None)`; `outcome_for(score: float | None) -> str | None`; constantes `OUTCOME_BANDS`, `PRIORITY_OUTCOME`, `ANSWER_VALUES`.

- [ ] **Step 1: Escribir tests que fallan**

```python
# backend/tests/test_ucca_scoring.py
"""Score y outcome de una auditoría por expediente (fórmulas del Excel UCCA)."""
import pytest

from app.domains.governance.ucca.scoring import PRIORITY_OUTCOME, compute_score, outcome_for

C, N, NA = "compliant", "non_compliant", "not_applicable"


def test_all_yes_is_compliant_100():
    r = compute_score([C] * 7)
    assert (r.applicable_count, r.yes_count, r.score, r.outcome) == (7, 7, 100.0, "compliant")


def test_na_excluded_from_denominator():
    r = compute_score([C, C, C, C, C, NA, N])  # 5/6
    assert r.applicable_count == 6 and r.yes_count == 5
    assert r.score == 83.33 and r.outcome == "minor_improvement"


def test_all_not_applicable():
    r = compute_score([NA] * 7)
    assert r.applicable_count == 0 and r.yes_count == 0
    assert r.score is None and r.outcome is None


def test_empty_answers():
    r = compute_score([])
    assert r.score is None and r.outcome is None


@pytest.mark.parametrize(
    "score,expected",
    [
        (100.0, "compliant"), (90.0, "compliant"), (89.99, "minor_improvement"),
        (80.0, "minor_improvement"), (79.99, "improvement_required"),
        (70.0, "improvement_required"), (69.99, PRIORITY_OUTCOME), (0.0, PRIORITY_OUTCOME),
        (None, None),
    ],
)
def test_outcome_bands(score, expected):
    assert outcome_for(score) == expected


def test_unknown_answer_rejected():
    with pytest.raises(ValueError):
        compute_score([C, "maybe"])
```

- [ ] **Step 2: Correr y ver fallo**

Run: `backend/.venv/bin/python -m pytest backend/tests/test_ucca_scoring.py -q` (desde la raíz del repo; pytest usa `backend/tests/conftest.py` → ejecutar con cwd `backend/`: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_scoring.py -q`)
Expected: `ModuleNotFoundError: app.domains.governance.ucca.scoring`

- [ ] **Step 3: Implementar**

```python
# backend/app/domains/governance/ucca/scoring.py
"""
Score y outcome de una auditoría por expediente. Réplica exacta de las fórmulas del Excel UCCA:
  Score   = IF(Applicable=0, "", YesCount/Applicable)
  Outcome = IF(Score="", "", IF(Score>=90%,"Compliant", IF(Score>=80%,"Minor Improvement",
            IF(Score>=70%,"Improvement Required","Priority Corrective Action"))))
Función pura: sin DB, sin FastAPI. El frontend la replica en `modules/ucca/scoring.ts`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ANSWER_YES = "compliant"
ANSWER_NO = "non_compliant"
ANSWER_NA = "not_applicable"
ANSWER_VALUES = (ANSWER_YES, ANSWER_NO, ANSWER_NA)

# (outcome, umbral mínimo en %) — evaluados en orden. Por debajo del último → PRIORITY_OUTCOME.
OUTCOME_BANDS: tuple[tuple[str, float], ...] = (
    ("compliant", 90.0),
    ("minor_improvement", 80.0),
    ("improvement_required", 70.0),
)
PRIORITY_OUTCOME = "priority_corrective_action"
OUTCOME_VALUES = tuple(o for o, _ in OUTCOME_BANDS) + (PRIORITY_OUTCOME,)


@dataclass(frozen=True)
class ScoreResult:
    applicable_count: int
    yes_count: int
    score: float | None
    outcome: str | None


def outcome_for(score: float | None) -> str | None:
    if score is None:
        return None
    for outcome, threshold in OUTCOME_BANDS:
        if score >= threshold:
            return outcome
    return PRIORITY_OUTCOME


def compute_score(outcomes: Iterable[str]) -> ScoreResult:
    answers = list(outcomes)
    for value in answers:
        if value not in ANSWER_VALUES:
            raise ValueError(f"Respuesta no válida: {value!r}")
    applicable = sum(1 for a in answers if a != ANSWER_NA)
    yes = sum(1 for a in answers if a == ANSWER_YES)
    score = None if applicable == 0 else round(yes / applicable * 100, 2)
    return ScoreResult(applicable_count=applicable, yes_count=yes, score=score, outcome=outcome_for(score))
```

- [ ] **Step 4: Correr tests**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_scoring.py -q`
Expected: `11 passed`

- [ ] **Step 5: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add backend/app/domains/governance/ucca/scoring.py backend/tests/test_ucca_scoring.py
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca): pure score/outcome calculation for chart audits

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Modelos y migración 0007

**Files:**
- Modify: `backend/app/domains/governance/ucca/models.py`
- Modify: `backend/app/domains/governance/corrective_actions/models.py`
- Create: `backend/alembic/versions/0007_ucca_chart_audits.py`
- Test: `backend/tests/test_ucca_models.py`

**Interfaces:**
- Produces: `ChartAudit` (tabla `ucca_chart_audits`), `AuditResult.chart_audit_id`, `AuditResult.comment`, `Finding.chart_audit_id`, `Finding.result_id` nullable, `CorrectiveAction.description/closure_evidence/closed_at`, `AuditCycle.year/quarter`.

- [ ] **Step 1: Test que falla (construcción de modelos)**

```python
# backend/tests/test_ucca_models.py
"""Los modelos UCCA exponen las columnas del diseño chart-audit (sin Postgres)."""
import uuid
from datetime import date


def test_chart_audit_columns():
    from app.domains.governance.ucca.models import ChartAudit

    audit = ChartAudit(
        cycle_id=uuid.uuid4(), facility_id=uuid.uuid4(), professional_id=uuid.uuid4(),
        auditor_user_id=uuid.uuid4(), case_reference="102453", audit_date=date(2026, 7, 20),
        status="draft", applicable_count=7, yes_count=7, score=100.0, outcome="compliant", notes="",
    )
    assert ChartAudit.__tablename__ == "ucca_chart_audits"
    assert audit.case_reference == "102453" and audit.score == 100.0


def test_result_finding_action_cycle_columns():
    from app.domains.governance.corrective_actions.models import CorrectiveAction
    from app.domains.governance.ucca.models import AuditCycle, AuditResult, Finding

    assert "chart_audit_id" in AuditResult.__table__.c and "comment" in AuditResult.__table__.c
    assert "chart_audit_id" in Finding.__table__.c and Finding.__table__.c.result_id.nullable
    for col in ("description", "closure_evidence", "closed_at"):
        assert col in CorrectiveAction.__table__.c
    assert "year" in AuditCycle.__table__.c and "quarter" in AuditCycle.__table__.c
```

- [ ] **Step 2: Correr y ver fallo**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_models.py -q`
Expected: `ImportError: cannot import name 'ChartAudit'`

- [ ] **Step 3: Modificar `ucca/models.py`**

Reemplazar `AuditCycle`, `AuditResult`, `Finding` y añadir `ChartAudit` (dejar `AuditTemplate`, `AuditTemplateVersion`, `AuditCriterion` como están). Añadir `Date, Numeric, Text, UniqueConstraint` al import de sqlalchemy.

```python
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func


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
```

- [ ] **Step 4: Modificar `corrective_actions/models.py`**

Añadir tras `status`:

```python
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    closure_evidence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    closed_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
```

- [ ] **Step 5: Migración**

```python
# backend/alembic/versions/0007_ucca_chart_audits.py
"""UCCA — auditoría por expediente (chart audit): cabecera con score/outcome, resultados ligados
a la cabecera, hallazgo a nivel expediente, acción correctiva con descripción/evidencia de
cierre, ciclo con año/trimestre. RLS por facility_id en la tabla nueva (patrón 0004).

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ciclo: año/trimestre con backfill desde period_label "Q3-2026"
    op.add_column("ucca_audit_cycles", sa.Column("year", sa.Integer(), nullable=True))
    op.add_column("ucca_audit_cycles", sa.Column("quarter", sa.String(2), nullable=True))
    op.execute(
        """
        UPDATE ucca_audit_cycles SET
            quarter = upper(split_part(period_label, '-', 1)),
            year = NULLIF(split_part(period_label, '-', 2), '')::int
        WHERE period_label ~* '^q[1-4]-\\d{4}$'
        """
    )
    op.execute("UPDATE ucca_audit_cycles SET year = 2026 WHERE year IS NULL")
    op.execute("UPDATE ucca_audit_cycles SET quarter = 'Q1' WHERE quarter IS NULL")
    op.alter_column("ucca_audit_cycles", "year", nullable=False)
    op.alter_column("ucca_audit_cycles", "quarter", nullable=False)

    # Cabecera por expediente
    op.create_table(
        "ucca_chart_audits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("cycle_id", UUID(as_uuid=True), sa.ForeignKey("ucca_audit_cycles.id"), nullable=False),
        sa.Column("facility_id", UUID(as_uuid=True), nullable=False),
        sa.Column("professional_id", UUID(as_uuid=True), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("auditor_user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("case_reference", sa.String(80), nullable=False),
        sa.Column("audit_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("applicable_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("yes_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("outcome", sa.String(40), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("cycle_id", "professional_id", "case_reference", name="uq_chart_audit_case"),
    )
    op.execute("ALTER TABLE ucca_chart_audits ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ucca_chart_audits FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY ucca_chart_audits_facility_scope ON ucca_chart_audits
        USING (
            current_setting('app.current_is_corporate', true) = 'true'
            OR facility_id::text = ANY (
                string_to_array(current_setting('app.current_facility_ids', true), ',')
            )
        );
        """
    )

    # Resultados: ahora siempre pertenecen a una cabecera. Tabla vacía en todos los entornos
    # conocidos; se limpian filas huérfanas (y sus hallazgos) antes de exigir la FK.
    op.execute("DELETE FROM ucca_findings WHERE result_id IS NOT NULL")
    op.execute("DELETE FROM ucca_audit_results")
    op.add_column(
        "ucca_audit_results",
        sa.Column("chart_audit_id", UUID(as_uuid=True), sa.ForeignKey("ucca_chart_audits.id"), nullable=False),
    )
    op.add_column("ucca_audit_results", sa.Column("comment", sa.String(500), nullable=True))
    op.create_unique_constraint("uq_result_audit_criterion", "ucca_audit_results", ["chart_audit_id", "criterion_id"])

    # Hallazgo a nivel expediente
    op.alter_column("ucca_findings", "result_id", nullable=True)
    op.add_column(
        "ucca_findings",
        sa.Column("chart_audit_id", UUID(as_uuid=True), sa.ForeignKey("ucca_chart_audits.id"), nullable=True),
    )
    op.create_check_constraint(
        "ck_finding_has_source", "ucca_findings", "chart_audit_id IS NOT NULL OR result_id IS NOT NULL"
    )

    # Acción correctiva (M06)
    op.add_column("corrective_actions", sa.Column("description", sa.String(1000), nullable=False, server_default=""))
    op.add_column("corrective_actions", sa.Column("closure_evidence", sa.String(1000), nullable=True))
    op.add_column("corrective_actions", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("corrective_actions", "closed_at")
    op.drop_column("corrective_actions", "closure_evidence")
    op.drop_column("corrective_actions", "description")
    op.drop_constraint("ck_finding_has_source", "ucca_findings", type_="check")
    op.drop_column("ucca_findings", "chart_audit_id")
    op.alter_column("ucca_findings", "result_id", nullable=False)
    op.drop_constraint("uq_result_audit_criterion", "ucca_audit_results", type_="unique")
    op.drop_column("ucca_audit_results", "comment")
    op.drop_column("ucca_audit_results", "chart_audit_id")
    op.execute("DROP POLICY IF EXISTS ucca_chart_audits_facility_scope ON ucca_chart_audits;")
    op.drop_table("ucca_chart_audits")
    op.drop_column("ucca_audit_cycles", "quarter")
    op.drop_column("ucca_audit_cycles", "year")
```

- [ ] **Step 6: Correr tests de modelos y suite completa**

Run: `cd backend && ./.venv/bin/python -m pytest -q`
Expected: todo verde (los tests existentes no tocan columnas eliminadas). Si `test_ucca_cycles.py` falla por `AuditCycleOut`, se arregla en Task 4.

- [ ] **Step 7: Aplicar migración en Postgres local y verificar**

Run (cwd `backend/`): `./.venv/bin/alembic upgrade head && psql -d aegis -Atc "select period_label, year, quarter from ucca_audit_cycles" -c "\d ucca_chart_audits" | head -30`
Expected: `Q3-2026|2026|Q3` y la tabla nueva listada con sus columnas.

- [ ] **Step 8: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add backend/app/domains backend/alembic/versions/0007_ucca_chart_audits.py backend/tests/test_ucca_models.py
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca): chart audit schema — header table, linked results, findings, cycle year/quarter

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Schemas, servicio y API de auditorías por expediente

**Files:**
- Modify: `backend/app/domains/governance/ucca/schemas.py` (reemplazar `AuditResult*` por los schemas de abajo; conservar `AuditCriterion*`)
- Modify: `backend/app/domains/governance/ucca/service.py` (eliminar `record_result`, `approve_result`, `get_result_or_404`, `list_results`; añadir lo de abajo)
- Modify: `backend/app/domains/governance/ucca/router.py` (eliminar rutas `/results*`; añadir rutas de auditoría)
- Test: `backend/tests/test_ucca_chart_audits.py`

**Interfaces:**
- Consumes: `compute_score`, modelos de Task 2, `record_event`, `get_or_404`, `domain_errors`.
- Produces (servicio): `create_chart_audit(db, *, actor_user_id, cycle, payload) -> dict`, `update_chart_audit(db, *, actor_user_id, audit, payload) -> dict`, `submit_chart_audit(db, *, actor_user_id, audit) -> dict`, `approve_chart_audit(db, *, actor_user_id, audit) -> dict`, `get_chart_audit_or_404(db, audit_id) -> ChartAudit`, `list_chart_audits(db, *, cycle_id) -> list[dict]`, `chart_audit_detail(db, audit) -> dict`.
- Produces (API): `GET /ucca/cycles/{id}/audits`, `POST /ucca/cycles/{id}/audits`, `GET /ucca/audits/{id}`, `PATCH /ucca/audits/{id}`, `POST /ucca/audits/{id}/submit`, `POST /ucca/audits/{id}/approve`.
- Orden de consultas del servicio (los tests con `FakeSession` dependen de él): ver comentarios `# scalar #n` en el código.

- [ ] **Step 1: Tests que fallan**

```python
# backend/tests/test_ucca_chart_audits.py
"""Auditoría por expediente: crear con 7 respuestas, score/outcome calculados, hallazgo + acción
correctiva, editar solo en borrador, enviar/aprobar. Sin Postgres (tests/_fakes.py)."""
import json
import uuid
from datetime import date

import pytest

from tests._fakes import DEV_USER_ID, FakeSession, cleanup, make_client

PERMS = frozenset({"ucca.view", "ucca.create", "ucca.approve"})
FACILITY = uuid.uuid4()
VERSION = uuid.uuid4()
CODES = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _cycle():
    from app.domains.governance.ucca.models import AuditCycle

    return AuditCycle(
        id=uuid.uuid4(), facility_id=FACILITY, template_version_id=VERSION, period_label="Q2-2026",
        year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.UUID(DEV_USER_ID),
    )


def _professional(facility=FACILITY, active=True):
    from app.domains.identity.models import Professional

    return Professional(
        id=uuid.uuid4(), employee_number="CL-0029", full_name="Dr. Divya Rani",
        profession_id=uuid.uuid4(), primary_facility_id=facility, scope_of_practice=[], is_active=active,
    )


def _criteria():
    from app.domains.governance.ucca.models import AuditCriterion

    return [
        AuditCriterion(id=uuid.uuid4(), template_version_id=VERSION, code=c, domain=c, universal_question="?",
                       profession_interpretation="", examples_evidence="", is_active=True)
        for c in CODES
    ]


def _answers(criteria, outcomes):
    return [
        {"criterion_id": str(c.id), "outcome": o, "not_applicable_reason": "Fuera de alcance" if o == "not_applicable" else None}
        for c, o in zip(criteria, outcomes)
    ]


def _payload(criteria, outcomes, finding=None):
    body = {
        "professional_id": str(_PRO.id), "case_reference": "102453", "audit_date": "2026-07-20",
        "notes": "", "answers": _answers(criteria, outcomes),
    }
    if finding is not None:
        body["finding"] = finding
    return body


_PRO = _professional()


def _events(session):
    return [p for _, p in session.executed if p and "action" in p]


def _create_session(cycle, professional, criteria, duplicate=None):
    # scalar #1 ciclo (router) · #2 profesional · #3 duplicado · scalars #1 criterios
    return FakeSession(scalar_results=[cycle, professional, duplicate], scalars_results=[criteria])


def test_create_all_yes_is_compliant(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    session = _create_session(cycle, _PRO, criteria)
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["compliant"] * 7))
    assert r.status_code == 201, r.text
    body = r.json()
    assert (body["applicable_count"], body["yes_count"], body["score"], body["outcome"]) == (7, 7, 100.0, "compliant")
    assert body["status"] == "draft" and body["employee_number"] == "CL-0029"
    assert {a["criterion_code"] for a in body["answers"]} == set(CODES)
    from app.domains.governance.ucca.models import AuditResult, ChartAudit

    assert sum(isinstance(o, ChartAudit) for o in session.added) == 1
    assert sum(isinstance(o, AuditResult) for o in session.added) == 7
    assert {e["entity_type"] for e in _events(session)} >= {"ChartAudit"}
    assert session.committed


def test_create_with_na_and_no_requires_finding(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    outcomes = ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"]  # 4/6 = 66.67
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, outcomes))
    assert r.status_code == 422 and "hallazgo" in r.json()["detail"].lower()


def test_create_with_finding_and_action(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    outcomes = ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"]
    owner = uuid.uuid4()
    finding = {
        "description": "Risk assessment missing",
        "corrective_action": {"description": "Retrain on risk documentation", "responsible_user_id": str(owner),
                              "due_date": "2026-08-30", "status": "assigned"},
    }
    session = _create_session(cycle, _PRO, criteria)
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, outcomes, finding))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["score"] == 66.67 and body["outcome"] == "priority_corrective_action"
    assert body["finding"]["description"] == "Risk assessment missing"
    assert body["finding"]["corrective_action"]["status"] == "assigned"
    from app.domains.governance.corrective_actions.models import CorrectiveAction
    from app.domains.governance.ucca.models import Finding

    assert any(isinstance(o, Finding) and o.chart_audit_id is not None for o in session.added)
    ca = next(o for o in session.added if isinstance(o, CorrectiveAction))
    assert ca.source_module == "ucca" and ca.responsible_user_id == owner and ca.description.startswith("Retrain")


def test_create_all_na_no_finding_required(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["not_applicable"] * 7))
    assert r.status_code == 201, r.text
    assert r.json()["score"] is None and r.json()["outcome"] is None


def test_create_na_without_reason_422(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    body = _payload(criteria, ["compliant"] * 6 + ["not_applicable"])
    body["answers"][6]["not_applicable_reason"] = "   "
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def test_create_rejects_unknown_or_duplicate_criterion(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    body = _payload(criteria, ["compliant"] * 7)
    body["answers"][0]["criterion_id"] = str(uuid.uuid4())  # ajeno
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422
    body = _payload(criteria, ["compliant"] * 7)
    body["answers"][1]["criterion_id"] = body["answers"][0]["criterion_id"]  # repetido
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def test_create_duplicate_case_409(monkeypatch):
    from app.domains.governance.ucca.models import ChartAudit

    cycle, criteria = _cycle(), _criteria()
    existing = ChartAudit(id=uuid.uuid4(), cycle_id=cycle.id, facility_id=FACILITY, professional_id=_PRO.id,
                          auditor_user_id=uuid.uuid4(), case_reference="102453", audit_date=date.today(), status="draft")
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria, duplicate=existing), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["compliant"] * 7)).status_code == 409


def test_create_professional_other_facility_422(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    other = _professional(facility=uuid.uuid4())
    client = make_client(monkeypatch, _create_session(cycle, other, criteria), PERMS)
    body = _payload(criteria, ["compliant"] * 7)
    body["professional_id"] = str(other.id)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def _existing_audit(cycle, status="draft"):
    from app.domains.governance.ucca.models import ChartAudit

    return ChartAudit(id=uuid.uuid4(), cycle_id=cycle.id, facility_id=FACILITY, professional_id=_PRO.id,
                      auditor_user_id=uuid.UUID(DEV_USER_ID), case_reference="102453", audit_date=date(2026, 7, 20),
                      status=status, applicable_count=7, yes_count=7, score=100.0, outcome="compliant", notes="")


def _existing_results(audit, criteria):
    from app.domains.governance.ucca.models import AuditResult

    return [AuditResult(id=uuid.uuid4(), chart_audit_id=audit.id, facility_id=FACILITY, cycle_id=audit.cycle_id,
                        criterion_id=c.id, professional_id=_PRO.id, auditor_user_id=audit.auditor_user_id,
                        outcome="compliant", status="draft") for c in criteria]


def test_update_replaces_answers_and_recomputes(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    old_results = _existing_results(audit, criteria)
    # scalar #1 auditoría (router) · #2 ciclo · #3 profesional · #4 duplicado (None)
    # scalars #1 criterios · #2 resultados previos · scalar #5 finding previo (None)
    session = FakeSession(scalar_results=[audit, cycle, _PRO, None, None], scalars_results=[criteria, old_results])
    client = make_client(monkeypatch, session, PERMS)
    outcomes = ["compliant"] * 6 + ["non_compliant"]  # 6/7 = 85.71
    r = client.patch(f"/ucca/audits/{audit.id}", json=_payload(criteria, outcomes, {"description": "CMC gap"}))
    assert r.status_code == 200, r.text
    assert r.json()["score"] == 85.71 and r.json()["outcome"] == "minor_improvement"
    assert len(session.deleted) == 7  # respuestas viejas fuera
    from app.domains.governance.ucca.models import AuditResult

    assert sum(isinstance(o, AuditResult) for o in session.added) == 7
    update = next(e for e in _events(session) if e["entity_type"] == "ChartAudit" and e["action"] == "update")
    assert json.loads(update["new_values"])["score"] == "85.71"


def test_update_approved_409(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle, status="approved")
    client = make_client(monkeypatch, FakeSession(scalar_results=[audit]), PERMS)
    assert client.patch(f"/ucca/audits/{audit.id}", json=_payload(criteria, ["compliant"] * 7)).status_code == 409


def test_submit_then_approve(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    results = _existing_results(audit, criteria)
    # submit: scalar #1 auditoría · scalars #1 resultados · (detalle) scalar #2 profesional, #3 auditor name, scalars #2 answers rows, scalar #4 finding
    session = FakeSession(scalar_results=[audit, _PRO, "Dev", None], scalars_results=[results, []])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/audits/{audit.id}/submit")
    assert r.status_code == 200, r.text and r.json()["status"] == "submitted"
    assert all(res.status == "submitted" for res in results)

    session = FakeSession(scalar_results=[audit, _PRO, "Dev", None], scalars_results=[results, []])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/audits/{audit.id}/approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved" and all(res.status == "approved" for res in results)
    assert any(e["action"] == "approve" for e in _events(session))


def test_approve_from_draft_409(monkeypatch):
    cycle = _cycle()
    audit = _existing_audit(cycle, status="draft")
    client = make_client(monkeypatch, FakeSession(scalar_results=[audit]), PERMS)
    assert client.post(f"/ucca/audits/{audit.id}/approve").status_code == 409


def test_list_chart_audits_rows(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    header_rows = [(audit, "Dr. Divya Rani", "CL-0029", "Psychiatrist", "Dr Ramez Abu Sabha")]
    answer_rows = [(audit.id, c.code, "compliant") for c in criteria]
    finding_rows = []
    session = FakeSession(scalar_results=[cycle], execute_rows=[header_rows, answer_rows, finding_rows])
    client = make_client(monkeypatch, session, PERMS)
    r = client.get(f"/ucca/cycles/{cycle.id}/audits")
    assert r.status_code == 200, r.text
    row = r.json()[0]
    assert row["employee_number"] == "CL-0029" and row["profession_name"] == "Psychiatrist"
    assert row["answers"] == {c: "compliant" for c in CODES}
    assert row["score"] == 100.0 and row["outcome"] == "compliant" and row["has_finding"] is False
```

- [ ] **Step 2: Correr y ver fallo**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_chart_audits.py -q`
Expected: fallos 404/422 (rutas inexistentes) y errores de import de schemas.

- [ ] **Step 3: Schemas**

En `schemas.py` borrar `AuditResultCreateRequest`, `AuditResultOut`, `AuditResultDetailOut`, `AuditResultApproveRequest` y añadir (import `date` de `datetime` y `Literal` de `typing`, `Field` ya importado):

```python
from datetime import date
from typing import Literal

AnswerValue = Literal["compliant", "non_compliant", "not_applicable"]
ActionStatus = Literal["assigned", "in_progress", "closed"]


class AnswerIn(BaseModel):
    criterion_id: uuid.UUID
    outcome: AnswerValue
    not_applicable_reason: str | None = Field(default=None, max_length=500)
    comment: str | None = Field(default=None, max_length=500)


class CorrectiveActionIn(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    responsible_user_id: uuid.UUID
    due_date: date
    status: ActionStatus = "assigned"
    closure_evidence: str | None = Field(default=None, max_length=1000)


class FindingIn(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    corrective_action: CorrectiveActionIn | None = None


class ChartAuditWriteRequest(BaseModel):
    professional_id: uuid.UUID
    case_reference: str = Field(min_length=1, max_length=80)
    audit_date: date
    notes: str = Field(default="", max_length=1000)
    answers: list[AnswerIn]
    finding: FindingIn | None = None


class AnswerOut(BaseModel):
    criterion_id: uuid.UUID
    criterion_code: str
    outcome: str
    not_applicable_reason: str | None = None
    comment: str | None = None


class CorrectiveActionOut(BaseModel):
    id: uuid.UUID
    description: str
    responsible_user_id: uuid.UUID
    responsible_name: str | None = None
    due_date: date
    status: str
    closure_evidence: str | None = None


class FindingOut(BaseModel):
    id: uuid.UUID
    description: str
    status: str
    corrective_action: CorrectiveActionOut | None = None


class ChartAuditOut(BaseModel):
    id: uuid.UUID
    cycle_id: uuid.UUID
    facility_id: uuid.UUID
    professional_id: uuid.UUID
    professional_name: str
    employee_number: str
    profession_name: str | None = None
    auditor_user_id: uuid.UUID
    auditor_name: str | None = None
    case_reference: str
    audit_date: date
    status: str
    applicable_count: int
    yes_count: int
    score: float | None = None
    outcome: str | None = None
    notes: str = ""
    answers: list[AnswerOut]
    finding: FindingOut | None = None


class ChartAuditRowOut(BaseModel):
    """Fila de la tabla tipo Excel: respuestas como {codigo: outcome}."""
    id: uuid.UUID
    professional_id: uuid.UUID
    professional_name: str
    employee_number: str
    profession_name: str | None = None
    auditor_name: str | None = None
    case_reference: str
    audit_date: date
    status: str
    applicable_count: int
    yes_count: int
    score: float | None = None
    outcome: str | None = None
    answers: dict[str, str]
    has_finding: bool
```

- [ ] **Step 4: Servicio**

En `service.py`: borrar `record_result`, `approve_result`, `get_result_or_404`, `list_results`. Añadir imports y funciones:

```python
from datetime import datetime, timezone

from app.core.master_data import get_or_404
from app.domains.governance.corrective_actions.models import CorrectiveAction
from app.domains.governance.ucca.models import ChartAudit  # añadir al import existente
from app.domains.governance.ucca.scoring import ANSWER_NA, ANSWER_NO, compute_score
from app.domains.governance.ucca.schemas import ChartAuditWriteRequest
from app.domains.identity.models import Profession, Professional, User


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
                **_score_values(compute_score([]))}
    previous.update({"applicable_count": str(audit.applicable_count), "yes_count": str(audit.yes_count),
                     "score": None if audit.score is None else f"{float(audit.score):.2f}", "outcome": audit.outcome})
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
    """Detalle completo desde DB. Orden: scalar profesional · scalar nombre auditor · scalars respuestas · scalar finding."""
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
```

Nota sobre `chart_audit_detail` con fakes en `test_submit_then_approve`: el orden de consultas es scalar profesional → scalar auditor → (profession_id: `_PRO.profession_id` no es None → scalar nombre profesión) → scalars resultados → scalars criterios → scalar finding. Ajustar el test a `scalar_results=[audit, _PRO, "Dev", "Psychiatry", None]` y `scalars_results=[results, results, []]` si el primer intento falla por el orden; el objetivo es que `_transition` y `chart_audit_detail` sigan el orden documentado en sus docstrings.

- [ ] **Step 5: Router**

Eliminar `list_results`, `record_result`, `approve_result`. Añadir (import `domain_errors` ya existe desde Task anterior; añadir `from fastapi import Body`):

```python
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
```

`get_cycle_or_404` en el servicio lanza `HTTPException` 404 directamente (ya existe); se conserva.

- [ ] **Step 6: Correr tests y suite completa**

Run: `cd backend && ./.venv/bin/python -m pytest -q`
Expected: todo verde (ajustar el orden de `scalar_results` en `test_submit_then_approve` según la nota del Step 4 si hace falta; no cambiar el orden del servicio).

- [ ] **Step 7: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add backend/app/domains/governance/ucca backend/tests/test_ucca_chart_audits.py
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca): chart audit API — create/edit/submit/approve with score, outcome and findings

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Ciclos con año/trimestre y listado enriquecido

**Files:**
- Modify: `backend/app/domains/governance/ucca/schemas.py` (`AuditCycleCreateRequest`, `AuditCycleOut`)
- Modify: `backend/app/domains/governance/ucca/service.py` (`create_cycle`, `list_cycles`)
- Modify: `backend/app/domains/governance/ucca/router.py` (`create_cycle`, `list_cycles`)
- Modify: `backend/tests/test_ucca_cycles.py` (el monkeypatch de `list_cycles` devuelve `[]`; sigue válido)
- Test: `backend/tests/test_ucca_cycles_create.py`

**Interfaces:**
- Produces: `POST /ucca/cycles` body `{facility_id, year, quarter}`; `AuditCycleOut` con `year`, `quarter`, `facility_name`, `audits_count`, `average_score`, `template_version_id`.
- `create_cycle(db, *, actor_user_id, facility_id, year, quarter) -> dict` — orden: scalar duplicado · scalar versión vigente · scalar nombre centro.
- `list_cycles(db) -> list[dict]` — un `execute()` con filas `(AuditCycle, facility_name, audits_count, average_score)`.

- [ ] **Step 1: Tests que fallan**

```python
# backend/tests/test_ucca_cycles_create.py
"""Ciclos UCCA: creación por centro + año + trimestre, etiqueta derivada, duplicado 409."""
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client

PERMS = frozenset({"ucca.view", "ucca.create"})


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _version():
    from app.domains.governance.ucca.models import AuditTemplateVersion

    return AuditTemplateVersion(id=uuid.uuid4(), template_id=uuid.uuid4(), version_number=1, is_current=True)


def test_create_cycle_derives_period_label(monkeypatch):
    facility = uuid.uuid4()
    # scalar #1 duplicado (None) · #2 versión vigente · #3 nombre del centro
    session = FakeSession(scalar_results=[None, _version(), "Al Bateen"])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(facility), "year": 2026, "quarter": "Q2"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["period_label"] == "Q2-2026" and body["year"] == 2026 and body["quarter"] == "Q2"
    assert body["facility_name"] == "Al Bateen" and body["audits_count"] == 0 and body["average_score"] is None
    assert session.committed


def test_create_cycle_duplicate_409(monkeypatch):
    from app.domains.governance.ucca.models import AuditCycle

    facility = uuid.uuid4()
    existing = AuditCycle(id=uuid.uuid4(), facility_id=facility, template_version_id=uuid.uuid4(),
                          period_label="Q2-2026", year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.uuid4())
    client = make_client(monkeypatch, FakeSession(scalar_results=[existing]), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(facility), "year": 2026, "quarter": "Q2"})
    assert r.status_code == 409


def test_create_cycle_invalid_quarter_422(monkeypatch):
    client = make_client(monkeypatch, FakeSession(), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(uuid.uuid4()), "year": 2026, "quarter": "Q5"})
    assert r.status_code == 422


def test_create_cycle_without_template_422(monkeypatch):
    client = make_client(monkeypatch, FakeSession(scalar_results=[None, None]), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(uuid.uuid4()), "year": 2026, "quarter": "Q1"})
    assert r.status_code == 422


def test_list_cycles_enriched(monkeypatch):
    from app.domains.governance.ucca.models import AuditCycle

    cycle = AuditCycle(id=uuid.uuid4(), facility_id=uuid.uuid4(), template_version_id=uuid.uuid4(),
                       period_label="Q2-2026", year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.uuid4())
    session = FakeSession(execute_rows=[[(cycle, "Al Bateen", 5, 92.5)]])
    client = make_client(monkeypatch, session, PERMS)
    r = client.get("/ucca/cycles")
    assert r.status_code == 200, r.text
    row = r.json()[0]
    assert row["facility_name"] == "Al Bateen" and row["audits_count"] == 5 and row["average_score"] == 92.5
```

- [ ] **Step 2: Correr y ver fallo**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_cycles_create.py -q`
Expected: 422 por body distinto / claves ausentes.

- [ ] **Step 3: Schemas**

Reemplazar `AuditCycleCreateRequest` y `AuditCycleOut`:

```python
Quarter = Literal["Q1", "Q2", "Q3", "Q4"]


class AuditCycleCreateRequest(BaseModel):
    facility_id: uuid.UUID
    year: int = Field(ge=2020, le=2100)
    quarter: Quarter


class AuditCycleOut(BaseModel):
    id: uuid.UUID
    facility_id: uuid.UUID
    facility_name: str | None = None
    template_version_id: uuid.UUID
    period_label: str
    year: int
    quarter: str
    status: str
    audits_count: int = 0
    average_score: float | None = None
```

- [ ] **Step 4: Servicio**

Reemplazar `create_cycle` y `list_cycles`:

```python
from sqlalchemy import func  # añadir al import de sqlalchemy
from app.domains.identity.models import Facility  # añadir al import de identity.models


def _cycle_out(cycle: AuditCycle, facility_name: str | None, audits_count: int, average_score) -> dict:
    return {
        "id": cycle.id, "facility_id": cycle.facility_id, "facility_name": facility_name,
        "template_version_id": cycle.template_version_id, "period_label": cycle.period_label,
        "year": cycle.year, "quarter": cycle.quarter, "status": cycle.status,
        "audits_count": int(audits_count or 0),
        "average_score": None if average_score is None else round(float(average_score), 2),
    }


def create_cycle(db: Session, *, actor_user_id: uuid.UUID, facility_id: uuid.UUID, year: int, quarter: str) -> dict:
    """Orden de consultas: duplicado · versión vigente · nombre del centro."""
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
```

- [ ] **Step 5: Router**

```python
@router.get("/cycles", response_model=list[schemas.AuditCycleOut])
def list_cycles(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> list[schemas.AuditCycleOut]:
    return [schemas.AuditCycleOut.model_validate(row) for row in service.list_cycles(db)]


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
```

- [ ] **Step 6: Correr suite completa**

Run: `cd backend && ./.venv/bin/python -m pytest -q`
Expected: todo verde.

- [ ] **Step 7: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add backend/app/domains/governance/ucca backend/tests/test_ucca_cycles_create.py
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca): cycles by facility + year + quarter with audit counts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Agregados — `summary.py` puro, `GET /cycles/{id}/summary`, `GET /dashboard`

**Files:**
- Create: `backend/app/domains/governance/ucca/summary.py`
- Modify: `backend/app/domains/governance/ucca/schemas.py` (schemas de summary)
- Modify: `backend/app/domains/governance/ucca/service.py` (`cycle_summary`, `dashboard`)
- Modify: `backend/app/domains/governance/ucca/router.py`
- Test: `backend/tests/test_ucca_summary.py`

**Interfaces:**
- Produces (puro): `summarize(audits: list[AuditRow], answers: list[AnswerRow], criteria_codes: list[str], open_actions: list[OpenActionRow]) -> dict` con claves `audits_count, draft_count, average_score, outcome_distribution, criteria, professionals, trend, open_corrective_actions`.
- `AuditRow(id, professional_id, employee_number, professional_name, profession_name, status, score, outcome, year, quarter)`, `AnswerRow(audit_id, code, outcome)`, `OpenActionRow(id, audit_id, case_reference, professional_name, finding, responsible_name, due_date, status)`.
- Produces (API): `GET /ucca/cycles/{id}/summary` y `GET /ucca/dashboard?facility_id=&year=&quarter=` → `SummaryOut`.

- [ ] **Step 1: Tests que fallan**

```python
# backend/tests/test_ucca_summary.py
"""Agregados UCCA: solo auditorías enviadas/aprobadas; % por criterio; por profesional; tendencia."""
import uuid
from datetime import date

from app.domains.governance.ucca.summary import AnswerRow, AuditRow, OpenActionRow, summarize

CODES = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]
P1, P2 = uuid.uuid4(), uuid.uuid4()


def _audit(aid, pro, status, score, outcome, quarter="Q2"):
    name = "Dr. Divya Rani" if pro == P1 else "Dr. Ahmed"
    return AuditRow(id=aid, professional_id=pro, employee_number="CL-0029" if pro == P1 else "CL-0030",
                    professional_name=name, profession_name="Psychiatrist", status=status, score=score,
                    outcome=outcome, year=2026, quarter=quarter)


def _answers(aid, outcomes):
    return [AnswerRow(audit_id=aid, code=c, outcome=o) for c, o in zip(CODES, outcomes)]


def test_summarize_empty():
    s = summarize([], [], CODES, [])
    assert s["audits_count"] == 0 and s["draft_count"] == 0 and s["average_score"] is None
    assert s["outcome_distribution"] == {"compliant": 0, "minor_improvement": 0, "improvement_required": 0, "priority_corrective_action": 0}
    assert [c["code"] for c in s["criteria"]] == CODES and all(c["yes_rate"] is None for c in s["criteria"])
    assert s["professionals"] == [] and s["trend"] == [] and s["open_corrective_actions"] == []


def test_summarize_ignores_drafts():
    a1, a2 = uuid.uuid4(), uuid.uuid4()
    audits = [_audit(a1, P1, "approved", 100.0, "compliant"), _audit(a2, P1, "draft", 50.0, "priority_corrective_action")]
    answers = _answers(a1, ["compliant"] * 7) + _answers(a2, ["non_compliant"] * 7)
    s = summarize(audits, answers, CODES, [])
    assert s["audits_count"] == 1 and s["draft_count"] == 1 and s["average_score"] == 100.0
    assert s["criteria"][0]["yes_rate"] == 100.0


def test_summarize_by_criterion_and_professional():
    a1, a2, a3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    audits = [
        _audit(a1, P1, "approved", 100.0, "compliant"),
        _audit(a2, P1, "submitted", 66.67, "priority_corrective_action"),
        _audit(a3, P2, "approved", 85.71, "minor_improvement", quarter="Q3"),
    ]
    answers = (
        _answers(a1, ["compliant"] * 7)
        + _answers(a2, ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"])
        + _answers(a3, ["compliant"] * 6 + ["non_compliant"])
    )
    s = summarize(audits, answers, CODES, [])
    assert s["audits_count"] == 3 and s["average_score"] == 84.13
    assert s["outcome_distribution"]["compliant"] == 1 and s["outcome_distribution"]["priority_corrective_action"] == 1
    cdc = next(c for c in s["criteria"] if c["code"] == "CDC")
    assert (cdc["applicable"], cdc["yes"], cdc["yes_rate"]) == (2, 2, 100.0)  # a2 fue N/A
    cmc = next(c for c in s["criteria"] if c["code"] == "CMC")
    assert (cmc["applicable"], cmc["yes"], cmc["yes_rate"]) == (3, 1, 33.33)
    p1 = next(p for p in s["professionals"] if p["professional_id"] == P1)
    assert p1["audits_count"] == 2 and p1["average_score"] == 83.34 and p1["outcome"] == "minor_improvement"
    assert p1["criteria"]["CDC"] == 100.0 and p1["criteria"]["CMC"] == 50.0
    assert s["trend"] == [{"year": 2026, "quarter": "Q2", "audits_count": 2, "average_score": 83.34},
                          {"year": 2026, "quarter": "Q3", "audits_count": 1, "average_score": 85.71}]


def test_summarize_open_actions_passthrough():
    row = OpenActionRow(id=uuid.uuid4(), audit_id=uuid.uuid4(), case_reference="102453", professional_name="Dr. Divya Rani",
                        finding="Risk missing", responsible_name="Sara", due_date=date(2026, 8, 30), status="assigned")
    s = summarize([], [], CODES, [row])
    assert s["open_corrective_actions"][0]["case_reference"] == "102453"
```

- [ ] **Step 2: Correr y ver fallo**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_summary.py -q`
Expected: `ModuleNotFoundError: ...ucca.summary`

- [ ] **Step 3: Implementar `summary.py`**

```python
# backend/app/domains/governance/ucca/summary.py
"""Agregados UCCA (summary por ciclo y dashboard). Función pura sobre filas simples para poder
probarla sin DB. Solo cuentan auditorías `submitted`/`approved`; los borradores se reportan aparte."""
from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date

from app.domains.governance.ucca.scoring import ANSWER_NA, ANSWER_YES, OUTCOME_VALUES, outcome_for

COUNTED_STATUSES = ("submitted", "approved")


@dataclass(frozen=True)
class AuditRow:
    id: uuid.UUID
    professional_id: uuid.UUID
    employee_number: str
    professional_name: str
    profession_name: str | None
    status: str
    score: float | None
    outcome: str | None
    year: int
    quarter: str


@dataclass(frozen=True)
class AnswerRow:
    audit_id: uuid.UUID
    code: str
    outcome: str


@dataclass(frozen=True)
class OpenActionRow:
    id: uuid.UUID
    audit_id: uuid.UUID
    case_reference: str
    professional_name: str
    finding: str
    responsible_name: str | None
    due_date: date
    status: str


def _avg(values: list[float]) -> float | None:
    return None if not values else round(sum(values) / len(values), 2)


def _rate(yes: int, applicable: int) -> float | None:
    return None if applicable == 0 else round(yes / applicable * 100, 2)


def summarize(audits: list[AuditRow], answers: list[AnswerRow], criteria_codes: list[str],
              open_actions: list[OpenActionRow]) -> dict:
    counted = [a for a in audits if a.status in COUNTED_STATUSES]
    counted_ids = {a.id for a in counted}
    draft_count = sum(1 for a in audits if a.status == "draft")

    distribution = {o: 0 for o in OUTCOME_VALUES}
    for a in counted:
        if a.outcome in distribution:
            distribution[a.outcome] += 1

    # por criterio
    crit_app: dict[str, int] = defaultdict(int)
    crit_yes: dict[str, int] = defaultdict(int)
    # por profesional y criterio
    pro_app: dict[tuple, int] = defaultdict(int)
    pro_yes: dict[tuple, int] = defaultdict(int)
    audit_pro = {a.id: a.professional_id for a in counted}
    for ans in answers:
        if ans.audit_id not in counted_ids:
            continue
        pro = audit_pro[ans.audit_id]
        if ans.outcome != ANSWER_NA:
            crit_app[ans.code] += 1
            pro_app[(pro, ans.code)] += 1
            if ans.outcome == ANSWER_YES:
                crit_yes[ans.code] += 1
                pro_yes[(pro, ans.code)] += 1

    criteria = [
        {"code": code, "applicable": crit_app[code], "yes": crit_yes[code], "yes_rate": _rate(crit_yes[code], crit_app[code])}
        for code in criteria_codes
    ]

    by_pro: dict[uuid.UUID, list[AuditRow]] = defaultdict(list)
    for a in counted:
        by_pro[a.professional_id].append(a)
    professionals = []
    for pro_id, rows in by_pro.items():
        scores = [r.score for r in rows if r.score is not None]
        avg = _avg(scores)
        professionals.append({
            "professional_id": pro_id, "employee_number": rows[0].employee_number,
            "professional_name": rows[0].professional_name, "profession_name": rows[0].profession_name,
            "audits_count": len(rows), "average_score": avg, "outcome": outcome_for(avg),
            "criteria": {code: _rate(pro_yes[(pro_id, code)], pro_app[(pro_id, code)]) for code in criteria_codes},
        })
    professionals.sort(key=lambda p: p["professional_name"])

    by_period: dict[tuple[int, str], list[float]] = defaultdict(list)
    period_counts: dict[tuple[int, str], int] = defaultdict(int)
    for a in counted:
        period_counts[(a.year, a.quarter)] += 1
        if a.score is not None:
            by_period[(a.year, a.quarter)].append(a.score)
    trend = [
        {"year": y, "quarter": q, "audits_count": period_counts[(y, q)], "average_score": _avg(by_period[(y, q)])}
        for (y, q) in sorted(period_counts)
    ]

    return {
        "audits_count": len(counted),
        "draft_count": draft_count,
        "average_score": _avg([a.score for a in counted if a.score is not None]),
        "outcome_distribution": distribution,
        "criteria": criteria,
        "professionals": professionals,
        "trend": trend,
        "open_corrective_actions": [asdict(r) for r in open_actions],
    }
```

- [ ] **Step 4: Correr tests puros**

Run: `cd backend && ./.venv/bin/python -m pytest tests/test_ucca_summary.py -q`
Expected: `4 passed`

- [ ] **Step 5: Schemas de salida**

```python
class CriterionStatOut(BaseModel):
    code: str
    applicable: int
    yes: int
    yes_rate: float | None = None


class ProfessionalStatOut(BaseModel):
    professional_id: uuid.UUID
    employee_number: str
    professional_name: str
    profession_name: str | None = None
    audits_count: int
    average_score: float | None = None
    outcome: str | None = None
    criteria: dict[str, float | None]


class TrendPointOut(BaseModel):
    year: int
    quarter: str
    audits_count: int
    average_score: float | None = None


class OpenActionOut(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    case_reference: str
    professional_name: str
    finding: str
    responsible_name: str | None = None
    due_date: date
    status: str


class SummaryOut(BaseModel):
    audits_count: int
    draft_count: int
    average_score: float | None = None
    outcome_distribution: dict[str, int]
    criteria: list[CriterionStatOut]
    professionals: list[ProfessionalStatOut]
    trend: list[TrendPointOut]
    open_corrective_actions: list[OpenActionOut]
```

- [ ] **Step 6: Servicio — carga de filas y wrappers**

```python
from app.domains.governance.ucca.summary import AnswerRow, AuditRow, OpenActionRow, summarize


def _load_summary_rows(db: Session, *, cycle_ids: list[uuid.UUID] | None, facility_id, year, quarter) -> dict:
    """Tres execute(): auditorías · respuestas · acciones abiertas. Filtros opcionales por ciclo/centro/periodo."""
    audit_stmt = (
        select(ChartAudit, Professional.employee_number, Professional.full_name, Profession.name, AuditCycle.year, AuditCycle.quarter)
        .join(Professional, Professional.id == ChartAudit.professional_id)
        .join(Profession, Profession.id == Professional.profession_id, isouter=True)
        .join(AuditCycle, AuditCycle.id == ChartAudit.cycle_id)
    )
    if cycle_ids is not None:
        audit_stmt = audit_stmt.where(ChartAudit.cycle_id.in_(cycle_ids))
    if facility_id is not None:
        audit_stmt = audit_stmt.where(ChartAudit.facility_id == facility_id)
    if year is not None:
        audit_stmt = audit_stmt.where(AuditCycle.year == year)
    if quarter is not None:
        audit_stmt = audit_stmt.where(AuditCycle.quarter == quarter)
    audit_rows = db.execute(audit_stmt).all()
    audits = [
        AuditRow(id=a.id, professional_id=a.professional_id, employee_number=emp, professional_name=name,
                 profession_name=prof, status=a.status, score=None if a.score is None else float(a.score),
                 outcome=a.outcome, year=y, quarter=q)
        for a, emp, name, prof, y, q in audit_rows
    ]
    ids = [a.id for a in audits]
    answers = []
    if ids:
        answers = [
            AnswerRow(audit_id=aid, code=code, outcome=outcome)
            for aid, code, outcome in db.execute(
                select(AuditResult.chart_audit_id, AuditCriterion.code, AuditResult.outcome)
                .join(AuditCriterion, AuditCriterion.id == AuditResult.criterion_id)
                .where(AuditResult.chart_audit_id.in_(ids))
            ).all()
        ]
    open_actions = []
    if ids:
        open_actions = [
            OpenActionRow(id=ca.id, audit_id=audit_id, case_reference=case_ref, professional_name=pro_name,
                          finding=finding_text, responsible_name=resp, due_date=ca.due_date, status=ca.status)
            for ca, audit_id, case_ref, pro_name, finding_text, resp in db.execute(
                select(CorrectiveAction, Finding.chart_audit_id, ChartAudit.case_reference, Professional.full_name,
                       Finding.description, User.full_name)
                .join(Finding, Finding.id == CorrectiveAction.source_finding_id)
                .join(ChartAudit, ChartAudit.id == Finding.chart_audit_id)
                .join(Professional, Professional.id == ChartAudit.professional_id)
                .join(User, User.id == CorrectiveAction.responsible_user_id, isouter=True)
                .where(Finding.chart_audit_id.in_(ids), CorrectiveAction.status != "closed")
                .order_by(CorrectiveAction.due_date)
            ).all()
        ]
    return {"audits": audits, "answers": answers, "open_actions": open_actions}


def _criteria_codes(db: Session, template_version_id: uuid.UUID | None) -> list[str]:
    if template_version_id is None:
        version = _current_template_version(db)
        template_version_id = version.id if version else None
    if template_version_id is None:
        return []
    return [c.code for c in _active_criteria(db, template_version_id)]


def cycle_summary(db: Session, cycle: AuditCycle) -> dict:
    codes = _criteria_codes(db, cycle.template_version_id)
    rows = _load_summary_rows(db, cycle_ids=[cycle.id], facility_id=None, year=None, quarter=None)
    return summarize(rows["audits"], rows["answers"], codes, rows["open_actions"])


def dashboard(db: Session, *, facility_id: uuid.UUID | None, year: int | None, quarter: str | None) -> dict:
    codes = _criteria_codes(db, None)
    rows = _load_summary_rows(db, cycle_ids=None, facility_id=facility_id, year=year, quarter=quarter)
    return summarize(rows["audits"], rows["answers"], codes, rows["open_actions"])
```

- [ ] **Step 7: Router**

```python
@router.get("/cycles/{cycle_id}/summary", response_model=schemas.SummaryOut)
def cycle_summary(
    cycle_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> schemas.SummaryOut:
    cycle = service.get_cycle_or_404(db, cycle_id)
    require_facility_access(str(cycle.facility_id), current_user)
    return schemas.SummaryOut.model_validate(service.cycle_summary(db, cycle))


@router.get("/dashboard", response_model=schemas.SummaryOut)
def dashboard(
    facility_id: uuid.UUID | None = Query(default=None),
    year: int | None = Query(default=None),
    quarter: str | None = Query(default=None, pattern="^Q[1-4]$"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("ucca.view")),
) -> schemas.SummaryOut:
    if facility_id is not None:
        require_facility_access(str(facility_id), current_user)
    return schemas.SummaryOut.model_validate(service.dashboard(db, facility_id=facility_id, year=year, quarter=quarter))
```

Añadir al final de `test_ucca_summary.py` un test de router con fakes:

```python
def test_dashboard_endpoint_empty(monkeypatch):
    import pytest as _pytest  # noqa: F401
    from tests._fakes import FakeSession, cleanup, make_client

    # scalar #1 versión vigente (None → sin criterios) · execute #1 auditorías vacías
    client = make_client(monkeypatch, FakeSession(scalar_results=[None], execute_rows=[[]]), frozenset({"ucca.view"}))
    try:
        r = client.get("/ucca/dashboard?year=2026&quarter=Q2")
        assert r.status_code == 200, r.text
        assert r.json()["audits_count"] == 0 and r.json()["criteria"] == []
        assert client.get("/ucca/dashboard?quarter=Q9").status_code == 422
    finally:
        cleanup()
```

- [ ] **Step 8: Correr suite completa y commit**

Run: `cd backend && ./.venv/bin/python -m pytest -q` → todo verde.

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add backend/app/domains/governance/ucca backend/tests/test_ucca_summary.py
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca): cycle summary and dashboard aggregates

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Frontend base — tipos, scoring en cliente, hook `useApiGet`, i18n, rutas, página de ciclos con "Nuevo ciclo"

**Files:**
- Create: `frontend/src/modules/ucca/types.ts`
- Create: `frontend/src/modules/ucca/scoring.ts`
- Create: `frontend/src/hooks/useApiGet.ts`
- Create: `frontend/src/modules/ucca/components/OutcomeBadge.tsx`
- Create: `frontend/src/modules/ucca/UccaCyclesPage.tsx` (reemplaza `UccaDashboard.tsx`)
- Delete: `frontend/src/modules/ucca/UccaDashboard.tsx`, `frontend/src/modules/ucca/UccaEvaluatePage.tsx`
- Modify: `frontend/src/App.tsx`, `frontend/src/layout/nav-config.ts`, `frontend/src/i18n/es.json`, `frontend/src/i18n/en.json`, `frontend/src/components/StatusBadge.tsx` (ampliar `ns`)

**Interfaces:**
- Produces: tipos `Cycle`, `Criterion`, `AnswerValue`, `Outcome`, `ChartAuditRow`, `ChartAudit`, `Summary`; `computeScore(outcomes: AnswerValue[]): ScoreResult`; `useApiGet<T>(path): {data: T | null, loading, error, reload}`; `<OutcomeBadge outcome={...} />`; rutas `/ucca`, `/ucca/cycles/:cycleId`, `/ucca/cycles/:cycleId/audits/new`, `/ucca/audits/:auditId`, `/ucca/dashboard` (las páginas de Tasks 7–9 se registran aquí con placeholders mínimos que luego se reemplazan).

- [ ] **Step 1: Tipos**

```ts
// frontend/src/modules/ucca/types.ts
export type AnswerValue = "compliant" | "non_compliant" | "not_applicable";
export type Outcome = "compliant" | "minor_improvement" | "improvement_required" | "priority_corrective_action";
export type AuditStatus = "draft" | "submitted" | "approved";
export type ActionStatus = "assigned" | "in_progress" | "closed";

export type Cycle = {
  id: string; facility_id: string; facility_name: string | null; template_version_id: string;
  period_label: string; year: number; quarter: string; status: string;
  audits_count: number; average_score: number | null;
};

export type Criterion = {
  id: string; code: string; domain: string; universal_question: string;
  profession_interpretation: string; examples_evidence: string; is_active: boolean;
};

export type Professional = {
  id: string; full_name: string; employee_number: string; profession_name: string;
  primary_facility_id: string; is_active?: boolean;
};

export type AnswerIn = { criterion_id: string; outcome: AnswerValue; not_applicable_reason: string | null; comment: string | null };
export type CorrectiveActionIn = {
  description: string; responsible_user_id: string; due_date: string; status: ActionStatus; closure_evidence: string | null;
};
export type FindingIn = { description: string; corrective_action: CorrectiveActionIn | null };
export type ChartAuditWrite = {
  professional_id: string; case_reference: string; audit_date: string; notes: string;
  answers: AnswerIn[]; finding: FindingIn | null;
};

export type AnswerOut = AnswerIn & { criterion_code: string };
export type CorrectiveActionOut = CorrectiveActionIn & { id: string; responsible_name: string | null };
export type FindingOut = { id: string; description: string; status: string; corrective_action: CorrectiveActionOut | null };

export type ChartAudit = {
  id: string; cycle_id: string; facility_id: string; professional_id: string; professional_name: string;
  employee_number: string; profession_name: string | null; auditor_user_id: string; auditor_name: string | null;
  case_reference: string; audit_date: string; status: AuditStatus; applicable_count: number; yes_count: number;
  score: number | null; outcome: Outcome | null; notes: string; answers: AnswerOut[]; finding: FindingOut | null;
};

export type ChartAuditRow = {
  id: string; professional_id: string; professional_name: string; employee_number: string;
  profession_name: string | null; auditor_name: string | null; case_reference: string; audit_date: string;
  status: AuditStatus; applicable_count: number; yes_count: number; score: number | null; outcome: Outcome | null;
  answers: Record<string, AnswerValue>; has_finding: boolean;
};

export type Summary = {
  audits_count: number; draft_count: number; average_score: number | null;
  outcome_distribution: Record<Outcome, number>;
  criteria: { code: string; applicable: number; yes: number; yes_rate: number | null }[];
  professionals: {
    professional_id: string; employee_number: string; professional_name: string; profession_name: string | null;
    audits_count: number; average_score: number | null; outcome: Outcome | null; criteria: Record<string, number | null>;
  }[];
  trend: { year: number; quarter: string; audits_count: number; average_score: number | null }[];
  open_corrective_actions: {
    id: string; audit_id: string; case_reference: string; professional_name: string; finding: string;
    responsible_name: string | null; due_date: string; status: ActionStatus;
  }[];
};
```

- [ ] **Step 2: Scoring en cliente (espejo de `scoring.py`)**

```ts
// frontend/src/modules/ucca/scoring.ts
import type { AnswerValue, Outcome } from "./types";

/** Réplica exacta de backend/app/domains/governance/ucca/scoring.py para feedback en vivo. */
export type ScoreResult = { applicable: number; yes: number; score: number | null; outcome: Outcome | null };

export const OUTCOME_BANDS: [Outcome, number][] = [
  ["compliant", 90],
  ["minor_improvement", 80],
  ["improvement_required", 70],
];
export const PRIORITY_OUTCOME: Outcome = "priority_corrective_action";

export function outcomeFor(score: number | null): Outcome | null {
  if (score === null) return null;
  for (const [outcome, threshold] of OUTCOME_BANDS) if (score >= threshold) return outcome;
  return PRIORITY_OUTCOME;
}

export function computeScore(outcomes: AnswerValue[]): ScoreResult {
  const applicable = outcomes.filter((o) => o !== "not_applicable").length;
  const yes = outcomes.filter((o) => o === "compliant").length;
  const score = applicable === 0 ? null : Math.round((yes / applicable) * 10000) / 100;
  return { applicable, yes, score, outcome: outcomeFor(score) };
}

export function formatScore(score: number | null): string {
  return score === null ? "—" : `${score.toFixed(score % 1 === 0 ? 0 : 2)} %`;
}
```

- [ ] **Step 3: Hook `useApiGet`**

```ts
// frontend/src/hooks/useApiGet.ts
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { ApiError, apiFetchJson } from "../api/client";
import { useAuth } from "../auth/AuthContext";

/** GET de un único objeto (detalle, resumen). `path` vacío → no consulta. */
export function useApiGet<T>(path: string) {
  const { t } = useTranslation();
  const { session } = useAuth();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(Boolean(path));
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    apiFetchJson<T>(path, { signal: controller.signal }, session?.token)
      .then((row) => { if (!controller.signal.aborted) setData(row); })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        setError(err instanceof ApiError ? t("app.errorLoadStatus", { status: err.status }) : t("app.errorLoad"));
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, session?.token, reloadKey]);

  return { data, loading, error, reload: () => setReloadKey((k) => k + 1) };
}
```

- [ ] **Step 4: `OutcomeBadge` y ampliar `StatusBadge`**

```tsx
// frontend/src/modules/ucca/components/OutcomeBadge.tsx
import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import type { Outcome } from "../types";

const STYLES: Record<Outcome, { bg: string; fg: string }> = {
  compliant: { bg: alkalma.turquoiseTint, fg: alkalma.indigo },
  minor_improvement: { bg: "#FBEFD9", fg: alkalma.indigo },
  improvement_required: { bg: "#F6DFB8", fg: alkalma.indigoDark },
  priority_corrective_action: { bg: "#F8E3E1", fg: brandTokens.colors.danger },
};

/** Badge de outcome (bandas del Excel). `null` → guion gris (sin aplicables). */
export function OutcomeBadge({ outcome, size = "sm" }: { outcome: Outcome | null; size?: "sm" | "lg" }) {
  const { t } = useTranslation();
  if (!outcome) return <span style={{ color: brandTokens.colors.textSecondary }}>—</span>;
  const s = STYLES[outcome];
  return (
    <span style={{ display: "inline-block", padding: size === "lg" ? "6px 14px" : "3px 10px", borderRadius: 999,
                   fontSize: size === "lg" ? 14 : 12, fontWeight: 600, background: s.bg, color: s.fg, whiteSpace: "nowrap" }}>
      {t(`ucca.outcomes.${outcome}`)}
    </span>
  );
}
```

En `StatusBadge.tsx` cambiar el tipo de `ns` a `"ucca.statuses" | "ucca.outcomes" | "ucca.answers" | "ucca.actionStatuses" | "indicators.severities"` y en `toneFor` añadir: `if (code === "in_progress") return "warning"; if (code === "assigned") return "neutral";`.

- [ ] **Step 5: i18n — reemplazar la rama `ucca` completa y añadir `nav.uccaDashboard`**

ES (`frontend/src/i18n/es.json`), `"nav"`: añadir `"uccaDashboard": "UCCA — Dashboard"` tras `uccaCycles`. Rama `"ucca"`:

```json
"ucca": {
  "title": "UCCA — Ciclos de auditoría",
  "subtitle": "M04 — Universal Clinical Competency Audit: un ciclo por centro y trimestre; cada ciclo audita expedientes por profesional",
  "newCycle": "Nuevo ciclo",
  "cycleFacility": "Centro",
  "cycleYear": "Año",
  "cycleQuarter": "Trimestre",
  "period": "Periodo",
  "facility": "Centro",
  "status": "Estado",
  "auditsCount": "Expedientes",
  "averageScore": "Score medio",
  "open": "Abrir",
  "empty": "No hay ciclos de auditoría. Cree el primero con «Nuevo ciclo».",
  "loadingCycles": "Cargando ciclos…",
  "cycleMissing": "Ciclo no especificado.",
  "cycleNotFound": "Ciclo no encontrado.",
  "cycleTitle": "Ciclo {{period}}",
  "cycleSubtitle": "Centro: {{facility}} · Un expediente por fila; score = Yes / aplicables (N/A excluidos)",
  "back": "Volver a ciclos",
  "backToCycle": "Volver al ciclo",
  "newAudit": "Nueva auditoría",
  "kpi": {
    "audits": "Expedientes auditados",
    "averageScore": "Score medio",
    "compliantRate": "% Compliant",
    "openActions": "Acciones correctivas abiertas",
    "drafts": "{{count}} en borrador (no cuentan)"
  },
  "table": {
    "num": "#",
    "cgId": "CG_ID",
    "professional": "Profesional",
    "profession": "Profesión",
    "mrn": "MRN / Caso",
    "date": "Fecha",
    "auditor": "Auditor",
    "applicable": "Aplic.",
    "yes": "Yes",
    "score": "Score",
    "outcome": "Outcome",
    "status": "Estado",
    "finding": "Hallazgo",
    "open": "Abrir",
    "empty": "Aún no hay expedientes auditados en este ciclo."
  },
  "answers": { "compliant": "Yes", "non_compliant": "No", "not_applicable": "N/A" },
  "outcomes": {
    "compliant": "Compliant",
    "minor_improvement": "Minor Improvement",
    "improvement_required": "Improvement Required",
    "priority_corrective_action": "Priority Corrective Action"
  },
  "statuses": { "draft": "Borrador", "submitted": "Enviado", "approved": "Aprobado", "open": "Abierto", "closed": "Cerrado", "withdrawn": "Retirado" },
  "actionStatuses": { "assigned": "Asignada", "in_progress": "En curso", "closed": "Cerrada" },
  "form": {
    "newTitle": "Auditar expediente",
    "editTitle": "Expediente {{mrn}}",
    "subtitle": "Responda Yes / No / N/A a cada criterio. El score y el outcome se calculan al instante.",
    "dataSection": "Datos del expediente",
    "professional": "Profesional auditado",
    "professionalPlaceholder": "Seleccione un profesional del centro…",
    "cgId": "CG_ID",
    "profession": "Profesión",
    "mrn": "MRN / Case Ref",
    "mrnPlaceholder": "Ej. 102453 o AKAD00132",
    "date": "Fecha de auditoría",
    "auditor": "Auditor",
    "criteriaSection": "Criterios de evaluación",
    "showDetails": "Ver interpretación y evidencia",
    "hideDetails": "Ocultar detalle",
    "interpretation": "Interpretación por profesión",
    "evidence": "Ejemplos / evidencia",
    "naReason": "Razón de N/A (obligatoria)",
    "naReasonPlaceholder": "Ej. fuera del alcance de práctica del profesional",
    "comment": "Comentario (opcional)",
    "notes": "Notas generales (opcional)",
    "findingSection": "Hallazgo y acción correctiva",
    "findingHint": "El outcome no es Compliant: registre el hallazgo principal y, si procede, la acción correctiva.",
    "findingOptional": "Outcome Compliant: puede registrar un hallazgo opcional.",
    "keyFinding": "Hallazgo principal (Key Finding)",
    "correctiveAction": "Acción correctiva",
    "owner": "Responsable",
    "ownerPlaceholder": "Seleccione responsable…",
    "dueDate": "Fecha límite",
    "actionStatus": "Estado de la acción",
    "closureEvidence": "Evidencia de cierre",
    "applicable": "Aplicables",
    "yesCount": "Yes",
    "score": "Score",
    "outcome": "Outcome",
    "answered": "{{done}} de {{total}} respondidos",
    "saveDraft": "Guardar borrador",
    "submit": "Enviar",
    "approve": "Aprobar",
    "saving": "Guardando…",
    "saved": "Auditoría guardada como borrador.",
    "submitted": "Auditoría enviada.",
    "approved": "Auditoría aprobada.",
    "readOnly": "Auditoría {{status}}: solo lectura.",
    "approvedNotice": "Auditoría aprobada: inmutable (regla de inmutabilidad del funcional).",
    "saveError": "No fue posible guardar la auditoría.",
    "missingAnswers": "Falta responder {{count}} criterio(s).",
    "missingNaReason": "Indique la razón de cada N/A.",
    "missingFinding": "Registre el hallazgo principal (el outcome no es Compliant).",
    "loading": "Cargando auditoría…",
    "notFound": "Auditoría no encontrada."
  },
  "dashboard": {
    "title": "UCCA — Dashboard",
    "subtitle": "Resultados consolidados por centro, profesional, criterio y trimestre (solo auditorías enviadas o aprobadas)",
    "filters": { "facility": "Centro", "year": "Año", "quarter": "Trimestre", "all": "Todos" },
    "byCriterion": "% Yes por criterio",
    "byProfessional": "Resultados por profesional",
    "trend": "Tendencia del score por trimestre",
    "openActions": "Acciones correctivas abiertas",
    "empty": "Sin auditorías enviadas o aprobadas para los filtros seleccionados.",
    "finding": "Hallazgo",
    "owner": "Responsable",
    "due": "Vence",
    "period": "Periodo",
    "noActions": "No hay acciones correctivas abiertas."
  }
}
```

EN (`frontend/src/i18n/en.json`), `"nav"`: `"uccaDashboard": "UCCA — Dashboard"`. Rama `"ucca"` con las mismas claves en inglés:

```json
"ucca": {
  "title": "UCCA — Audit cycles",
  "subtitle": "M04 — Universal Clinical Competency Audit: one cycle per facility and quarter; each cycle audits charts per professional",
  "newCycle": "New cycle",
  "cycleFacility": "Facility",
  "cycleYear": "Year",
  "cycleQuarter": "Quarter",
  "period": "Period",
  "facility": "Facility",
  "status": "Status",
  "auditsCount": "Charts",
  "averageScore": "Average score",
  "open": "Open",
  "empty": "No audit cycles yet. Create the first one with “New cycle”.",
  "loadingCycles": "Loading cycles…",
  "cycleMissing": "Cycle not specified.",
  "cycleNotFound": "Cycle not found.",
  "cycleTitle": "Cycle {{period}}",
  "cycleSubtitle": "Facility: {{facility}} · One chart per row; score = Yes / applicable (N/A excluded)",
  "back": "Back to cycles",
  "backToCycle": "Back to cycle",
  "newAudit": "New audit",
  "kpi": {
    "audits": "Charts audited",
    "averageScore": "Average score",
    "compliantRate": "% Compliant",
    "openActions": "Open corrective actions",
    "drafts": "{{count}} in draft (not counted)"
  },
  "table": {
    "num": "#", "cgId": "CG_ID", "professional": "Practitioner", "profession": "Profession", "mrn": "MRN / Case Ref",
    "date": "Audit date", "auditor": "Auditor", "applicable": "Applicable", "yes": "Yes count", "score": "Score",
    "outcome": "Outcome", "status": "Status", "finding": "Finding", "open": "Open",
    "empty": "No charts audited in this cycle yet."
  },
  "answers": { "compliant": "Yes", "non_compliant": "No", "not_applicable": "N/A" },
  "outcomes": {
    "compliant": "Compliant", "minor_improvement": "Minor Improvement",
    "improvement_required": "Improvement Required", "priority_corrective_action": "Priority Corrective Action"
  },
  "statuses": { "draft": "Draft", "submitted": "Submitted", "approved": "Approved", "open": "Open", "closed": "Closed", "withdrawn": "Withdrawn" },
  "actionStatuses": { "assigned": "Assigned", "in_progress": "In progress", "closed": "Closed" },
  "form": {
    "newTitle": "Audit chart", "editTitle": "Chart {{mrn}}",
    "subtitle": "Answer Yes / No / N/A for each criterion. Score and outcome update instantly.",
    "dataSection": "Chart details", "professional": "Audited practitioner",
    "professionalPlaceholder": "Select a practitioner from this facility…", "cgId": "CG_ID", "profession": "Profession",
    "mrn": "MRN / Case Ref", "mrnPlaceholder": "e.g. 102453 or AKAD00132", "date": "Audit date", "auditor": "Auditor",
    "criteriaSection": "Evaluation criteria", "showDetails": "Show interpretation and evidence", "hideDetails": "Hide details",
    "interpretation": "Profession-specific interpretation", "evidence": "Examples / evidence",
    "naReason": "N/A reason (required)", "naReasonPlaceholder": "e.g. outside the practitioner's scope of practice",
    "comment": "Comment (optional)", "notes": "General notes (optional)",
    "findingSection": "Finding & corrective action",
    "findingHint": "Outcome is not Compliant: record the key finding and, if needed, the corrective action.",
    "findingOptional": "Outcome Compliant: you may record an optional finding.",
    "keyFinding": "Key finding", "correctiveAction": "Corrective action", "owner": "Action owner",
    "ownerPlaceholder": "Select owner…", "dueDate": "Due date", "actionStatus": "Action status",
    "closureEvidence": "Closure evidence", "applicable": "Applicable", "yesCount": "Yes", "score": "Score",
    "outcome": "Outcome", "answered": "{{done}} of {{total}} answered", "saveDraft": "Save draft", "submit": "Submit",
    "approve": "Approve", "saving": "Saving…", "saved": "Audit saved as draft.", "submitted": "Audit submitted.",
    "approved": "Audit approved.", "readOnly": "Audit {{status}}: read only.",
    "approvedNotice": "Approved audit: immutable (immutability rule).", "saveError": "Could not save the audit.",
    "missingAnswers": "{{count}} criterion(s) still unanswered.", "missingNaReason": "Provide a reason for each N/A.",
    "missingFinding": "Record the key finding (outcome is not Compliant).", "loading": "Loading audit…",
    "notFound": "Audit not found."
  },
  "dashboard": {
    "title": "UCCA — Dashboard",
    "subtitle": "Consolidated results by facility, practitioner, criterion and quarter (submitted or approved audits only)",
    "filters": { "facility": "Facility", "year": "Year", "quarter": "Quarter", "all": "All" },
    "byCriterion": "% Yes by criterion", "byProfessional": "Results by practitioner",
    "trend": "Score trend by quarter", "openActions": "Open corrective actions",
    "empty": "No submitted or approved audits for the selected filters.",
    "finding": "Finding", "owner": "Owner", "due": "Due", "period": "Period", "noActions": "No open corrective actions."
  }
}
```

- [ ] **Step 6: Página de ciclos con drawer "Nuevo ciclo"**

```tsx
// frontend/src/modules/ucca/UccaCyclesPage.tsx
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ApiError, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { DataTable } from "../../components/DataTable";
import { Drawer } from "../../components/Drawer";
import { FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { Toolbar } from "../../components/Toolbar";
import { useApiList } from "../../hooks/useApiList";
import { useCanManage } from "../../hooks/useCanManage";
import { brandTokens } from "../../theme/brand-tokens";
import { formatScore } from "./scoring";
import type { Cycle } from "./types";

type Facility = { id: string; name: string; is_active: boolean };
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

export function UccaCyclesPage() {
  const { t } = useTranslation();
  const { session } = useAuth();
  const canCreate = useCanManage("ucca.create");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const facilities = useApiList<Facility>("/identity/facilities");

  const [open, setOpen] = useState(false);
  const [facilityId, setFacilityId] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [quarter, setQuarter] = useState("Q1");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await apiPostJson("/ucca/cycles", { facility_id: facilityId, year: Number(year), quarter }, session?.token);
      setOpen(false);
      cycles.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("app.saveError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section>
      <PageHeader title={t("ucca.title")} subtitle={t("ucca.subtitle")} />
      <Toolbar right={canCreate && <button type="button" className="btn-primary" onClick={() => setOpen(true)}>+ {t("ucca.newCycle")}</button>} />
      {cycles.loading && <p>{t("ucca.loadingCycles")}</p>}
      {cycles.error && <p>{cycles.error}</p>}
      {!cycles.loading && !cycles.error && (
        <DataTable
          rows={cycles.data}
          emptyMessage={t("ucca.empty")}
          columns={[
            { key: "period", header: t("ucca.period"), render: (r) => (
              <Link to={`/ucca/cycles/${r.id}`} style={{ color: brandTokens.colors.link, fontWeight: 600, textDecoration: "none" }}>{r.period_label}</Link>
            ) },
            { key: "facility", header: t("ucca.facility"), render: (r) => r.facility_name ?? "—" },
            { key: "audits", header: t("ucca.auditsCount"), render: (r) => r.audits_count },
            { key: "score", header: t("ucca.averageScore"), render: (r) => formatScore(r.average_score) },
            { key: "status", header: t("ucca.status"), render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            { key: "open", header: "", render: (r) => (
              <Link to={`/ucca/cycles/${r.id}`} className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12, textDecoration: "none" }}>{t("ucca.open")} →</Link>
            ) },
          ]}
        />
      )}

      <Drawer open={open} title={t("ucca.newCycle")} onClose={() => !saving && setOpen(false)}
        footer={<>
          <button type="button" className="btn-ghost" onClick={() => setOpen(false)} disabled={saving}>{t("app.cancel")}</button>
          <button type="submit" form="cycle-form" className="btn-primary" disabled={saving || !facilityId}>{saving ? t("app.saving") : t("app.save")}</button>
        </>}>
        <form id="cycle-form" onSubmit={submit}>
          <FormField label={t("ucca.cycleFacility")} required>
            <select value={facilityId} onChange={(e) => setFacilityId(e.target.value)} required>
              <option value="">{t("admin.users.selectPlaceholder")}</option>
              {facilities.data.filter((f) => f.is_active !== false).map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </FormField>
          <FormField label={t("ucca.cycleYear")} required>
            <input type="number" min={2020} max={2100} value={year} onChange={(e) => setYear(e.target.value)} required />
          </FormField>
          <FormField label={t("ucca.cycleQuarter")} required>
            <select value={quarter} onChange={(e) => setQuarter(e.target.value)}>
              {QUARTERS.map((q) => <option key={q} value={q}>{q}</option>)}
            </select>
          </FormField>
          {error && <p role="alert" style={{ color: brandTokens.colors.danger, fontSize: 13 }}>{error}</p>}
        </form>
      </Drawer>
    </section>
  );
}
```

- [ ] **Step 7: Rutas y navegación**

`App.tsx`: eliminar imports de `UccaDashboard` y `UccaEvaluatePage`; importar `UccaCyclesPage`, `UccaCyclePage` (Task 7), `ChartAuditPage` (Task 8), `UccaAnalyticsPage` (Task 9). Hasta que existan, crear cada archivo con un placeholder mínimo que se sustituye en su Task:

```tsx
// placeholder temporal, p.ej. frontend/src/modules/ucca/UccaCyclePage.tsx
export function UccaCyclePage() { return <p>UCCA cycle</p>; }
```

Rutas:

```tsx
<Route path="/ucca" element={<UccaCyclesPage />} />
<Route path="/ucca/dashboard" element={<UccaAnalyticsPage />} />
<Route path="/ucca/cycles/:cycleId" element={<UccaCyclePage />} />
<Route path="/ucca/cycles/:cycleId/audits/new" element={<ChartAuditPage />} />
<Route path="/ucca/audits/:auditId" element={<ChartAuditPage />} />
```

`nav-config.ts`, grupo `nav.governance`:

```ts
{ labelKey: "nav.uccaCycles", path: "/ucca" },
{ labelKey: "nav.uccaDashboard", path: "/ucca/dashboard" },
{ labelKey: "nav.indicators", path: "/indicators" },
```

Borrar `UccaDashboard.tsx` y `UccaEvaluatePage.tsx` (`git rm`).

- [ ] **Step 8: Build y verificación rápida**

Run: `npm --prefix /Users/danielsandoval/Documents/Proyectos/clinical-governance/frontend run build` → `✓ built`.
Con los servicios arriba, abrir `http://localhost:5173/ucca` con Playwright: crear ciclo "Al Falah · 2026 · Q2" → fila nueva; repetir → mensaje 409 en el drawer.

- [ ] **Step 9: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add -A frontend/src
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca-ui): cycles page with new-cycle drawer, shared types, client scoring, routes and i18n

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Página del ciclo — KPIs + tabla tipo Excel

**Files:**
- Create: `frontend/src/modules/ucca/components/KpiCard.tsx`
- Create: `frontend/src/modules/ucca/components/AnswerChip.tsx`
- Replace: `frontend/src/modules/ucca/UccaCyclePage.tsx`

**Interfaces:**
- Consumes: `GET /ucca/cycles` (para cabecera), `GET /ucca/cycles/{id}/audits` → `ChartAuditRow[]`, `GET /ucca/cycles/{id}/summary` → `Summary`, `GET /ucca/criteria?only_active=true` → `Criterion[]`.
- Produces: `<KpiCard label value hint? tone? />`, `<AnswerChip value={AnswerValue | undefined} />`.

- [ ] **Step 1: Componentes**

```tsx
// frontend/src/modules/ucca/components/KpiCard.tsx
import type { ReactNode } from "react";

import { brandTokens } from "../../../theme/brand-tokens";

export function KpiCard({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`,
                  borderRadius: brandTokens.radius.lg, boxShadow: brandTokens.shadow.card, padding: "16px 20px", minWidth: 0 }}>
      <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", color: brandTokens.colors.textSecondary }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 600, color: brandTokens.colors.textPrimary, marginTop: 6, lineHeight: 1.1 }}>{value}</div>
      {hint && <div style={{ fontSize: 12, color: brandTokens.colors.textSecondary, marginTop: 6 }}>{hint}</div>}
    </div>
  );
}
```

```tsx
// frontend/src/modules/ucca/components/AnswerChip.tsx
import { useTranslation } from "react-i18next";

import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import type { AnswerValue } from "../types";

const STYLE: Record<AnswerValue, { bg: string; fg: string; glyph: string }> = {
  compliant: { bg: alkalma.turquoiseTint, fg: alkalma.turquoiseDark, glyph: "✓" },
  non_compliant: { bg: "#F8E3E1", fg: brandTokens.colors.danger, glyph: "✗" },
  not_applicable: { bg: alkalma.bgSoft, fg: brandTokens.colors.textSecondary, glyph: "N/A" },
};

/** Celda compacta Yes/No/N/A de la tabla tipo Excel. `undefined` → guion (sin respuesta). */
export function AnswerChip({ value }: { value: AnswerValue | undefined }) {
  const { t } = useTranslation();
  if (!value) return <span style={{ color: brandTokens.colors.textSecondary }}>—</span>;
  const s = STYLE[value];
  return (
    <span title={t(`ucca.answers.${value}`)} aria-label={t(`ucca.answers.${value}`)}
          style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", minWidth: 28, height: 22, padding: "0 6px",
                   borderRadius: 999, fontSize: 12, fontWeight: 700, background: s.bg, color: s.fg }}>
      {s.glyph}
    </span>
  );
}
```

- [ ] **Step 2: Página del ciclo**

```tsx
// frontend/src/modules/ucca/UccaCyclePage.tsx
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { Toolbar } from "../../components/Toolbar";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { useCanManage } from "../../hooks/useCanManage";
import { brandTokens } from "../../theme/brand-tokens";
import { AnswerChip } from "./components/AnswerChip";
import { KpiCard } from "./components/KpiCard";
import { OutcomeBadge } from "./components/OutcomeBadge";
import { formatScore } from "./scoring";
import type { ChartAuditRow, Criterion, Cycle, Summary } from "./types";

const small: React.CSSProperties = { fontSize: 13 };
const muted: React.CSSProperties = { fontSize: 12, color: brandTokens.colors.textSecondary };

export function UccaCyclePage() {
  const { t } = useTranslation();
  const { cycleId = "" } = useParams<{ cycleId: string }>();
  const canCreate = useCanManage("ucca.create");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const audits = useApiList<ChartAuditRow>(cycleId ? `/ucca/cycles/${cycleId}/audits` : "");
  const summary = useApiGet<Summary>(cycleId ? `/ucca/cycles/${cycleId}/summary` : "");
  const criteria = useApiList<Criterion>("/ucca/criteria?only_active=true");

  const cycle = cycles.data.find((c) => c.id === cycleId);
  if (!cycleId) return <p>{t("ucca.cycleMissing")}</p>;
  if (cycles.loading) return <p>{t("ucca.loadingCycles")}</p>;
  if (!cycle) return <p>{t("ucca.cycleNotFound")}</p>;

  const s = summary.data;
  const compliantRate = s && s.audits_count > 0 ? Math.round((s.outcome_distribution.compliant / s.audits_count) * 100) : null;
  const codes = criteria.data.map((c) => c.code);

  return (
    <section>
      <p style={{ margin: "0 0 18px" }}>
        <Link to="/ucca" style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 500 }}>← {t("ucca.back")}</Link>
      </p>
      <PageHeader title={t("ucca.cycleTitle", { period: cycle.period_label })}
                  subtitle={t("ucca.cycleSubtitle", { facility: cycle.facility_name ?? "—" })} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 20 }}>
        <KpiCard label={t("ucca.kpi.audits")} value={s?.audits_count ?? "—"}
                 hint={s && s.draft_count > 0 ? t("ucca.kpi.drafts", { count: s.draft_count }) : undefined} />
        <KpiCard label={t("ucca.kpi.averageScore")} value={formatScore(s?.average_score ?? null)} />
        <KpiCard label={t("ucca.kpi.compliantRate")} value={compliantRate === null ? "—" : `${compliantRate} %`} />
        <KpiCard label={t("ucca.kpi.openActions")} value={s?.open_corrective_actions.length ?? "—"} />
      </div>

      <Toolbar right={canCreate && (
        <Link to={`/ucca/cycles/${cycleId}/audits/new`} className="btn-primary" style={{ textDecoration: "none" }}>+ {t("ucca.newAudit")}</Link>
      )} />

      {audits.loading && <p>{t("app.loading")}</p>}
      {audits.error && <p>{audits.error}</p>}
      {!audits.loading && !audits.error && (
        <DataTable
          rows={audits.data.map((r, i) => ({ ...r, num: i + 1 }))}
          emptyMessage={t("ucca.table.empty")}
          columns={[
            { key: "num", header: t("ucca.table.num"), width: 36, render: (r) => <span style={muted}>{r.num}</span> },
            { key: "cg", header: t("ucca.table.cgId"), width: 80, render: (r) => <code style={{ fontSize: 12 }}>{r.employee_number}</code> },
            { key: "pro", header: t("ucca.table.professional"), render: (r) => (
              <span style={{ display: "block", ...small }}>
                <strong style={{ fontWeight: 500 }}>{r.professional_name}</strong>
                <span style={{ display: "block", ...muted }}>{r.profession_name ?? "—"}</span>
              </span>
            ) },
            { key: "mrn", header: t("ucca.table.mrn"), width: 110, render: (r) => <code style={{ fontSize: 12 }}>{r.case_reference}</code> },
            { key: "date", header: t("ucca.table.date"), width: 96, render: (r) => <span style={small}>{r.audit_date}</span> },
            ...codes.map((code) => ({
              key: code, header: code, width: 44,
              render: (r: ChartAuditRow) => <AnswerChip value={r.answers[code]} />,
            })),
            { key: "app", header: t("ucca.table.applicable"), width: 52, render: (r) => <span style={small}>{r.applicable_count}</span> },
            { key: "yes", header: t("ucca.table.yes"), width: 44, render: (r) => <span style={small}>{r.yes_count}</span> },
            { key: "score", header: t("ucca.table.score"), width: 70, render: (r) => <strong style={{ ...small, fontWeight: 600 }}>{formatScore(r.score)}</strong> },
            { key: "outcome", header: t("ucca.table.outcome"), width: 140, render: (r) => <OutcomeBadge outcome={r.outcome} /> },
            { key: "status", header: t("ucca.table.status"), width: 90, render: (r) => <StatusBadge code={r.status} ns="ucca.statuses" /> },
            { key: "open", header: "", width: 64, render: (r) => (
              <Link to={`/ucca/audits/${r.id}`} className="btn-ghost" style={{ padding: "4px 10px", fontSize: 12, textDecoration: "none" }}>{t("ucca.table.open")}</Link>
            ) },
          ]}
        />
      )}
    </section>
  );
}
```

`DataTable` ya soporta `width` (añadido en el commit `84feabe`). La columna "Auditor" del Excel se omite en la tabla (visible en el detalle) para mantener el ancho; `has_finding` se señala con un punto ámbar junto al MRN: en la columna `mrn`, si `r.has_finding`, renderizar además `<span aria-label={t("ucca.table.finding")} style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: brandTokens.colors.warning, marginLeft: 6 }} />`.

- [ ] **Step 3: Build + verificación visual**

Run: `npm --prefix /Users/danielsandoval/Documents/Proyectos/clinical-governance/frontend run build` → `✓ built`.
Playwright a 1280px en `/ucca/cycles/<id>`: `document.documentElement.scrollWidth === window.innerWidth`; KPIs con "—" si no hay auditorías; tabla vacía con mensaje.

- [ ] **Step 4: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add frontend/src/modules/ucca
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca-ui): cycle page with KPIs and Excel-style chart audit table

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: Formulario "Auditar expediente" — tarjetas por criterio, barra en vivo, hallazgo y acción correctiva

**Files:**
- Create: `frontend/src/modules/ucca/components/AnswerSelector.tsx`
- Create: `frontend/src/modules/ucca/components/CriterionCard.tsx`
- Create: `frontend/src/modules/ucca/components/ScoreBar.tsx`
- Create: `frontend/src/modules/ucca/components/FindingSection.tsx`
- Replace: `frontend/src/modules/ucca/ChartAuditPage.tsx`
- Modify: `frontend/src/styles.css` (clase `.segmented`)

**Interfaces:**
- Consumes: `GET /ucca/criteria?only_active=true`, `GET /identity/professionals`, `GET /identity/users` (responsables activos), `GET /identity/me`, `GET /ucca/audits/{id}`, `POST /ucca/cycles/{id}/audits`, `PATCH /ucca/audits/{id}`, `POST /ucca/audits/{id}/submit|approve`; `computeScore`.
- Estado del formulario: `answers: Record<criterionId, {outcome: AnswerValue | null, reason: string, comment: string}>`.

- [ ] **Step 1: Estilos del selector segmentado** (añadir a `styles.css`)

```css
.segmented { display: inline-flex; border: 1px solid var(--border, #DCE5EA); border-radius: 999px; overflow: hidden; }
.segmented button { border: 0; background: #fff; padding: 6px 14px; font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; color: #16455C; }
.segmented button + button { border-left: 1px solid #DCE5EA; }
.segmented button[aria-pressed="true"][data-value="compliant"] { background: #70C8C3; color: #16455C; }
.segmented button[aria-pressed="true"][data-value="non_compliant"] { background: #B3261E; color: #fff; }
.segmented button[aria-pressed="true"][data-value="not_applicable"] { background: #8B9EA5; color: #fff; }
.segmented button:disabled { cursor: default; opacity: .7; }
```

- [ ] **Step 2: `AnswerSelector`**

```tsx
// frontend/src/modules/ucca/components/AnswerSelector.tsx
import { useTranslation } from "react-i18next";

import type { AnswerValue } from "../types";

const VALUES: AnswerValue[] = ["compliant", "non_compliant", "not_applicable"];

export function AnswerSelector({ value, onChange, disabled, name }: {
  value: AnswerValue | null; onChange: (v: AnswerValue) => void; disabled?: boolean; name: string;
}) {
  const { t } = useTranslation();
  return (
    <div className="segmented" role="group" aria-label={name}>
      {VALUES.map((v) => (
        <button key={v} type="button" data-value={v} aria-pressed={value === v} disabled={disabled} onClick={() => onChange(v)}>
          {t(`ucca.answers.${v}`)}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: `CriterionCard`**

```tsx
// frontend/src/modules/ucca/components/CriterionCard.tsx
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../../../theme/brand-tokens";
import type { AnswerValue, Criterion } from "../types";
import { AnswerSelector } from "./AnswerSelector";

export type AnswerState = { outcome: AnswerValue | null; reason: string; comment: string };

export function CriterionCard({ criterion, state, onChange, readOnly, invalid }: {
  criterion: Criterion; state: AnswerState; onChange: (next: AnswerState) => void; readOnly: boolean; invalid: boolean;
}) {
  const { t } = useTranslation();
  const [details, setDetails] = useState(false);
  const border = invalid ? brandTokens.colors.danger : state.outcome ? brandTokens.colors.accent : brandTokens.colors.border;
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${border}`, borderLeft: `4px solid ${border}`,
                  borderRadius: brandTokens.radius.md, padding: "16px 18px", display: "grid", gap: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.04em", color: brandTokens.colors.textSecondary }}>
            <code>{criterion.code}</code> · {criterion.domain}
          </div>
          <div style={{ fontSize: 15, fontWeight: 500, marginTop: 4 }}>{criterion.universal_question}</div>
        </div>
        <AnswerSelector name={criterion.code} value={state.outcome} disabled={readOnly} onChange={(outcome) => onChange({ ...state, outcome })} />
      </div>
      <button type="button" className="btn-ghost" style={{ justifySelf: "start", padding: "2px 8px", fontSize: 12 }} onClick={() => setDetails((d) => !d)}>
        {details ? t("ucca.form.hideDetails") : t("ucca.form.showDetails")}
      </button>
      {details && (
        <div style={{ fontSize: 13, color: brandTokens.colors.textSecondary, display: "grid", gap: 6 }}>
          <div><strong style={{ color: brandTokens.colors.textPrimary }}>{t("ucca.form.interpretation")}:</strong> {criterion.profession_interpretation || "—"}</div>
          <div><strong style={{ color: brandTokens.colors.textPrimary }}>{t("ucca.form.evidence")}:</strong> {criterion.examples_evidence || "—"}</div>
        </div>
      )}
      {state.outcome === "not_applicable" && (
        <label style={{ display: "grid", gap: 4, fontSize: 13, fontWeight: 500 }}>
          {t("ucca.form.naReason")}
          <input value={state.reason} disabled={readOnly} required placeholder={t("ucca.form.naReasonPlaceholder")}
                 onChange={(e) => onChange({ ...state, reason: e.target.value })} />
        </label>
      )}
      <label style={{ display: "grid", gap: 4, fontSize: 13, fontWeight: 500 }}>
        {t("ucca.form.comment")}
        <input value={state.comment} disabled={readOnly} onChange={(e) => onChange({ ...state, comment: e.target.value })} />
      </label>
    </div>
  );
}
```

- [ ] **Step 4: `ScoreBar` (barra fija inferior)**

```tsx
// frontend/src/modules/ucca/components/ScoreBar.tsx
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { brandTokens } from "../../../theme/brand-tokens";
import { formatScore, type ScoreResult } from "../scoring";
import { OutcomeBadge } from "./OutcomeBadge";

function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div style={{ display: "grid", gap: 2 }}>
      <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", color: brandTokens.colors.textSecondary }}>{label}</span>
      <span style={{ fontSize: 18, fontWeight: 600 }}>{value}</span>
    </div>
  );
}

export function ScoreBar({ score, answered, total, actions }: { score: ScoreResult; answered: number; total: number; actions: ReactNode }) {
  const { t } = useTranslation();
  return (
    <div style={{ position: "sticky", bottom: 0, zIndex: 5, background: brandTokens.colors.surface, borderTop: `1px solid ${brandTokens.colors.border}`,
                  boxShadow: "0 -6px 24px rgba(22, 69, 92, 0.08)", padding: "12px 20px", display: "flex", alignItems: "center",
                  justifyContent: "space-between", gap: 20, flexWrap: "wrap", marginTop: 24, borderRadius: `${brandTokens.radius.md}px ${brandTokens.radius.md}px 0 0` }}>
      <div style={{ display: "flex", gap: 28, alignItems: "center", flexWrap: "wrap" }}>
        <Stat label={t("ucca.form.answered", { done: answered, total })} value={`${answered}/${total}`} />
        <Stat label={t("ucca.form.applicable")} value={score.applicable} />
        <Stat label={t("ucca.form.yesCount")} value={score.yes} />
        <Stat label={t("ucca.form.score")} value={formatScore(score.score)} />
        <Stat label={t("ucca.form.outcome")} value={<OutcomeBadge outcome={score.outcome} size="lg" />} />
      </div>
      <div style={{ display: "flex", gap: 10 }}>{actions}</div>
    </div>
  );
}
```

- [ ] **Step 5: `FindingSection`**

```tsx
// frontend/src/modules/ucca/components/FindingSection.tsx
import { useTranslation } from "react-i18next";

import { FormField } from "../../../components/FormField";
import { brandTokens } from "../../../theme/brand-tokens";
import type { ActionStatus } from "../types";

export type FindingState = {
  enabled: boolean; description: string; actionEnabled: boolean; actionDescription: string;
  ownerId: string; dueDate: string; actionStatus: ActionStatus; closureEvidence: string;
};

export const EMPTY_FINDING: FindingState = {
  enabled: false, description: "", actionEnabled: false, actionDescription: "", ownerId: "", dueDate: "",
  actionStatus: "assigned", closureEvidence: "",
};

type Owner = { id: string; full_name: string; status?: string };
const STATUSES: ActionStatus[] = ["assigned", "in_progress", "closed"];

export function FindingSection({ state, onChange, required, owners, readOnly }: {
  state: FindingState; onChange: (s: FindingState) => void; required: boolean; owners: Owner[]; readOnly: boolean;
}) {
  const { t } = useTranslation();
  const set = (patch: Partial<FindingState>) => onChange({ ...state, ...patch });
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${required ? brandTokens.colors.warning : brandTokens.colors.border}`,
                  borderRadius: brandTokens.radius.lg, padding: 20, marginTop: 24 }}>
      <h2 style={{ fontSize: 17, margin: "0 0 6px" }}>{t("ucca.form.findingSection")}</h2>
      <p style={{ fontSize: 13, color: required ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary, margin: "0 0 14px" }}>
        {required ? t("ucca.form.findingHint") : t("ucca.form.findingOptional")}
      </p>
      {!required && !readOnly && (
        <label style={{ fontSize: 13, display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
          <input type="checkbox" checked={state.enabled} onChange={(e) => set({ enabled: e.target.checked })} /> {t("ucca.form.keyFinding")}
        </label>
      )}
      {(required || state.enabled) && (
        <>
          <FormField label={t("ucca.form.keyFinding")} required>
            <textarea rows={2} value={state.description} disabled={readOnly} required onChange={(e) => set({ description: e.target.value })} />
          </FormField>
          <label style={{ fontSize: 13, display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
            <input type="checkbox" checked={state.actionEnabled} disabled={readOnly} onChange={(e) => set({ actionEnabled: e.target.checked })} /> {t("ucca.form.correctiveAction")}
          </label>
          {state.actionEnabled && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0 16px" }}>
              <div style={{ gridColumn: "1 / -1" }}>
                <FormField label={t("ucca.form.correctiveAction")} required>
                  <textarea rows={2} value={state.actionDescription} disabled={readOnly} required onChange={(e) => set({ actionDescription: e.target.value })} />
                </FormField>
              </div>
              <FormField label={t("ucca.form.owner")} required>
                <select value={state.ownerId} disabled={readOnly} required onChange={(e) => set({ ownerId: e.target.value })}>
                  <option value="">{t("ucca.form.ownerPlaceholder")}</option>
                  {owners.filter((o) => o.status === undefined || o.status === "active").map((o) => <option key={o.id} value={o.id}>{o.full_name}</option>)}
                </select>
              </FormField>
              <FormField label={t("ucca.form.dueDate")} required>
                <input type="date" value={state.dueDate} disabled={readOnly} required onChange={(e) => set({ dueDate: e.target.value })} />
              </FormField>
              <FormField label={t("ucca.form.actionStatus")}>
                <select value={state.actionStatus} disabled={readOnly} onChange={(e) => set({ actionStatus: e.target.value as ActionStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{t(`ucca.actionStatuses.${s}`)}</option>)}
                </select>
              </FormField>
              <FormField label={t("ucca.form.closureEvidence")}>
                <input value={state.closureEvidence} disabled={readOnly} onChange={(e) => set({ closureEvidence: e.target.value })} />
              </FormField>
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Página `ChartAuditPage`**

```tsx
// frontend/src/modules/ucca/ChartAuditPage.tsx
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ApiError, apiPatchJson, apiPostJson } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { FormField } from "../../components/FormField";
import { PageHeader } from "../../components/PageHeader";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import { brandTokens } from "../../theme/brand-tokens";
import { CriterionCard, type AnswerState } from "./components/CriterionCard";
import { EMPTY_FINDING, FindingSection, type FindingState } from "./components/FindingSection";
import { ScoreBar } from "./components/ScoreBar";
import { computeScore } from "./scoring";
import type { AnswerValue, ChartAudit, ChartAuditWrite, Criterion, Cycle, Professional } from "./types";

type Owner = { id: string; full_name: string; status?: string };

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export function ChartAuditPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { session } = useAuth();
  const me = useCurrentUser();
  const { cycleId: cycleParam, auditId } = useParams<{ cycleId?: string; auditId?: string }>();
  const isEdit = Boolean(auditId);

  const existing = useApiGet<ChartAudit>(auditId ? `/ucca/audits/${auditId}` : "");
  const cycleId = cycleParam ?? existing.data?.cycle_id ?? "";
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const cycle = cycles.data.find((c) => c.id === cycleId);
  const criteria = useApiList<Criterion>("/ucca/criteria?only_active=true");
  const professionals = useApiList<Professional>("/identity/professionals");
  const owners = useApiList<Owner>("/identity/users");

  const canCreate = me?.permissions.includes("ucca.create") ?? false;
  const canApprove = me?.permissions.includes("ucca.approve") ?? false;

  const [professionalId, setProfessionalId] = useState("");
  const [caseRef, setCaseRef] = useState("");
  const [auditDate, setAuditDate] = useState(today());
  const [notes, setNotes] = useState("");
  const [answers, setAnswers] = useState<Record<string, AnswerState>>({});
  const [finding, setFinding] = useState<FindingState>(EMPTY_FINDING);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [showErrors, setShowErrors] = useState(false);

  // Carga de una auditoría existente → estado del formulario.
  useEffect(() => {
    const a = existing.data;
    if (!a) return;
    setProfessionalId(a.professional_id);
    setCaseRef(a.case_reference);
    setAuditDate(a.audit_date);
    setNotes(a.notes);
    setAnswers(Object.fromEntries(a.answers.map((x) => [x.criterion_id, { outcome: x.outcome, reason: x.not_applicable_reason ?? "", comment: x.comment ?? "" }])));
    if (a.finding) {
      const ca = a.finding.corrective_action;
      setFinding({ enabled: true, description: a.finding.description, actionEnabled: Boolean(ca), actionDescription: ca?.description ?? "",
                   ownerId: ca?.responsible_user_id ?? "", dueDate: ca?.due_date ?? "", actionStatus: ca?.status ?? "assigned",
                   closureEvidence: ca?.closure_evidence ?? "" });
    }
  }, [existing.data]);

  const status = existing.data?.status ?? "draft";
  const readOnly = status !== "draft" || !canCreate;
  const professional = professionals.data.find((p) => p.id === professionalId);
  const facilityProfessionals = useMemo(
    () => professionals.data.filter((p) => p.primary_facility_id === cycle?.facility_id && p.is_active !== false),
    [professionals.data, cycle?.facility_id],
  );

  const answered = criteria.data.filter((c) => answers[c.id]?.outcome).length;
  const live = computeScore(criteria.data.map((c) => answers[c.id]?.outcome).filter((o): o is AnswerValue => Boolean(o)));
  const hasNo = criteria.data.some((c) => answers[c.id]?.outcome === "non_compliant");
  const findingRequired = live.outcome !== null && live.outcome !== "compliant" && hasNo;

  function validate(): string | null {
    const missing = criteria.data.length - answered;
    if (missing > 0) return t("ucca.form.missingAnswers", { count: missing });
    if (criteria.data.some((c) => answers[c.id]?.outcome === "not_applicable" && !answers[c.id].reason.trim())) return t("ucca.form.missingNaReason");
    if (findingRequired && !finding.description.trim()) return t("ucca.form.missingFinding");
    return null;
  }

  function payload(): ChartAuditWrite {
    const includeFinding = findingRequired || finding.enabled;
    return {
      professional_id: professionalId, case_reference: caseRef.trim(), audit_date: auditDate, notes,
      answers: criteria.data.map((c) => ({
        criterion_id: c.id, outcome: answers[c.id].outcome as AnswerValue,
        not_applicable_reason: answers[c.id].outcome === "not_applicable" ? answers[c.id].reason.trim() : null,
        comment: answers[c.id].comment.trim() || null,
      })),
      finding: includeFinding && finding.description.trim() ? {
        description: finding.description.trim(),
        corrective_action: finding.actionEnabled ? {
          description: finding.actionDescription.trim(), responsible_user_id: finding.ownerId, due_date: finding.dueDate,
          status: finding.actionStatus, closure_evidence: finding.closureEvidence.trim() || null,
        } : null,
      } : null,
    };
  }

  async function save(e?: FormEvent) {
    e?.preventDefault();
    setShowErrors(true);
    const problem = validate();
    if (problem) { setError(problem); return; }
    setSaving(true); setError(null); setMessage(null);
    try {
      const saved = isEdit
        ? await apiPatchJson<ChartAudit>(`/ucca/audits/${auditId}`, payload(), session?.token)
        : await apiPostJson<ChartAudit>(`/ucca/cycles/${cycleId}/audits`, payload(), session?.token);
      setMessage(t("ucca.form.saved"));
      if (!isEdit) navigate(`/ucca/audits/${saved.id}`, { replace: true });
      else existing.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ucca.form.saveError"));
    } finally { setSaving(false); }
  }

  async function transition(kind: "submit" | "approve") {
    if (!auditId) return;
    setSaving(true); setError(null); setMessage(null);
    try {
      await apiPostJson<ChartAudit>(`/ucca/audits/${auditId}/${kind}`, {}, session?.token);
      setMessage(t(kind === "submit" ? "ucca.form.submitted" : "ucca.form.approved"));
      existing.reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ucca.form.saveError"));
    } finally { setSaving(false); }
  }

  if (isEdit && existing.loading) return <p>{t("ucca.form.loading")}</p>;
  if (isEdit && !existing.loading && !existing.data) return <p>{t("ucca.form.notFound")}</p>;
  if (!cycleId) return <p>{t("ucca.cycleMissing")}</p>;

  return (
    <section>
      <p style={{ margin: "0 0 18px" }}>
        <Link to={`/ucca/cycles/${cycleId}`} style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 500 }}>← {t("ucca.backToCycle")}</Link>
      </p>
      <PageHeader title={isEdit ? t("ucca.form.editTitle", { mrn: existing.data?.case_reference ?? "" }) : t("ucca.form.newTitle")}
                  subtitle={`${cycle?.period_label ?? ""} · ${cycle?.facility_name ?? ""} — ${t("ucca.form.subtitle")}`} />
      {status === "approved" && <p role="status" style={{ color: brandTokens.colors.textSecondary, fontSize: 13 }}>{t("ucca.form.approvedNotice")}</p>}
      {status === "submitted" && <p role="status" style={{ color: brandTokens.colors.textSecondary, fontSize: 13 }}>{t("ucca.form.readOnly", { status: t("ucca.statuses.submitted") })}</p>}

      <form id="audit-form" onSubmit={save}>
        <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`, borderRadius: brandTokens.radius.lg, padding: 20 }}>
          <h2 style={{ fontSize: 17, margin: "0 0 14px" }}>{t("ucca.form.dataSection")}</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0 16px" }}>
            <FormField label={t("ucca.form.professional")} required>
              <select value={professionalId} disabled={readOnly} required onChange={(e) => setProfessionalId(e.target.value)}>
                <option value="">{t("ucca.form.professionalPlaceholder")}</option>
                {facilityProfessionals.map((p) => <option key={p.id} value={p.id}>{p.full_name} · {p.profession_name}</option>)}
              </select>
            </FormField>
            <FormField label={t("ucca.form.cgId")}><input value={professional?.employee_number ?? ""} readOnly /></FormField>
            <FormField label={t("ucca.form.profession")}><input value={professional?.profession_name ?? ""} readOnly /></FormField>
            <FormField label={t("ucca.form.mrn")} required>
              <input value={caseRef} disabled={readOnly} required placeholder={t("ucca.form.mrnPlaceholder")} onChange={(e) => setCaseRef(e.target.value)} />
            </FormField>
            <FormField label={t("ucca.form.date")} required>
              <input type="date" value={auditDate} disabled={readOnly} required onChange={(e) => setAuditDate(e.target.value)} />
            </FormField>
            <FormField label={t("ucca.form.auditor")}><input value={existing.data?.auditor_name ?? me?.full_name ?? ""} readOnly /></FormField>
          </div>
        </div>

        <h2 style={{ fontSize: 17, margin: "24px 0 12px" }}>{t("ucca.form.criteriaSection")}</h2>
        <div style={{ display: "grid", gap: 12 }}>
          {criteria.data.map((c) => (
            <CriterionCard key={c.id} criterion={c} readOnly={readOnly}
              state={answers[c.id] ?? { outcome: null, reason: "", comment: "" }}
              invalid={showErrors && (!answers[c.id]?.outcome || (answers[c.id]?.outcome === "not_applicable" && !answers[c.id].reason.trim()))}
              onChange={(next) => setAnswers((a) => ({ ...a, [c.id]: next }))} />
          ))}
        </div>

        <FormField label={t("ucca.form.notes")}>
          <textarea rows={2} value={notes} disabled={readOnly} onChange={(e) => setNotes(e.target.value)} />
        </FormField>

        <FindingSection state={finding} onChange={setFinding} required={findingRequired} owners={owners.data} readOnly={readOnly} />
      </form>

      {message && <p role="status" style={{ color: brandTokens.colors.success, marginTop: 12 }}>{message}</p>}
      {error && <p role="alert" style={{ color: brandTokens.colors.danger, marginTop: 12 }}>{error}</p>}

      <ScoreBar score={live} answered={answered} total={criteria.data.length} actions={
        <>
          {!readOnly && <button type="submit" form="audit-form" className="btn-primary" disabled={saving}>{saving ? t("ucca.form.saving") : t("ucca.form.saveDraft")}</button>}
          {isEdit && status === "draft" && canCreate && <button type="button" className="btn-ghost" disabled={saving} onClick={() => transition("submit")}>{t("ucca.form.submit")}</button>}
          {isEdit && status === "submitted" && canApprove && <button type="button" className="btn-primary" disabled={saving} onClick={() => transition("approve")}>{t("ucca.form.approve")}</button>}
        </>
      } />
    </section>
  );
}
```

Nota: `GET /identity/users` devuelve `status`; `GET /identity/professionals` devuelve `profession_name`, `employee_number`, `primary_facility_id` (ver `identity/schemas.py::ProfessionalOut`; si falta `employee_number` o `is_active`, añadirlos al schema en este Task).

- [ ] **Step 7: Build + verificación con Playwright**

Run: `npm --prefix /Users/danielsandoval/Documents/Proyectos/clinical-governance/frontend run build` → `✓ built`.
Flujo en `http://localhost:5173/ucca/cycles/<id>/audits/new`: elegir profesional (CG_ID y profesión se rellenan), MRN `102453`, marcar 5 Yes + 1 N/A (con razón) + 1 No → barra muestra `6/7 … 5 … 83.33 % … Minor Improvement`; sección de hallazgo aparece; guardar sin hallazgo → mensaje de validación; con hallazgo + acción (responsable, fecha) → redirige a `/ucca/audits/<id>` con estado Borrador; **Enviar** → Enviado y campos deshabilitados; **Aprobar** → Aprobado. Volver al ciclo: fila con chips ✓/✗/N/A, score y outcome. Confirmar sin scroll horizontal.

- [ ] **Step 8: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add frontend/src
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca-ui): chart audit form — criterion cards, live score bar, finding and corrective action

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: Dashboard UCCA (`/ucca/dashboard`)

**Files:**
- Create: `frontend/src/modules/ucca/components/RateBars.tsx`
- Replace: `frontend/src/modules/ucca/UccaAnalyticsPage.tsx`

**Interfaces:**
- Consumes: `GET /ucca/dashboard?facility_id=&year=&quarter=` → `Summary`; `GET /identity/facilities`; `GET /ucca/cycles` (para poblar años disponibles).
- Produces: `<RateBars items={{label, value: number | null}[]} />` (barras horizontales CSS, sin librerías).

- [ ] **Step 1: `RateBars`**

```tsx
// frontend/src/modules/ucca/components/RateBars.tsx
import { alkalma, brandTokens } from "../../../theme/brand-tokens";
import { outcomeFor } from "../scoring";

const COLOR: Record<string, string> = {
  compliant: alkalma.turquoise, minor_improvement: alkalma.amber, improvement_required: "#D98B2B",
  priority_corrective_action: brandTokens.colors.danger,
};

/** Barras horizontales 0–100 %; color según banda de outcome del valor. */
export function RateBars({ items }: { items: { label: string; value: number | null; hint?: string }[] }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {items.map((it) => {
        const outcome = outcomeFor(it.value);
        return (
          <div key={it.label} style={{ display: "grid", gridTemplateColumns: "72px 1fr 64px", alignItems: "center", gap: 10, fontSize: 13 }}>
            <span style={{ fontWeight: 600 }}>{it.label}</span>
            <div style={{ background: alkalma.bgSoft, borderRadius: 999, height: 12, overflow: "hidden" }} title={it.hint}>
              <div style={{ width: `${it.value ?? 0}%`, height: "100%", background: outcome ? COLOR[outcome] : alkalma.bluegray, transition: "width .2s" }} />
            </div>
            <span style={{ textAlign: "right", color: brandTokens.colors.textSecondary }}>{it.value === null ? "—" : `${it.value} %`}</span>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Página**

```tsx
// frontend/src/modules/ucca/UccaAnalyticsPage.tsx
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { DataTable } from "../../components/DataTable";
import { PageHeader } from "../../components/PageHeader";
import { StatusBadge } from "../../components/StatusBadge";
import { useApiGet } from "../../hooks/useApiGet";
import { useApiList } from "../../hooks/useApiList";
import { brandTokens } from "../../theme/brand-tokens";
import { KpiCard } from "./components/KpiCard";
import { OutcomeBadge } from "./components/OutcomeBadge";
import { RateBars } from "./components/RateBars";
import { formatScore } from "./scoring";
import type { Cycle, Summary } from "./types";

type Facility = { id: string; name: string };
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: brandTokens.colors.surface, border: `1px solid ${brandTokens.colors.border}`, borderRadius: brandTokens.radius.lg,
                  boxShadow: brandTokens.shadow.card, padding: 20, minWidth: 0 }}>
      <h2 style={{ fontSize: 16, margin: "0 0 14px" }}>{title}</h2>
      {children}
    </div>
  );
}

export function UccaAnalyticsPage() {
  const { t } = useTranslation();
  const facilities = useApiList<Facility>("/identity/facilities");
  const cycles = useApiList<Cycle>("/ucca/cycles");
  const [facilityId, setFacilityId] = useState("");
  const [year, setYear] = useState("");
  const [quarter, setQuarter] = useState("");

  const query = useMemo(() => {
    const q = new URLSearchParams();
    if (facilityId) q.set("facility_id", facilityId);
    if (year) q.set("year", year);
    if (quarter) q.set("quarter", quarter);
    const s = q.toString();
    return `/ucca/dashboard${s ? `?${s}` : ""}`;
  }, [facilityId, year, quarter]);
  const summary = useApiGet<Summary>(query);
  const years = Array.from(new Set(cycles.data.map((c) => c.year))).sort((a, b) => b - a);
  const s = summary.data;
  const compliantRate = s && s.audits_count > 0 ? Math.round((s.outcome_distribution.compliant / s.audits_count) * 100) : null;
  const codes = s?.criteria.map((c) => c.code) ?? [];

  const select = (value: string, onChange: (v: string) => void, options: { value: string; label: string }[], label: string) => (
    <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600, color: brandTokens.colors.textSecondary }}>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)} style={{ minWidth: 160 }}>
        <option value="">{t("ucca.dashboard.filters.all")}</option>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  );

  return (
    <section>
      <PageHeader title={t("ucca.dashboard.title")} subtitle={t("ucca.dashboard.subtitle")} />
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
        {select(facilityId, setFacilityId, facilities.data.map((f) => ({ value: f.id, label: f.name })), t("ucca.dashboard.filters.facility"))}
        {select(year, setYear, years.map((y) => ({ value: String(y), label: String(y) })), t("ucca.dashboard.filters.year"))}
        {select(quarter, setQuarter, QUARTERS.map((q) => ({ value: q, label: q })), t("ucca.dashboard.filters.quarter"))}
      </div>

      {summary.loading && <p>{t("app.loading")}</p>}
      {summary.error && <p>{summary.error}</p>}
      {s && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 20 }}>
            <KpiCard label={t("ucca.kpi.audits")} value={s.audits_count} hint={s.draft_count > 0 ? t("ucca.kpi.drafts", { count: s.draft_count }) : undefined} />
            <KpiCard label={t("ucca.kpi.averageScore")} value={formatScore(s.average_score)} />
            <KpiCard label={t("ucca.kpi.compliantRate")} value={compliantRate === null ? "—" : `${compliantRate} %`} />
            <KpiCard label={t("ucca.kpi.openActions")} value={s.open_corrective_actions.length} />
          </div>
          {s.audits_count === 0 && <p style={{ color: brandTokens.colors.textSecondary }}>{t("ucca.dashboard.empty")}</p>}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16, marginBottom: 20 }}>
            <Card title={t("ucca.dashboard.byCriterion")}>
              <RateBars items={s.criteria.map((c) => ({ label: c.code, value: c.yes_rate, hint: `${c.yes}/${c.applicable}` }))} />
            </Card>
            <Card title={t("ucca.dashboard.trend")}>
              <RateBars items={s.trend.map((p) => ({ label: `${p.quarter}-${p.year}`, value: p.average_score, hint: `${p.audits_count}` }))} />
            </Card>
          </div>

          <Card title={t("ucca.dashboard.byProfessional")}>
            <DataTable
              rows={s.professionals.map((p) => ({ ...p, id: p.professional_id }))}
              emptyMessage={t("ucca.dashboard.empty")}
              columns={[
                { key: "cg", header: t("ucca.table.cgId"), width: 80, render: (r) => <code style={{ fontSize: 12 }}>{r.employee_number}</code> },
                { key: "name", header: t("ucca.table.professional"), render: (r) => (
                  <span style={{ display: "block", fontSize: 13 }}><strong style={{ fontWeight: 500 }}>{r.professional_name}</strong>
                    <span style={{ display: "block", fontSize: 12, color: brandTokens.colors.textSecondary }}>{r.profession_name ?? "—"}</span></span>
                ) },
                { key: "n", header: t("ucca.auditsCount"), width: 60, render: (r) => r.audits_count },
                { key: "score", header: t("ucca.table.score"), width: 72, render: (r) => <strong style={{ fontSize: 13 }}>{formatScore(r.average_score)}</strong> },
                { key: "outcome", header: t("ucca.table.outcome"), width: 150, render: (r) => <OutcomeBadge outcome={r.outcome} /> },
                ...codes.map((code) => ({ key: code, header: code, width: 52,
                  render: (r: Summary["professionals"][number]) => <span style={{ fontSize: 12 }}>{r.criteria[code] === null ? "—" : `${r.criteria[code]}%`}</span> })),
              ]}
            />
          </Card>

          <div style={{ marginTop: 20 }}>
            <Card title={t("ucca.dashboard.openActions")}>
              <DataTable
                rows={s.open_corrective_actions}
                emptyMessage={t("ucca.dashboard.noActions")}
                columns={[
                  { key: "mrn", header: t("ucca.table.mrn"), width: 110, render: (r) => (
                    <Link to={`/ucca/audits/${r.audit_id}`} style={{ color: brandTokens.colors.link, textDecoration: "none", fontWeight: 600 }}>{r.case_reference}</Link>
                  ) },
                  { key: "pro", header: t("ucca.table.professional"), render: (r) => r.professional_name },
                  { key: "finding", header: t("ucca.dashboard.finding"), render: (r) => <span style={{ fontSize: 13 }}>{r.finding}</span> },
                  { key: "owner", header: t("ucca.dashboard.owner"), width: 140, render: (r) => r.responsible_name ?? "—" },
                  { key: "due", header: t("ucca.dashboard.due"), width: 100, render: (r) => r.due_date },
                  { key: "st", header: t("ucca.table.status"), width: 100, render: (r) => <StatusBadge code={r.status} ns="ucca.actionStatuses" /> },
                ]}
              />
            </Card>
          </div>
        </>
      )}
    </section>
  );
}
```

- [ ] **Step 3: Build + verificación**

Run: `npm --prefix /Users/danielsandoval/Documents/Proyectos/clinical-governance/frontend run build` → `✓ built`.
Playwright en `/ucca/dashboard`: con la auditoría aprobada de Task 8, KPIs > 0, barras por criterio, fila del profesional con outcome, acción abierta listada; filtro trimestre distinto → mensaje vacío; sin scroll horizontal a 1280px.

- [ ] **Step 4: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add frontend/src/modules/ucca
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "feat(ucca-ui): dashboard with filters, criterion rates, practitioner table and open actions

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Seed demo, documentación y grafo

**Files:**
- Modify: `backend/app/scripts/seed_demo_data.py` (`_seed_sample_cycle` → ciclo Q2-2026 + 6 auditorías)
- Modify: `README.md` (sección "Datos de demostración" y tabla de pantallas; añadir fila UCCA)
- Create: `docs/AEGIS_M04_UCCA_Chart_Audit.md`
- Modify: `frontend/src/i18n/{es,en}.json` → `nav.uccaCycles` pasa a "UCCA — Ciclos" / "UCCA — Cycles" (sin cambio si ya lo es)

- [ ] **Step 1: Seed**

Reemplazar `_seed_sample_cycle` por:

```python
from datetime import date

from app.domains.governance.corrective_actions.models import CorrectiveAction
from app.domains.governance.ucca.models import ChartAudit, AuditResult, Finding  # añadir al import existente
from app.domains.governance.ucca.scoring import compute_score

# (MRN, respuestas por código en orden CCA,CRS,CTP,COM,CDC,CEP,CMC) — los 5 primeros como el Excel.
DEMO_CHART_AUDITS = [
    ("102453", ["compliant"] * 7),
    ("100598", ["compliant"] * 7),
    ("AKAD00132", ["compliant"] * 7),
    ("AKAD00264", ["compliant"] * 7),
    ("101460", ["compliant"] * 7),
    ("103877", ["compliant", "non_compliant", "compliant", "not_applicable", "compliant", "compliant", "non_compliant"]),
]


def _seed_sample_cycle(db: Session, facilities, users, template_version) -> None:
    auditor = users["governance.lead@alkalma.health"]
    facility = facilities["Al Bateen"]
    cycle = db.scalar(select(AuditCycle).where(AuditCycle.facility_id == facility.id, AuditCycle.year == 2026, AuditCycle.quarter == "Q2"))
    if not cycle:
        cycle = AuditCycle(facility_id=facility.id, template_version_id=template_version.id, period_label="Q2-2026",
                           year=2026, quarter="Q2", status="draft", created_by_user_id=auditor.id)
        db.add(cycle)
        db.flush()
    # Ciclo Q3-2026 histórico se conserva si existe (creado por seeds anteriores).
    professional = db.scalar(select(Professional).where(Professional.employee_number == "PRO-101"))  # Dr. Ahmed Al Bateen
    criteria = {c.code: c for c in db.scalars(select(AuditCriterion).where(AuditCriterion.template_version_id == template_version.id)).all()}
    codes = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]
    if not professional or any(code not in criteria for code in codes):
        return
    for case_ref, outcomes in DEMO_CHART_AUDITS:
        if db.scalar(select(ChartAudit).where(ChartAudit.cycle_id == cycle.id, ChartAudit.professional_id == professional.id,
                                              ChartAudit.case_reference == case_ref)):
            continue
        score = compute_score(outcomes)
        audit = ChartAudit(cycle_id=cycle.id, facility_id=facility.id, professional_id=professional.id, auditor_user_id=auditor.id,
                           case_reference=case_ref, audit_date=date(2026, 7, 20), status="approved",
                           applicable_count=score.applicable_count, yes_count=score.yes_count, score=score.score,
                           outcome=score.outcome, notes="")
        db.add(audit)
        db.flush()
        for code, outcome in zip(codes, outcomes):
            db.add(AuditResult(chart_audit_id=audit.id, facility_id=facility.id, cycle_id=cycle.id, criterion_id=criteria[code].id,
                               professional_id=professional.id, auditor_user_id=auditor.id, outcome=outcome,
                               not_applicable_reason="Outcome monitoring not yet due at audit date" if outcome == "not_applicable" else None,
                               status="approved"))
        if score.outcome not in (None, "compliant"):
            finding = Finding(facility_id=facility.id, chart_audit_id=audit.id,
                              description="Risk documentation and MDT communication incomplete in the audited chart.", status="open")
            db.add(finding)
            db.flush()
            db.add(CorrectiveAction(facility_id=facility.id, source_module="ucca", source_finding_id=finding.id,
                                    responsible_user_id=users["md.bateen@alkalma.health"].id, due_date=date(2026, 8, 30),
                                    status="assigned", description="Refresher on risk assessment documentation; audit 5 further charts in Q3."))
```

Actualizar la llamada en `run()` para pasar `facilities, users, template_version` como ya hace, y el resumen impreso: `print(f"  Auditorías de expediente demo: {db.scalar(select(func.count(ChartAudit.id)))}")` (import `func` de sqlalchemy).

Run (cwd `backend/`): `./.venv/bin/python -m app.scripts.seed_demo_data` → "Auditorías de expediente demo: 6". Ejecutar dos veces → mismo conteo (idempotente).

- [ ] **Step 2: README**

En "Datos de demostración" sustituir el texto del ciclo por: `… la plantilla UCCA v1 con los 7 criterios de evaluación (CCA, CRS, CTP, COM, CDC, CEP, CMC), un ciclo Q2-2026 en Al Bateen con 6 expedientes auditados (5 Compliant, 1 con hallazgo y acción correctiva) y el ciclo Q3-2026 vacío.`

Añadir sección tras "Módulo administrativo":

```markdown
## UCCA — Auditoría por expediente (M04)

Diseño: `docs/superpowers/specs/2026-10-12-ucca-chart-audit-design.md` · Guía: `docs/AEGIS_M04_UCCA_Chart_Audit.md`.

| Pantalla | Endpoints | Notas |
|---|---|---|
| UCCA — Ciclos | `GET/POST /ucca/cycles` | Un ciclo por centro + año + trimestre. |
| Página del ciclo | `GET /ucca/cycles/{id}/audits`, `GET /ucca/cycles/{id}/summary` | Tabla tipo Excel: una fila por expediente con Yes/No/N/A por criterio, score y outcome. |
| Auditar expediente | `POST /ucca/cycles/{id}/audits`, `GET/PATCH /ucca/audits/{id}`, `POST …/submit`, `POST …/approve` | 7 criterios en una pantalla; score = Yes / aplicables (N/A excluidos, razón obligatoria); outcome ≥90 Compliant · ≥80 Minor Improvement · ≥70 Improvement Required · <70 Priority Corrective Action. Hallazgo + acción correctiva (M06) en la misma pantalla. Aprobada = inmutable. |
| UCCA — Dashboard | `GET /ucca/dashboard?facility_id&year&quarter` | Solo auditorías enviadas/aprobadas; % Yes por criterio, por profesional, tendencia por trimestre, acciones abiertas. |
```

- [ ] **Step 3: Documento M04**

Crear `docs/AEGIS_M04_UCCA_Chart_Audit.md` con: objetivo (1 párrafo), flujo del director médico (5 pasos: crear ciclo → nueva auditoría → responder 7 criterios → hallazgo/acción si procede → enviar/aprobar), fórmulas (copiar §3.2 del spec), mapa Excel → AEGIS (tabla: Audit ID→`id`, Year/Quarter→ciclo, CG_ID→`professionals.employee_number`, Practitioner/Profession→profesional, Center→centro del ciclo, MRN/Case Ref→`case_reference`, Audit Date→`audit_date`, Auditor→`auditor_user_id`, CCA…CMC→`ucca_audit_results.outcome`, Applicable/Yes Count/Score/Outcome→columnas calculadas, Key Finding→`ucca_findings.description`, Corrective Action/Owner/Due Date/Status/Closure Evidence→`corrective_actions`), y tabla de estado de implementación (todo ✅ salvo capa OMH/JAWDA, exportación Excel, umbrales configurables: pendiente).

- [ ] **Step 4: Verificación final end-to-end**

1. `cd backend && ./.venv/bin/python -m pytest -q` → todo verde.
2. `npm --prefix frontend run build` → `✓ built`.
3. Playwright, 1280px: `/ucca` lista Q2-2026 con 6 expedientes y score medio 94.05; abrir ciclo → KPIs (6, 94.05 %, 83 %, 1), tabla con 6 filas, chips, outcome Priority Corrective Action en `103877` con punto ámbar; abrir `103877` → solo lectura (aprobada), hallazgo y acción visibles; `/ucca/dashboard` → barras (CRS 83.33 %, COM 100 % con 5 aplicables, CMC 83.33 %), profesional Dr. Ahmed Al Bateen con outcome Compliant (94.05), acción abierta listada; filtro `Q3` → vacío. Ninguna página con scroll horizontal.
4. `graphify update .` desde la raíz.

- [ ] **Step 5: Commit**

```bash
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance add -A
git -C /Users/danielsandoval/Documents/Proyectos/clinical-governance commit -m "docs(ucca): demo chart audits, README section, M04 guide, graph refresh

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Self-review del plan (hecho al escribirlo)

- **Cobertura del spec:** §3 modelo → Task 2; §3.2 cálculo → Task 1 (+ espejo en Task 6); §4 API → Tasks 3, 4, 5; §5.1 → Task 6; §5.2 → Task 7; §5.3 → Task 8; §5.4 → Task 9; §6 agregados → Task 5; §7 seed → Task 10; §8 pruebas → cada Task + verificación final; permisos §3.3 → routers de Tasks 3–5.
- **Consistencia de nombres:** `compute_score`/`computeScore`, `ScoreResult`, `outcome_for`/`outcomeFor`, `ChartAuditWriteRequest`/`ChartAuditWrite`, `ChartAuditRowOut`/`ChartAuditRow`, `SummaryOut`/`Summary`, `useApiGet`, `OutcomeBadge`, `AnswerChip`, `KpiCard`, `RateBars`, `FindingState`/`EMPTY_FINDING` usados con la misma firma en todas las tareas.
- **Review Focus:** cada punto tiene su test nombrado en la tarea dueña (Tasks 1, 3, 4, 5).
- **Nota de ejecución:** en Task 3 el orden de consultas con `FakeSession` es la parte frágil; si un test falla por orden, corregir el test al orden documentado en docstrings del servicio, nunca alterar el servicio para "cuadrar" un fake.
