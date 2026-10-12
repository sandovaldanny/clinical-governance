"""Criterios de evaluación: la plantilla UCCA pasa a la estructura Código · Dominio · Pregunta
universal · Interpretación por profesión · Ejemplos/Evidencia (+ estado activo). Se descartan
los criterios iniciales de demostración (DOC/SAF/GOV/REG/JAWDA/PROF/MED/PSY/OMH) siempre que no
tengan resultados asociados; el seed carga los 7 criterios definitivos.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-12
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM ucca_audit_criteria c
        WHERE NOT EXISTS (SELECT 1 FROM ucca_audit_results r WHERE r.criterion_id = c.id)
        """
    )
    op.alter_column("ucca_audit_criteria", "description", new_column_name="universal_question")
    op.drop_column("ucca_audit_criteria", "severity")
    op.add_column("ucca_audit_criteria", sa.Column("domain", sa.String(120), nullable=False, server_default=""))
    op.add_column(
        "ucca_audit_criteria",
        sa.Column("profession_interpretation", sa.String(1000), nullable=False, server_default=""),
    )
    op.add_column(
        "ucca_audit_criteria",
        sa.Column("examples_evidence", sa.String(1000), nullable=False, server_default=""),
    )
    op.add_column(
        "ucca_audit_criteria",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # Criterios históricos conservados (con resultados): el dominio toma el código como etiqueta.
    op.execute("UPDATE ucca_audit_criteria SET domain = code WHERE domain = ''")
    op.alter_column("ucca_audit_criteria", "domain", server_default=None)


def downgrade() -> None:
    op.drop_column("ucca_audit_criteria", "is_active")
    op.drop_column("ucca_audit_criteria", "examples_evidence")
    op.drop_column("ucca_audit_criteria", "profession_interpretation")
    op.drop_column("ucca_audit_criteria", "domain")
    op.add_column(
        "ucca_audit_criteria",
        sa.Column("severity", sa.String(30), nullable=False, server_default="standard"),
    )
    op.alter_column("ucca_audit_criteria", "universal_question", new_column_name="description")
