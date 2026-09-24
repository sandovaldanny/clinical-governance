from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser, get_current_user
from app.core.rbac import require_permission
from app.core.security import create_access_token
from app.domains.identity import schemas, service

router = APIRouter(prefix="/identity", tags=["identity"])


@router.post("/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    user = service.authenticate(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    facility_ids, is_corporate = service.resolve_facility_scope(db, user.id)
    permissions = service.resolve_effective_permissions(db, user.id)

    token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "facility_ids": facility_ids,
            "is_corporate": is_corporate,
            "permissions": sorted(permissions),
        },
    )
    return schemas.TokenResponse(access_token=token, must_change_password=user.must_change_password)


@router.get("/me", response_model=schemas.CurrentUserOut)
def me(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> schemas.CurrentUserOut:
    """Perfil del usuario autenticado. Solo requiere sesión válida, no un permiso específico."""
    profile = service.get_profile(db, user_id=uuid.UUID(current_user.id))
    email = profile["email"] or current_user.email
    return schemas.CurrentUserOut(
        id=current_user.id,
        email=email,
        full_name=profile["full_name"] or email,
        roles=profile["roles"],
        facilities=profile["facilities"],
        is_corporate=current_user.is_corporate,
        permissions=sorted(current_user.effective_permissions),
    )


@router.get("/facilities", response_model=list[schemas.FacilityOut])
def list_facilities(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.FacilityOut]:
    return service.list_facilities(db)


@router.get("/professions", response_model=list[schemas.ProfessionOut])
def list_professions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.ProfessionOut]:
    return service.list_professions(db)


@router.get("/roles", response_model=list[schemas.RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.RoleOut]:
    return service.list_roles(db)


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.UserOut]:
    return service.list_users(db)


@router.get("/professionals", response_model=list[schemas.ProfessionalOut])
def list_professionals(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.ProfessionalOut]:
    return [schemas.ProfessionalOut.model_validate(row) for row in service.list_professionals(db)]


@router.get("/catalogs", response_model=list[schemas.CatalogValueOut])
def list_catalogs(
    catalog_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.CatalogValueOut]:
    return service.list_catalog_values(db, catalog_type=catalog_type)


@router.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: schemas.UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.manage")),
) -> schemas.UserOut:
    try:
        user = service.create_user(
            db,
            actor_user_id=uuid.UUID(current_user.id),
            email=payload.email,
            full_name=payload.full_name,
            employee_number=payload.employee_number,
            profession_id=payload.profession_id,
            facility_ids=payload.facility_ids,
            role_ids=payload.role_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return user
