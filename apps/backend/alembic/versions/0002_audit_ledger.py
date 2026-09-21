"""Audit ledger inmutable (M10, sección 7 de la arquitectura técnica).

La tabla es append-only por diseño: NO se otorgan permisos de UPDATE/DELETE al rol de aplicación,
ni siquiera al System Administrator vía interfaz funcional (regla crítica del funcional).

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_user_id", sa.String(64), nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("is_retrospective", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id"])
    op.create_index("ix_audit_events_module", "audit_events", ["module"])

    # Revoca explícitamente UPDATE/DELETE del rol de aplicación (ajustar "aegis_app" al rol de
    # base de datos real usado por el backend en cada entorno).
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aegis_app') THEN
                REVOKE UPDATE, DELETE ON audit_events FROM aegis_app;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.drop_index("ix_audit_events_module", table_name="audit_events")
    op.drop_index("ix_audit_events_entity", table_name="audit_events")
    op.drop_table("audit_events")
