"""
Hash de contraseñas y emisión/validación de JWT.

Fase 1 del requerimiento: usuario y contraseña propios. La tabla Users ya incluye
`auth_provider` / `external_id` (ver domains/identity/models.py) para que activar SSO con
Microsoft Entra ID (fase posterior) sea agregar un proveedor nuevo, no migrar datos.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def create_access_token(*, subject: str, extra_claims: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire, **extra_claims}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
