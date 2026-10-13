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
    # Base nueva: 0004 ya creó ucca_chart_audits y las columnas de esta revisión.
    if sa.inspect(op.get_bind()).has_table("ucca_chart_audits"):
        return

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
