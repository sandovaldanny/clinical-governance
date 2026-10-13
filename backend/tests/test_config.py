from app.core.config import Settings


def test_database_url_plain_postgresql_scheme_is_normalized_to_psycopg():
    s = Settings(database_url="postgresql://u:p@host/db?sslmode=require")
    assert s.database_url == "postgresql+psycopg://u:p@host/db?sslmode=require"


def test_database_url_postgres_short_scheme_is_normalized_to_psycopg():
    s = Settings(database_url="postgres://u:p@host/db")
    assert s.database_url == "postgresql+psycopg://u:p@host/db"


def test_database_url_already_psycopg_is_untouched():
    s = Settings(database_url="postgresql+psycopg://u:p@host/db")
    assert s.database_url == "postgresql+psycopg://u:p@host/db"


def test_default_jwt_secret_rejected_outside_local_env():
    import pytest

    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(env="production", jwt_secret="change-me")


def test_default_jwt_secret_allowed_in_local_env():
    assert Settings(env="local", jwt_secret="change-me").jwt_secret == "change-me"
