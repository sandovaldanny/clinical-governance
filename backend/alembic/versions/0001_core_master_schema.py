"""Esquema maestro (M01 + M02): usuarios, roles, permisos, centros, profesiones, profesionales.

Revision ID: 0001
Revises:
Create Date: 2026-09-08
"""
from alembic import op

from app.core.database import Base
from app.domains.identity import models as identity_models  # noqa: F401

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_TABLES = [
    "facilities",
    "professions",
    "organizational_positions",
    "aegis_roles",
    "permissions",
    "role_permission_assignments",
    "users",
    "user_facility_assignments",
    "user_role_assignments",
    "professionals",
    "catalog_values",
    "login_history",
]


def upgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in _TABLES]
    Base.metadata.create_all(bind=bind, tables=tables)


def downgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in reversed(_TABLES)]
    Base.metadata.drop_all(bind=bind, tables=tables)
