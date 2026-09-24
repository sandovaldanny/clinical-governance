"""
Dependencias comunes de FastAPI: sesión de base de datos con contexto de tenant ya fijado,
y resolución del usuario autenticado a partir del JWT.
"""
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db, set_tenant_context
from app.core.security import decode_access_token
from app.domains.identity import service as identity_service
from app.domains.identity.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/identity/auth/login", auto_error=False)

_BASE_DEV_PERMISSIONS = {
    "users.manage",
    "ucca.create",
    "ucca.approve",
    "corrective_actions.manage",
    "audit.read",
}


@dataclass
class CurrentUser:
    id: str
    email: str
    facility_ids: list[str]
    is_corporate: bool
    effective_permissions: set[str]


def _dev_bypass_user(db: Session) -> CurrentUser:
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == settings.seed_admin_email))
    if user:
        facility_ids, is_corporate = identity_service.resolve_facility_scope(db, user.id)
        permissions = identity_service.resolve_effective_permissions(db, user.id)
        return CurrentUser(
            id=str(user.id),
            email=user.email,
            facility_ids=facility_ids,
            is_corporate=is_corporate,
            effective_permissions=permissions,
        )
    return CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        email="dev@local",
        facility_ids=[],
        is_corporate=True,
        effective_permissions=_BASE_DEV_PERMISSIONS,
    )


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    settings = get_settings()
    if settings.auth_disabled:
        user = _dev_bypass_user(db)
        set_tenant_context(
            db, user_id=user.id, facility_ids=user.facility_ids, is_corporate=user.is_corporate
        )
        return user

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas o expiradas"
        )

    try:
        payload = decode_access_token(token)
    except Exception as exc:  # noqa: BLE001 — cualquier fallo de JWT es 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas o expiradas"
        ) from exc

    user = CurrentUser(
        id=payload["sub"],
        email=payload.get("email", ""),
        facility_ids=payload.get("facility_ids", []),
        is_corporate=payload.get("is_corporate", False),
        effective_permissions=set(payload.get("permissions", [])),
    )

    set_tenant_context(
        db, user_id=user.id, facility_ids=user.facility_ids, is_corporate=user.is_corporate
    )
    return user
