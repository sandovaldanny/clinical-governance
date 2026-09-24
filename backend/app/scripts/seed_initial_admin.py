"""
Provisiona el usuario System Administrator inicial (sección 6.2/6.3 del funcional y sección
6.3 de la arquitectura técnica): permisos completos otorgados por ROL, no por excepción a la
cuenta; obligado a cambiar contraseña en el primer acceso; credenciales fuera del código.

Uso: docker compose exec backend python -m app.scripts.seed_initial_admin
"""
from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domains.identity.models import (
    AegisRole,
    Facility,
    Permission,
    RolePermissionAssignment,
    User,
    UserFacilityAssignment,
    UserRoleAssignment,
)

# Catálogo mínimo de permisos del arquetipo. Cada módulo nuevo agrega los suyos aquí o, en un
# sistema real, mediante su propia migración de datos — nunca hardcodeados en el backend.
_BASE_PERMISSIONS = [
    "users.manage",
    "ucca.create",
    "ucca.approve",
    "corrective_actions.manage",
    "audit.read",
]


def run() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        admin_role = db.scalar(select(AegisRole).where(AegisRole.code == "system_administrator"))
        if not admin_role:
            admin_role = AegisRole(
                code="system_administrator", name="System Administrator", is_system_defined=True
            )
            db.add(admin_role)
            db.flush()

        for code in _BASE_PERMISSIONS:
            permission = db.scalar(select(Permission).where(Permission.code == code))
            if not permission:
                permission = Permission(code=code, description=code)
                db.add(permission)
                db.flush()
            exists = db.scalar(
                select(RolePermissionAssignment).where(
                    RolePermissionAssignment.role_id == admin_role.id,
                    RolePermissionAssignment.permission_id == permission.id,
                )
            )
            if not exists:
                db.add(
                    RolePermissionAssignment(role_id=admin_role.id, permission_id=permission.id)
                )

        corporate_facility = db.scalar(select(Facility).limit(1))
        if not corporate_facility:
            corporate_facility = Facility(name="Al Bateen", city="Abu Dhabi", country="UAE")
            db.add(corporate_facility)
            db.flush()

        existing_admin = db.scalar(select(User).where(User.email == settings.seed_admin_email))
        if existing_admin:
            print(f"El administrador inicial ya existe: {settings.seed_admin_email}")
            return

        admin_user = User(
            email=settings.seed_admin_email,
            full_name="System Administrator",
            hashed_password=hash_password(settings.seed_admin_temp_password),
            must_change_password=True,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

        db.add(
            UserFacilityAssignment(
                user_id=admin_user.id, facility_id=corporate_facility.id, is_corporate_scope=True
            )
        )
        db.add(UserRoleAssignment(user_id=admin_user.id, role_id=admin_role.id))

        db.commit()
        print(f"Administrador inicial creado: {settings.seed_admin_email}")
        print("Contraseña temporal — cámbiela de inmediato y elimínela de cualquier registro:")
        print(f"  {settings.seed_admin_temp_password}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
