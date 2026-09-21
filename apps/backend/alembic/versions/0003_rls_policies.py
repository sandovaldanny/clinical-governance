"""Row-Level Security multi-centro (sección 5.2 de la arquitectura técnica).

Patrón obligatorio para TODA tabla operativa nueva que incluya facility_id: habilitar RLS y
crear una política que permita la fila si el centro está en app.current_facility_ids, o si
app.current_is_corporate = true. Este archivo aplica el patrón a las tablas ya creadas
(user_facility_assignments, professionals) y sirve de plantilla para cada módulo nuevo.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-08
"""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

_FACILITY_SCOPED_TABLES = [
    "professionals",
]


def _enable_rls(table: str, facility_column: str = "facility_id") -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
    op.execute(
        f"""
        CREATE POLICY {table}_facility_scope ON {table}
        USING (
            current_setting('app.current_is_corporate', true) = 'true'
            OR {facility_column}::text = ANY (
                string_to_array(current_setting('app.current_facility_ids', true), ',')
            )
        );
        """
    )


def upgrade() -> None:
    _enable_rls("professionals", facility_column="primary_facility_id")


def downgrade() -> None:
    for table in _FACILITY_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_facility_scope ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
