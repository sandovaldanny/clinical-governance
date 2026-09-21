"""
Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca con os.environ
disperso por los módulos — así el arquetipo cumple el principio "configuración sobre código"
para lo que sí es configuración de infraestructura (no de negocio; eso vive en la base de datos).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://aegis:aegis@localhost:5432/aegis"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60
    env: str = "local"
    auth_disabled: bool = False

    seed_admin_email: str = "admin@alkalma.local"
    seed_admin_temp_password: str = "ChangeMeOnFirstLogin!23"


@lru_cache
def get_settings() -> Settings:
    return Settings()
