"""M04 — tablas de UCCA y M06 — stub de Acciones Correctivas, con RLS aplicada por facility_id
siguiendo exactamente el patrón de 0003_rls_policies.py.

Nota: `create_all` materializa los modelos ACTUALES (incluida `ucca_chart_audits`, añadida en 0007).
En una base nueva las migraciones 0005–0007 detectan que el esquema ya está y no hacen nada; en bases
creadas antes de ellas aplican sus cambios incrementales.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-08
"""
from alembic import op

from app.core.database import Base
from app.domains.governance.corrective_actions import models as corrective_actions_models  # noqa: F401
from app.domains.governance.ucca import models as ucca_models  # noqa: F401

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

_TABLES = [
    "ucca_audit_templates",
    "ucca_audit_template_versions",
    "ucca_audit_criteria",
    "ucca_audit_cycles",
    "ucca_audit_results",
    "ucca_findings",
    "corrective_actions",
    "ucca_chart_audits",
]

_FACILITY_SCOPED_TABLES = [
    "ucca_audit_cycles",
    "ucca_audit_results",
    "ucca_findings",
    "corrective_actions",
    "ucca_chart_audits",
]


def upgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in _TABLES]
    Base.metadata.create_all(bind=bind, tables=tables)

    for table in _FACILITY_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        op.execute(
            f"""
            CREATE POLICY {table}_facility_scope ON {table}
            USING (
                current_setting('app.current_is_corporate', true) = 'true'
                OR facility_id::text = ANY (
                    string_to_array(current_setting('app.current_facility_ids', true), ',')
                )
            );
            """
        )


def downgrade() -> None:
    for table in _FACILITY_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_facility_scope ON {table};")
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in reversed(_TABLES)]
    Base.metadata.drop_all(bind=bind, tables=tables)
