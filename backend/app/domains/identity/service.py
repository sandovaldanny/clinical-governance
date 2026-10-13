"""
Lógica de dominio de identidad. Resuelve permisos efectivos (roles -> permisos) y aplica las
reglas del funcional: cada usuario requiere al menos un centro y un rol; los permisos siempre se
otorgan por rol, nunca por excepción directa a la cuenta (sección 6.2 del funcional).
"""
from __future__ import annotations

import secrets
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import record_event
from app.core.master_data import apply_changes, create_audited, get_or_404, update_audited
from app.core.security import hash_password, verify_password
from app.domains.identity.models import (
    FACILITY_STATUSES,
    USER_STATUSES,
    AegisRole,
    CatalogValue,
    Facility,
    OrganizationalPosition,
    Permission,
    Profession,
    Professional,
    RolePermissionAssignment,
    User,
    UserFacilityAssignment,
    UserRoleAssignment,
)


_apply_changes = apply_changes


def authenticate(db: Session, *, identifier: str, password: str) -> User | None:
    """`identifier` es el correo completo o solo su parte local (`admin` ≡ `admin@<dominio>`);
    la parte local debe ser única entre usuarios activos para resolver."""
    ident = identifier.strip().lower()
    if "@" in ident:
        condition = func.lower(User.email) == ident
    else:
        condition = func.split_part(func.lower(User.email), "@", 1) == ident
    user = db.scalar(select(User).where(condition, User.is_active.is_(True)))
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


def _generate_temporary_password() -> str:
    """Contraseña temporal gestionada por el sistema (M01 doc: "Password — System managed";
    §6.3 arquitectura): se muestra una sola vez y se fuerza cambio en el primer acceso."""
    return secrets.token_urlsafe(9)


def _full_name(first_name: str | None, last_name: str | None) -> str:
    return " ".join(part for part in (first_name, last_name) if part).strip()


def _role_codes(db: Session, role_ids: list[uuid.UUID]) -> set[str]:
    if not role_ids:
        return set()
    return set(db.scalars(select(AegisRole.code).where(AegisRole.id.in_(role_ids))).all())


def _validate_user_rules(
    *, facility_ids: list[uuid.UUID] | None, role_ids: list[uuid.UUID] | None,
    role_codes: set[str], profession_id: uuid.UUID | None,
) -> None:
    """Reglas de negocio M01 §6: ≥1 centro, ≥1 rol, todo usuario clínico con profesión."""
    if facility_ids is not None and not facility_ids:
        raise ValueError("Todo usuario debe tener al menos un centro asignado.")
    if role_ids is not None and not role_ids:
        raise ValueError("Todo usuario debe tener al menos un rol asignado.")
    if "clinician" in role_codes and profession_id is None:
        raise ValueError("Todo usuario clínico debe tener una profesión asignada.")


def _replace_facilities(db: Session, user_id: uuid.UUID, facility_ids: list[uuid.UUID], is_corporate: bool) -> None:
    for row in db.scalars(select(UserFacilityAssignment).where(UserFacilityAssignment.user_id == user_id)).all():
        db.delete(row)
    for facility_id in facility_ids:
        db.add(UserFacilityAssignment(user_id=user_id, facility_id=facility_id, is_corporate_scope=is_corporate))


def _replace_roles(db: Session, user_id: uuid.UUID, role_ids: list[uuid.UUID]) -> None:
    for row in db.scalars(select(UserRoleAssignment).where(UserRoleAssignment.user_id == user_id)).all():
        db.delete(row)
    for role_id in role_ids:
        db.add(UserRoleAssignment(user_id=user_id, role_id=role_id))


def get_user_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise LookupError("Usuario no encontrado")
    return user


def user_to_dict(db: Session, user: User) -> dict:
    """UserOut para un usuario: nombres de cargo/profesión, especialidad del profesional
    vinculado y asignaciones de centros/roles (sin duplicar datos)."""
    facility_rows = db.execute(
        select(UserFacilityAssignment.facility_id, UserFacilityAssignment.is_corporate_scope).where(
            UserFacilityAssignment.user_id == user.id
        )
    ).all()
    role_ids = db.scalars(select(UserRoleAssignment.role_id).where(UserRoleAssignment.user_id == user.id)).all()
    position_name = (
        db.scalar(select(OrganizationalPosition.title).where(OrganizationalPosition.id == user.organizational_position_id))
        if user.organizational_position_id else None
    )
    profession_name = (
        db.scalar(select(Profession.name).where(Profession.id == user.profession_id)) if user.profession_id else None
    )
    specialty = db.scalar(select(Professional.specialty).where(Professional.user_id == user.id))
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "employee_number": user.employee_number,
        "mobile": user.mobile,
        "status": user.status or "active",
        "is_active": bool(user.is_active),
        "organizational_position_id": user.organizational_position_id,
        "position_name": position_name,
        "profession_id": user.profession_id,
        "profession_name": profession_name,
        "specialty": specialty,
        "facility_ids": [r[0] for r in facility_rows],
        "is_corporate_scope": any(r[1] for r in facility_rows),
        "role_ids": list(role_ids),
        "must_change_password": bool(user.must_change_password),
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
    }


def create_user(
    db: Session,
    *,
    actor_user_id: uuid.UUID,
    first_name: str,
    last_name: str,
    employee_number: str,
    email: str,
    mobile: str | None,
    organizational_position_id: uuid.UUID | None,
    profession_id: uuid.UUID | None,
    facility_ids: list[uuid.UUID],
    is_corporate_scope: bool,
    role_ids: list[uuid.UUID],
) -> tuple[User, str]:
    """Flujo M01: crear → cargo → centro → profesión → roles → activar. Devuelve (usuario,
    contraseña temporal en claro) — la contraseña solo existe en esta respuesta."""
    if db.scalar(select(User).where(User.email == email)):
        raise PermissionError("Ya existe un usuario con ese correo.")
    _validate_user_rules(
        facility_ids=facility_ids, role_ids=role_ids, role_codes=_role_codes(db, role_ids), profession_id=profession_id
    )

    temporary_password = _generate_temporary_password()
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        full_name=_full_name(first_name, last_name),
        employee_number=employee_number,
        mobile=mobile,
        organizational_position_id=organizational_position_id,
        profession_id=profession_id,
        hashed_password=hash_password(temporary_password),
        must_change_password=True,
        status="active",
        is_active=True,
        created_by_user_id=actor_user_id,
    )
    db.add(user)
    db.flush()
    _replace_facilities(db, user.id, facility_ids, is_corporate_scope)
    _replace_roles(db, user.id, role_ids)

    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="identity",
        entity_type="User",
        entity_id=str(user.id),
        action="create",
        new_values={
            "email": email,
            "full_name": user.full_name,
            "employee_number": employee_number,
            "facility_ids": [str(f) for f in facility_ids],
            "role_ids": [str(r) for r in role_ids],
        },
    )
    db.commit()
    db.refresh(user)
    return user, temporary_password


def update_user(db: Session, *, actor_user_id: uuid.UUID, user_id: uuid.UUID, data: dict) -> User:
    """Edición parcial. `facility_ids` / `role_ids` presentes reemplazan las asignaciones."""
    user = get_user_or_404(db, user_id)
    facility_ids = data.pop("facility_ids", None)
    is_corporate = data.pop("is_corporate_scope", None)
    role_ids = data.pop("role_ids", None)

    new_email = data.get("email")
    if new_email and new_email != user.email and db.scalar(select(User).where(User.email == new_email)):
        raise PermissionError("Ya existe un usuario con ese correo.")

    effective_profession = data.get("profession_id", user.profession_id)
    role_codes = _role_codes(db, role_ids) if role_ids is not None else set()
    _validate_user_rules(
        facility_ids=facility_ids, role_ids=role_ids, role_codes=role_codes, profession_id=effective_profession
    )

    previous, new = _apply_changes(user, data)
    if "first_name" in new or "last_name" in new:
        previous["full_name"] = user.full_name
        user.full_name = _full_name(user.first_name, user.last_name)
        new["full_name"] = user.full_name

    if facility_ids is not None or is_corporate is not None:
        current_rows = db.execute(
            select(UserFacilityAssignment.facility_id, UserFacilityAssignment.is_corporate_scope).where(
                UserFacilityAssignment.user_id == user.id
            )
        ).all()
        current_ids = [r[0] for r in current_rows]
        current_corp = any(r[1] for r in current_rows)
        target_ids = facility_ids if facility_ids is not None else current_ids
        target_corp = is_corporate if is_corporate is not None else current_corp
        _replace_facilities(db, user.id, target_ids, target_corp)
        previous["facility_ids"] = [str(f) for f in current_ids]
        new["facility_ids"] = [str(f) for f in target_ids]
        previous["is_corporate_scope"] = current_corp
        new["is_corporate_scope"] = target_corp
    if role_ids is not None:
        current_roles = db.scalars(select(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)).all()
        for row in current_roles:
            db.delete(row)
        for role_id in role_ids:
            db.add(UserRoleAssignment(user_id=user.id, role_id=role_id))
        previous["role_ids"] = [str(r.role_id) for r in current_roles]
        new["role_ids"] = [str(r) for r in role_ids]

    if new:
        record_event(
            db,
            actor_user_id=str(actor_user_id),
            module="identity",
            entity_type="User",
            entity_id=str(user.id),
            action="update",
            previous_values=previous,
            new_values=new,
        )
    db.commit()
    db.refresh(user)
    return user


def set_initial_password(db: Session, user: User, raw_password: str) -> None:
    user.hashed_password = hash_password(raw_password)
    db.commit()


# ---------------------------------------------------------------------------
# Datos maestros (M02): helpers genéricos crear/editar con auditoría
# ---------------------------------------------------------------------------


def _create_audited(db: Session, obj, *, actor_user_id: uuid.UUID, entity_type: str, new_values: dict):
    return create_audited(db, obj, actor_user_id=actor_user_id, module="identity", entity_type=entity_type, new_values=new_values)


def _update_audited(db: Session, obj, *, actor_user_id: uuid.UUID, entity_type: str, data: dict):
    return update_audited(db, obj, actor_user_id=actor_user_id, module="identity", entity_type=entity_type, data=data)


_get_or_404 = get_or_404


# ----- positions -----


def create_position(db: Session, *, actor_user_id: uuid.UUID, title: str, description: str) -> OrganizationalPosition:
    if db.scalar(select(OrganizationalPosition).where(OrganizationalPosition.title == title)):
        raise PermissionError("Ya existe un cargo con ese nombre.")
    obj = OrganizationalPosition(title=title, description=description, is_active=True)
    return _create_audited(
        db, obj, actor_user_id=actor_user_id, entity_type="OrganizationalPosition",
        new_values={"title": title, "description": description},
    )


def update_position(db: Session, *, actor_user_id: uuid.UUID, position_id: uuid.UUID, data: dict) -> OrganizationalPosition:
    obj = _get_or_404(db, OrganizationalPosition, position_id, "Cargo")
    return _update_audited(db, obj, actor_user_id=actor_user_id, entity_type="OrganizationalPosition", data=data)


# ----- facilities -----


def facility_to_dict(db: Session, facility: Facility) -> dict:
    director_name = (
        db.scalar(select(User.full_name).where(User.id == facility.clinical_director_user_id))
        if facility.clinical_director_user_id else None
    )
    return {
        "id": facility.id,
        "name": facility.name,
        "city": facility.city,
        "country": facility.country,
        "status": facility.status or "active",
        "is_active": bool(facility.is_active),
        "clinical_director_user_id": facility.clinical_director_user_id,
        "clinical_director_name": director_name,
    }


def list_facilities(db: Session) -> list[dict]:
    rows = db.execute(
        select(Facility, User.full_name)
        .outerjoin(User, Facility.clinical_director_user_id == User.id)
        .order_by(Facility.name)
    ).all()
    return [
        {
            "id": f.id, "name": f.name, "city": f.city, "country": f.country,
            "status": f.status or "active", "is_active": bool(f.is_active),
            "clinical_director_user_id": f.clinical_director_user_id, "clinical_director_name": director_name,
        }
        for f, director_name in rows
    ]


def _validate_director(db: Session, user_id: uuid.UUID | None) -> None:
    if user_id is None:
        return
    if not db.scalar(select(User).where(User.id == user_id)):
        raise ValueError("El director clínico indicado no existe.")


def create_facility(
    db: Session, *, actor_user_id: uuid.UUID, name: str, country: str, city: str,
    clinical_director_user_id: uuid.UUID | None,
) -> Facility:
    if db.scalar(select(Facility).where(Facility.name == name)):
        raise PermissionError("Ya existe un centro con ese nombre.")
    _validate_director(db, clinical_director_user_id)
    obj = Facility(
        name=name, country=country, city=city, clinical_director_user_id=clinical_director_user_id,
        status="active", is_active=True,
    )
    return _create_audited(
        db, obj, actor_user_id=actor_user_id, entity_type="Facility",
        new_values={"name": name, "country": country, "city": city,
                    "clinical_director_user_id": str(clinical_director_user_id) if clinical_director_user_id else None},
    )


def update_facility(db: Session, *, actor_user_id: uuid.UUID, facility_id: uuid.UUID, data: dict) -> Facility:
    obj = _get_or_404(db, Facility, facility_id, "Centro")
    if "clinical_director_user_id" in data:
        _validate_director(db, data["clinical_director_user_id"])
    status = data.get("status")
    if status is not None:
        if status not in FACILITY_STATUSES:
            raise ValueError(f"Estado inválido: {status}")
        data["is_active"] = status == "active"
    return _update_audited(db, obj, actor_user_id=actor_user_id, entity_type="Facility", data=data)


# ----- professions -----


def create_profession(db: Session, *, actor_user_id: uuid.UUID, name: str) -> Profession:
    if db.scalar(select(Profession).where(Profession.name == name)):
        raise PermissionError("Ya existe una profesión con ese nombre.")
    obj = Profession(name=name, is_active=True)
    return _create_audited(db, obj, actor_user_id=actor_user_id, entity_type="Profession", new_values={"name": name})


def update_profession(db: Session, *, actor_user_id: uuid.UUID, profession_id: uuid.UUID, data: dict) -> Profession:
    obj = _get_or_404(db, Profession, profession_id, "Profesión")
    return _update_audited(db, obj, actor_user_id=actor_user_id, entity_type="Profession", data=data)


# ----- catalog values -----


def create_catalog_value(db: Session, *, actor_user_id: uuid.UUID, catalog_type: str, code: str, label: str) -> CatalogValue:
    if db.scalar(select(CatalogValue).where(CatalogValue.catalog_type == catalog_type, CatalogValue.code == code)):
        raise PermissionError("Ya existe un valor con ese código en el catálogo.")
    obj = CatalogValue(catalog_type=catalog_type, code=code, label=label, is_active=True)
    return _create_audited(
        db, obj, actor_user_id=actor_user_id, entity_type="CatalogValue",
        new_values={"catalog_type": catalog_type, "code": code, "label": label},
    )


def update_catalog_value(db: Session, *, actor_user_id: uuid.UUID, value_id: uuid.UUID, data: dict) -> CatalogValue:
    obj = _get_or_404(db, CatalogValue, value_id, "Valor de catálogo")
    return _update_audited(db, obj, actor_user_id=actor_user_id, entity_type="CatalogValue", data=data)


def list_professions(db: Session) -> list[Profession]:
    return list(db.scalars(select(Profession).order_by(Profession.name)).all())


# ---------------------------------------------------------------------------
# Roles y matriz rol→permiso (M01 doc, tablas 5/6/8)
# ---------------------------------------------------------------------------

SYSTEM_ADMIN_CODE = "system_administrator"


def list_permissions_grouped(db: Session) -> list[dict]:
    """Permisos agrupados por módulo (prefijo del código), en orden estable."""
    groups: dict[str, list[Permission]] = {}
    for perm in db.scalars(select(Permission).order_by(Permission.module, Permission.code)).all():
        groups.setdefault(perm.module or perm.code.split(".")[0], []).append(perm)
    return [{"module": module, "permissions": perms} for module, perms in groups.items()]


def role_to_dict(db: Session, role: AegisRole) -> dict:
    user_ids = db.scalars(select(UserRoleAssignment.user_id).where(UserRoleAssignment.role_id == role.id)).all()
    permission_ids = db.scalars(
        select(RolePermissionAssignment.permission_id).where(RolePermissionAssignment.role_id == role.id)
    ).all()
    return {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description or "",
        "is_system_defined": bool(role.is_system_defined),
        "is_active": role.is_active if role.is_active is not None else True,
        "permission_ids": list(permission_ids),
        "user_count": len(set(user_ids)),
    }


def list_roles(db: Session) -> list[dict]:
    roles = db.scalars(select(AegisRole).order_by(AegisRole.name)).all()
    perms: dict[uuid.UUID, list[uuid.UUID]] = {}
    for role_id, permission_id in db.execute(
        select(RolePermissionAssignment.role_id, RolePermissionAssignment.permission_id)
    ).all():
        perms.setdefault(role_id, []).append(permission_id)
    users: dict[uuid.UUID, set[uuid.UUID]] = {}
    for role_id, user_id in db.execute(select(UserRoleAssignment.role_id, UserRoleAssignment.user_id)).all():
        users.setdefault(role_id, set()).add(user_id)
    return [
        {
            "id": r.id, "code": r.code, "name": r.name, "description": r.description or "",
            "is_system_defined": bool(r.is_system_defined),
            "is_active": r.is_active if r.is_active is not None else True,
            "permission_ids": perms.get(r.id, []), "user_count": len(users.get(r.id, set())),
        }
        for r in roles
    ]


def _validate_permission_ids(db: Session, permission_ids: list[uuid.UUID]) -> None:
    if not permission_ids:
        return
    valid = set(db.scalars(select(Permission.id).where(Permission.id.in_(permission_ids))).all())
    if set(permission_ids) - valid:
        raise ValueError("Uno o más permisos no existen.")


def create_role(
    db: Session, *, actor_user_id: uuid.UUID, code: str, name: str, description: str, permission_ids: list[uuid.UUID],
) -> AegisRole:
    _validate_permission_ids(db, permission_ids)
    if db.scalar(select(AegisRole).where(AegisRole.code == code)):
        raise PermissionError("Ya existe un rol con ese código.")
    role = AegisRole(code=code, name=name, description=description, is_system_defined=False, is_active=True)
    db.add(role)
    db.flush()
    for permission_id in permission_ids:
        db.add(RolePermissionAssignment(role_id=role.id, permission_id=permission_id))
    record_event(
        db, actor_user_id=str(actor_user_id), module="identity", entity_type="AegisRole", entity_id=str(role.id),
        action="create", new_values={"code": code, "name": name, "permission_ids": [str(p) for p in permission_ids]},
    )
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, *, actor_user_id: uuid.UUID, role_id: uuid.UUID, data: dict) -> AegisRole:
    """Edita nombre/descripción/estado y, si viene `permission_ids`, reemplaza la matriz del rol —
    el cambio aplica a todos los usuarios con ese rol (M01 doc, tabla 8)."""
    role = _get_or_404(db, AegisRole, role_id, "Rol")
    permission_ids = data.pop("permission_ids", None)

    if role.code == SYSTEM_ADMIN_CODE:
        if permission_ids is not None:
            raise PermissionError("System Administrator conserva siempre todos los permisos; su matriz no se edita.")
        if data.get("is_active") is False:
            raise PermissionError("System Administrator no puede desactivarse.")

    previous: dict = {}
    new: dict = {}
    if permission_ids is not None:
        _validate_permission_ids(db, permission_ids)
        current = db.scalars(select(RolePermissionAssignment).where(RolePermissionAssignment.role_id == role.id)).all()
        current_ids = {row.permission_id for row in current}
        target_ids = set(permission_ids)
        for row in current:
            if row.permission_id not in target_ids:
                db.delete(row)
        for permission_id in target_ids - current_ids:
            db.add(RolePermissionAssignment(role_id=role.id, permission_id=permission_id))
        if current_ids != target_ids:
            previous["permission_ids"] = sorted(str(p) for p in current_ids)
            new["permission_ids"] = sorted(str(p) for p in target_ids)

    if data.get("is_active") is False:
        assigned = db.scalars(select(UserRoleAssignment.user_id).where(UserRoleAssignment.role_id == role.id)).all()
        if assigned:
            raise PermissionError(
                f"El rol tiene {len(set(assigned))} usuario(s) asignado(s). Reasigne o retire el rol antes de desactivarlo."
            )

    prev_fields, new_fields = _apply_changes(role, data)
    previous.update(prev_fields)
    new.update(new_fields)
    if new:
        record_event(
            db, actor_user_id=str(actor_user_id), module="identity", entity_type="AegisRole", entity_id=str(role.id),
            action="update", previous_values=previous, new_values=new,
        )
    db.commit()
    db.refresh(role)
    return role


def list_users(db: Session) -> list[dict]:
    """Registro de usuarios (M01 §9 "User Register") con cargo, profesión, especialidad y
    asignaciones. Tres consultas en total, sin N+1."""
    rows = db.execute(
        select(User, OrganizationalPosition.title, Profession.name, Professional.specialty)
        .outerjoin(OrganizationalPosition, User.organizational_position_id == OrganizationalPosition.id)
        .outerjoin(Profession, User.profession_id == Profession.id)
        .outerjoin(Professional, Professional.user_id == User.id)
        .order_by(User.full_name)
    ).all()
    facilities: dict[uuid.UUID, list] = {}
    for user_id, facility_id, corp in db.execute(
        select(UserFacilityAssignment.user_id, UserFacilityAssignment.facility_id, UserFacilityAssignment.is_corporate_scope)
    ).all():
        facilities.setdefault(user_id, []).append((facility_id, corp))
    roles: dict[uuid.UUID, list] = {}
    for user_id, role_id in db.execute(select(UserRoleAssignment.user_id, UserRoleAssignment.role_id)).all():
        roles.setdefault(user_id, []).append(role_id)

    result = []
    for user, position_name, profession_name, specialty in rows:
        f = facilities.get(user.id, [])
        result.append(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "employee_number": user.employee_number,
                "mobile": user.mobile,
                "status": user.status or "active",
                "is_active": bool(user.is_active),
                "organizational_position_id": user.organizational_position_id,
                "position_name": position_name,
                "profession_id": user.profession_id,
                "profession_name": profession_name,
                "specialty": specialty,
                "facility_ids": [x[0] for x in f],
                "is_corporate_scope": any(x[1] for x in f),
                "role_ids": roles.get(user.id, []),
                "must_change_password": bool(user.must_change_password),
                "last_login_at": user.last_login_at,
                "created_at": user.created_at,
            }
        )
    return result


def set_user_status(db: Session, *, actor_user_id: uuid.UUID, user_id: uuid.UUID, status: str) -> User:
    """Activa / inactiva / suspende una cuenta. Nunca se borra (regla global #2: autoría
    histórica). Un usuario no puede quitarse a sí mismo el estado activo."""
    if status not in USER_STATUSES:
        raise ValueError(f"Estado inválido: {status}")
    user = get_user_or_404(db, user_id)
    if user.id == actor_user_id and status != "active":
        raise PermissionError("No puede desactivar ni suspender su propia cuenta.")
    if user.status == status:
        return user

    previous = user.status
    user.status = status
    user.is_active = status == "active"
    record_event(
        db,
        actor_user_id=str(actor_user_id),
        module="identity",
        entity_type="User",
        entity_id=str(user.id),
        action="activate" if status == "active" else status,
        previous_values={"status": previous},
        new_values={"status": status},
    )
    db.commit()
    db.refresh(user)
    return user


def list_positions(db: Session) -> list[OrganizationalPosition]:
    return list(db.scalars(select(OrganizationalPosition).order_by(OrganizationalPosition.title)).all())


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


def get_profile(db: Session, *, user_id: uuid.UUID) -> dict:
    """Nombre, roles y centros del usuario para el menú de perfil. Tolera que no exista fila
    (usuario dev del bypass local): devuelve listas vacías y nombre None."""
    user = db.scalar(select(User).where(User.id == user_id))
    role_names = db.scalars(
        select(AegisRole.name)
        .join(UserRoleAssignment, UserRoleAssignment.role_id == AegisRole.id)
        .where(UserRoleAssignment.user_id == user_id)
        .order_by(AegisRole.name)
    ).all()
    facility_names = db.scalars(
        select(Facility.name)
        .join(UserFacilityAssignment, UserFacilityAssignment.facility_id == Facility.id)
        .where(UserFacilityAssignment.user_id == user_id)
        .order_by(Facility.name)
    ).all()
    return {
        "full_name": user.full_name if user else None,
        "email": user.email if user else None,
        "roles": list(role_names),
        "facilities": list(facility_names),
    }
