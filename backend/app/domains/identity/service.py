"""
Lógica de dominio de identidad. Resuelve permisos efectivos (roles -> permisos) y aplica las
reglas del funcional: cada usuario requiere al menos un centro y un rol; los permisos siempre se
otorgan por rol, nunca por excepción directa a la cuenta (sección 6.2 del funcional).
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import record_event
from app.core.security import hash_password, verify_password
from app.domains.identity.models import (
    AegisRole,
    CatalogValue,
    Facility,
    Permission,
    Profession,
    Professional,
    RolePermissionAssignment,
    User,
    UserFacilityAssignment,
    UserRoleAssignment,
)


def authenticate(db: Session, *, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def resolve_effective_permissions(db: Session, user_id: uuid.UUID) -> set[str]:
    role_ids = db.scalars(
        select(UserRoleAssignment.role_id).where(UserRoleAssignment.user_id == user_id)
    ).all()
    if not role_ids:
        return set()
    permission_ids = db.scalars(
        select(RolePermissionAssignment.permission_id).where(
            RolePermissionAssignment.role_id.in_(role_ids)
        )
    ).all()
    if not permission_ids:
        return set()
    codes = db.scalars(select(Permission.code).where(Permission.id.in_(permission_ids))).all()
    return set(codes)


def resolve_facility_scope(db: Session, user_id: uuid.UUID) -> tuple[list[str], bool]:
    rows = db.execute(
        select(UserFacilityAssignment.facility_id, UserFacilityAssignment.is_corporate_scope).where(
            UserFacilityAssignment.user_id == user_id
        )
    ).all()
    facility_ids = [str(r[0]) for r in rows]
    is_corporate = any(r[1] for r in rows)
    return facility_ids, is_corporate


def create_user(
    db: Session,
    *,
    actor_user_id: uuid.UUID,
    email: str,
    full_name: str,
    employee_number: str | None,
    profession_id: uuid.UUID | None,
    facility_ids: list[uuid.UUID],
    role_ids: list[uuid.UUID],
) -> User:
    """Regla del funcional (sección 6.1/12): todo usuario debe tener al menos un centro y un rol."""
    if not facility_ids:
        raise ValueError("Todo usuario debe tener al menos un centro asignado.")
    if not role_ids:
        raise ValueError("Todo usuario debe tener al menos un rol asignado.")

    user = User(
        email=email,
        full_name=full_name,
        employee_number=employee_number,
        profession_id=profession_id,
        must_change_password=True,
        is_active=True,
    )
    db.add(user)
    db.flush()

    for facility_id in facility_ids:
        db.add(UserFacilityAssignment(user_id=user.id, facility_id=facility_id))
    for role_id in role_ids:
        db.add(UserRoleAssignment(user_id=user.id, role_id=role_id))

    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="identity",
        entity_type="User",
        entity_id=str(user.id),
        action="create",
        new_values={"email": email, "full_name": full_name},
    )
    db.commit()
    db.refresh(user)
    return user


def set_initial_password(db: Session, user: User, raw_password: str) -> None:
    user.hashed_password = hash_password(raw_password)
    db.commit()


def list_facilities(db: Session) -> list[Facility]:
    return list(db.scalars(select(Facility).order_by(Facility.name)).all())


def list_professions(db: Session) -> list[Profession]:
    return list(db.scalars(select(Profession).order_by(Profession.name)).all())


def list_roles(db: Session) -> list[AegisRole]:
    return list(db.scalars(select(AegisRole).order_by(AegisRole.name)).all())


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)).all())


def list_professionals(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Professional,
            Profession.name.label("profession_name"),
        )
        .join(Profession, Professional.profession_id == Profession.id)
        .order_by(Professional.full_name)
    ).all()
    return [
        {
            "id": pro.id,
            "employee_number": pro.employee_number,
            "full_name": pro.full_name,
            "specialty": pro.specialty,
            "profession_id": pro.profession_id,
            "profession_name": profession_name,
            "primary_facility_id": pro.primary_facility_id,
            "is_active": pro.is_active,
        }
        for pro, profession_name in rows
    ]


def list_catalog_values(db: Session, *, catalog_type: str | None = None) -> list[CatalogValue]:
    stmt = select(CatalogValue).order_by(CatalogValue.catalog_type, CatalogValue.label)
    if catalog_type:
        stmt = stmt.where(CatalogValue.catalog_type == catalog_type)
    return list(db.scalars(stmt).all())
