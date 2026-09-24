from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserStatus = Literal["active", "inactive", "suspended"]
FacilityStatus = Literal["active", "closed"]


# ---------- auth ----------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool


class CurrentUserOut(BaseModel):
    """Perfil del usuario autenticado para el encabezado/menú de perfil del frontend."""

    id: str
    email: str
    full_name: str
    roles: list[str]
    facilities: list[str]
    is_corporate: bool
    permissions: list[str]


# ---------- users (M01) ----------


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    full_name: str
    employee_number: str | None = None
    mobile: str | None = None
    status: UserStatus = "active"
    is_active: bool
    organizational_position_id: uuid.UUID | None = None
    position_name: str | None = None
    profession_id: uuid.UUID | None = None
    profession_name: str | None = None
    specialty: str | None = None
    facility_ids: list[uuid.UUID] = Field(default_factory=list)
    is_corporate_scope: bool = False
    role_ids: list[uuid.UUID] = Field(default_factory=list)
    must_change_password: bool = False
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Flujo del documento M01: identidad → cargo → centro(s) → profesión → rol(es)."""

    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    employee_number: str = Field(min_length=1, max_length=50)
    email: EmailStr
    mobile: str | None = Field(default=None, max_length=40)
    organizational_position_id: uuid.UUID | None = None
    profession_id: uuid.UUID | None = None
    facility_ids: list[uuid.UUID] = Field(min_length=1)
    is_corporate_scope: bool = False
    role_ids: list[uuid.UUID] = Field(min_length=1)


class UserUpdateRequest(BaseModel):
    """Edición parcial. Listas presentes reemplazan las asignaciones actuales."""

    first_name: str | None = Field(default=None, min_length=1, max_length=120)
    last_name: str | None = Field(default=None, min_length=1, max_length=120)
    employee_number: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    mobile: str | None = Field(default=None, max_length=40)
    organizational_position_id: uuid.UUID | None = None
    profession_id: uuid.UUID | None = None
    facility_ids: list[uuid.UUID] | None = Field(default=None, min_length=1)
    is_corporate_scope: bool | None = None
    role_ids: list[uuid.UUID] | None = Field(default=None, min_length=1)


class UserCreatedOut(BaseModel):
    user: UserOut
    temporary_password: str


class UserStatusUpdateRequest(BaseModel):
    status: UserStatus


# ---------- master data (M02) ----------


class PositionOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str = ""
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class FacilityOut(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    country: str
    status: FacilityStatus = "active"
    is_active: bool
    clinical_director_user_id: uuid.UUID | None = None
    clinical_director_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfessionOut(BaseModel):
    id: uuid.UUID
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RoleOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str = ""
    is_system_defined: bool
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ProfessionalOut(BaseModel):
    id: uuid.UUID
    employee_number: str
    full_name: str
    specialty: str | None
    profession_id: uuid.UUID
    profession_name: str
    primary_facility_id: uuid.UUID
    is_active: bool


class CatalogValueOut(BaseModel):
    id: uuid.UUID
    catalog_type: str
    code: str
    label: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
