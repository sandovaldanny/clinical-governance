"""
Entidades maestras (M01 + M02): la fuente única de verdad que consumen TODOS los módulos.
Ningún módulo de negocio debe redefinir Users, Facilities, Professions o Professionals — se
referencian por clave foránea (principio "registrar una vez, usar en todas partes").
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


USER_STATUSES = ("active", "inactive", "suspended")
FACILITY_STATUSES = ("active", "closed")


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    # Director clínico responsable (M01 doc, tabla Facilities: "Clinical Director — User Lookup").
    clinical_director_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | closed
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # derivado de status


class Profession(Base):
    __tablename__ = "professions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class OrganizationalPosition(Base):
    __tablename__ = "organizational_positions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(300), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AegisRole(Base):
    """Rol funcional configurable (System Administrator, Governance Lead, Clinician, ...).
    Los permisos NUNCA se asignan directamente a un usuario; siempre a través de un rol."""

    __tablename__ = "aegis_roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(300), default="")
    is_system_defined: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Permission(Base):
    """Convención de código: "<modulo>.<accion>", ej. "ucca.approve"."""

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    module: Mapped[str] = mapped_column(String(50), default="")  # prefijo del código, ej. "ucca"
    name: Mapped[str] = mapped_column(String(150), default="")
    description: Mapped[str] = mapped_column(String(300), default="")


class RolePermissionAssignment(Base):
    __tablename__ = "role_permission_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("aegis_roles.id"), nullable=False)
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permissions.id"), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)  # calculado: first + last
    employee_number: Mapped[str | None] = mapped_column(String(50))
    mobile: Mapped[str | None] = mapped_column(String(40))

    # Desacopla identidad de mecanismo de autenticación: activar SSO con Entra ID no requiere
    # migrar usuarios existentes, solo crear un nuevo auth_provider.
    auth_provider: Mapped[str] = mapped_column(String(30), default="local")
    external_id: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str | None] = mapped_column(String(255))

    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | inactive | suspended
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # derivado: status == "active"

    profession_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("professions.id"))
    organizational_position_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_positions.id")
    )

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    last_login_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(default=0)


class UserFacilityAssignment(Base):
    """Un usuario puede tener uno o varios centros (regla del funcional, sección 6.3/12)."""

    __tablename__ = "user_facility_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    is_corporate_scope: Mapped[bool] = mapped_column(Boolean, default=False)


class UserRoleAssignment(Base):
    """Un usuario puede tener varios roles (regla del funcional, sección 6.3)."""

    __tablename__ = "user_role_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("aegis_roles.id"), nullable=False)
    assigned_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Professional(Base):
    """Registro único de profesionales clínicos (M02), separado de User: no todo profesional
    tiene necesariamente acceso a AEGIS, pero todo profesional con acceso se vincula a un User."""

    __tablename__ = "professionals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    employee_number: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    profession_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("professions.id"), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(150))
    primary_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    # Alcance de práctica: usado por el motor de reglas para preclasificar "No aplica"
    # en criterios UCCA/JAWDA (regla crítica de la sección M02 del funcional).
    scope_of_practice: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CatalogValue(Base):
    """Catálogo genérico configurable (estados, severidades, categorías, ...). Activable /
    desactivable sin borrar historial, per principio 9 del funcional."""

    __tablename__ = "catalog_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    catalog_type: Mapped[str] = mapped_column(String(80), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LoginHistory(Base):
    __tablename__ = "login_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    occurred_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    was_successful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64))
