from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
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
    return [schemas.FacilityOut.model_validate(row) for row in service.list_facilities(db)]


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
    return [schemas.RoleOut.model_validate(row) for row in service.list_roles(db)]


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.UserOut]:
    return [schemas.UserOut.model_validate(row) for row in service.list_users(db)]


@router.patch("/users/{user_id}/status", response_model=schemas.UserOut)
def set_user_status(
    user_id: uuid.UUID,
    payload: schemas.UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.manage")),
) -> schemas.UserOut:
    try:
        user = service.set_user_status(
            db, actor_user_id=uuid.UUID(current_user.id), user_id=user_id, status=payload.status
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return schemas.UserOut.model_validate(service.user_to_dict(db, user))


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


@router.get("/positions", response_model=list[schemas.PositionOut])
def list_positions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.PositionOut]:
    return service.list_positions(db)


@router.post("/users", response_model=schemas.UserCreatedOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: schemas.UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.manage")),
) -> schemas.UserCreatedOut:
    try:
        user, temporary_password = service.create_user(
            db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump()
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Referencia inválida (cargo, centro, profesión o rol) o correo duplicado."
        ) from exc
    return schemas.UserCreatedOut(
        user=schemas.UserOut.model_validate(service.user_to_dict(db, user)), temporary_password=temporary_password
    )


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: schemas.UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.manage")),
) -> schemas.UserOut:
    try:
        user = service.update_user(
            db, actor_user_id=uuid.UUID(current_user.id), user_id=user_id, data=payload.model_dump(exclude_unset=True)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referencia inválida o correo duplicado.") from exc
    return schemas.UserOut.model_validate(service.user_to_dict(db, user))


# ---------------------------------------------------------------------------
# Datos maestros (M02): crear / editar / estado. Errores de dominio → HTTP.
# ---------------------------------------------------------------------------


def _domain_errors(fn):
    """Envuelve la llamada al servicio traduciendo excepciones de dominio a HTTP."""
    try:
        return fn()
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/positions", response_model=schemas.PositionOut, status_code=status.HTTP_201_CREATED)
def create_position(
    payload: schemas.PositionCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.PositionOut:
    return _domain_errors(lambda: service.create_position(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump()))


@router.patch("/positions/{position_id}", response_model=schemas.PositionOut)
def update_position(
    position_id: uuid.UUID,
    payload: schemas.PositionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.PositionOut:
    return _domain_errors(
        lambda: service.update_position(
            db, actor_user_id=uuid.UUID(current_user.id), position_id=position_id, data=payload.model_dump(exclude_unset=True)
        )
    )


@router.post("/facilities", response_model=schemas.FacilityOut, status_code=status.HTTP_201_CREATED)
def create_facility(
    payload: schemas.FacilityCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("facilities.manage")),
) -> schemas.FacilityOut:
    facility = _domain_errors(
        lambda: service.create_facility(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump())
    )
    return schemas.FacilityOut.model_validate(service.facility_to_dict(db, facility))


@router.patch("/facilities/{facility_id}", response_model=schemas.FacilityOut)
def update_facility(
    facility_id: uuid.UUID,
    payload: schemas.FacilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("facilities.manage")),
) -> schemas.FacilityOut:
    facility = _domain_errors(
        lambda: service.update_facility(
            db, actor_user_id=uuid.UUID(current_user.id), facility_id=facility_id, data=payload.model_dump(exclude_unset=True)
        )
    )
    return schemas.FacilityOut.model_validate(service.facility_to_dict(db, facility))


@router.post("/professions", response_model=schemas.ProfessionOut, status_code=status.HTTP_201_CREATED)
def create_profession(
    payload: schemas.ProfessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.ProfessionOut:
    return _domain_errors(lambda: service.create_profession(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump()))


@router.patch("/professions/{profession_id}", response_model=schemas.ProfessionOut)
def update_profession(
    profession_id: uuid.UUID,
    payload: schemas.ProfessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.ProfessionOut:
    return _domain_errors(
        lambda: service.update_profession(
            db, actor_user_id=uuid.UUID(current_user.id), profession_id=profession_id, data=payload.model_dump(exclude_unset=True)
        )
    )


@router.post("/catalogs", response_model=schemas.CatalogValueOut, status_code=status.HTTP_201_CREATED)
def create_catalog_value(
    payload: schemas.CatalogValueCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.CatalogValueOut:
    return _domain_errors(lambda: service.create_catalog_value(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump()))


@router.patch("/catalogs/{value_id}", response_model=schemas.CatalogValueOut)
def update_catalog_value(
    value_id: uuid.UUID,
    payload: schemas.CatalogValueUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("catalogs.manage")),
) -> schemas.CatalogValueOut:
    return _domain_errors(
        lambda: service.update_catalog_value(
            db, actor_user_id=uuid.UUID(current_user.id), value_id=value_id, data=payload.model_dump(exclude_unset=True)
        )
    )


# ---------------------------------------------------------------------------
# Roles y permisos (M01 doc, tablas 5/6/8)
# ---------------------------------------------------------------------------


@router.get("/permissions", response_model=list[schemas.PermissionGroupOut])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("users.view")),
) -> list[schemas.PermissionGroupOut]:
    return [schemas.PermissionGroupOut.model_validate(g) for g in service.list_permissions_grouped(db)]


@router.post("/roles", response_model=schemas.RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: schemas.RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles.manage")),
) -> schemas.RoleOut:
    role = _domain_errors(lambda: service.create_role(db, actor_user_id=uuid.UUID(current_user.id), **payload.model_dump()))
    return schemas.RoleOut.model_validate(service.role_to_dict(db, role))


@router.patch("/roles/{role_id}", response_model=schemas.RoleOut)
def update_role(
    role_id: uuid.UUID,
    payload: schemas.RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles.manage")),
) -> schemas.RoleOut:
    role = _domain_errors(
        lambda: service.update_role(
            db, actor_user_id=uuid.UUID(current_user.id), role_id=role_id, data=payload.model_dump(exclude_unset=True)
        )
    )
    return schemas.RoleOut.model_validate(service.role_to_dict(db, role))
