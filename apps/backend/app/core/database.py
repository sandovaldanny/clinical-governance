"""
Sesión de base de datos + soporte de Row-Level Security multi-centro.

Decisión de arquitectura (sección 5.2 del documento técnico): la segregación por centro NO se
implementa filtrando en cada query de cada módulo. Se implementa con políticas RLS de PostgreSQL
que leen una variable de sesión (`app.current_facility_ids` y `app.current_user_id`), fijada por
`set_tenant_context()` al inicio de cada request autenticado. Así, aunque un desarrollador de un
módulo nuevo olvide filtrar por centro, la base de datos igual bloquea el acceso cruzado.
"""
from collections.abc import Generator
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def set_tenant_context(db: Session, *, user_id: str, facility_ids: list[str], is_corporate: bool) -> None:
    """Fija el contexto que consumen las políticas RLS definidas en las migraciones."""
    # PostgreSQL no acepta bind params en SET LOCAL; validamos UUIDs antes de interpolar.
    uuid.UUID(user_id)
    safe_fids = ",".join(str(uuid.UUID(fid)) for fid in facility_ids)
    corp = "true" if is_corporate else "false"
    db.execute(text(f"SET LOCAL app.current_user_id = '{user_id}'"))
    db.execute(text(f"SET LOCAL app.current_facility_ids = '{safe_fids}'"))
    db.execute(text(f"SET LOCAL app.current_is_corporate = '{corp}'"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
