"""M01 — campos del documento "Module 1 – User, Organization & Access Management":
nombre/apellido/móvil/estado en users, descripción en cargos, director y estado en centros,
descripción/estado en roles, módulo/nombre en permisos. Con backfill; se conservan is_active.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Base nueva: 0001 ya creó estas columnas desde los modelos actuales.
    if "status" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("users")}:
        return

    # users
    op.add_column("users", sa.Column("first_name", sa.String(120), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(120), nullable=True))
    op.add_column("users", sa.Column("mobile", sa.String(40), nullable=True))
    op.add_column("users", sa.Column("status", sa.String(20), nullable=False, server_default="active"))
    op.add_column("users", sa.Column("created_by_user_id", UUID(as_uuid=True), nullable=True))
    op.execute(
        """
        UPDATE users SET
            status = CASE WHEN is_active THEN 'active' ELSE 'inactive' END,
            first_name = split_part(full_name, ' ', 1),
            last_name = NULLIF(btrim(substr(full_name, length(split_part(full_name, ' ', 1)) + 1)), '')
        """
    )

    # organizational_positions
    op.add_column(
        "organizational_positions",
        sa.Column("description", sa.String(300), nullable=False, server_default=""),
    )

    # facilities
    op.add_column(
        "facilities",
        sa.Column("clinical_director_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("facilities", sa.Column("status", sa.String(20), nullable=False, server_default="active"))
    op.execute("UPDATE facilities SET status = CASE WHEN is_active THEN 'active' ELSE 'closed' END")

    # aegis_roles
    op.add_column("aegis_roles", sa.Column("description", sa.String(300), nullable=False, server_default=""))
    op.add_column("aegis_roles", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    # permissions
    op.add_column("permissions", sa.Column("module", sa.String(50), nullable=False, server_default=""))
    op.add_column("permissions", sa.Column("name", sa.String(150), nullable=False, server_default=""))
    op.execute("UPDATE permissions SET module = split_part(code, '.', 1), name = code WHERE module = ''")


def downgrade() -> None:
    op.drop_column("permissions", "name")
    op.drop_column("permissions", "module")
    op.drop_column("aegis_roles", "is_active")
    op.drop_column("aegis_roles", "description")
    op.drop_column("facilities", "status")
    op.drop_column("facilities", "clinical_director_user_id")
    op.drop_column("organizational_positions", "description")
    op.drop_column("users", "created_by_user_id")
    op.drop_column("users", "status")
    op.drop_column("users", "mobile")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
