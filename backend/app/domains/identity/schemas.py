from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    employee_number: str | None = None
    profession_id: uuid.UUID | None = None
    facility_ids: list[uuid.UUID]
    role_ids: list[uuid.UUID]


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True


class FacilityOut(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    country: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfessionOut(BaseModel):
    id: uuid.UUID
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    is_system_defined: bool

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
