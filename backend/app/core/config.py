"""
Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca con os.environ
disperso por los módulos — así el arquetipo cumple el principio "configuración sobre código"
para lo que sí es configuración de infraestructura (no de negocio; eso vive en la base de datos).
"""
from functools import lru_cache
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://aegis:aegis@localhost:5432/aegis"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60
    env: str = "local"
    auth_disabled: bool = False

    seed_admin_email: str = "admin@alkalma.local"
    # Demo: acceso `admin` / `admin` sin cambio forzado (decisión del equipo para el mockup público).
    seed_admin_temp_password: str = "admin"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Proveedores gestionados (Neon, Vercel) entregan `postgres://` o `postgresql://`;
        SQLAlchemy necesita el driver explícito `postgresql+psycopg://`."""
        for prefix in ("postgresql://", "postgres://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix):]
        return value

    @model_validator(mode="after")
    def _reject_default_secret_outside_local(self) -> "Settings":
        if self.env != "local" and self.jwt_secret == "change-me":
            raise ValueError("JWT_SECRET must be set to a real secret when ENV is not 'local'")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
