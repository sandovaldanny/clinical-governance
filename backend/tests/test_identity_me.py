"""
GET /identity/me devuelve el perfil del usuario autenticado (nombre, correo, roles, centros,
permisos efectivos) para el menú de perfil del frontend. Sin Postgres: sesión doble.
"""
import pytest
from fastapi.testclient import TestClient


class _EmptyScalars:
    def all(self):
        return []


class _FakeSession:
    def scalar(self, *_args, **_kwargs):
        return None

    def scalars(self, *_args, **_kwargs):
        return _EmptyScalars()

    def execute(self, *_args, **_kwargs):
        return None

    def close(self) -> None:
        return None


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    from app.core.config import get_settings

    get_settings.cache_clear()
    from app.core.database import get_db
    from app.main import app

    def _fake_db():
        yield _FakeSession()

    app.dependency_overrides[get_db] = _fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_me_returns_profile_shape(client: TestClient):
    response = client.get("/identity/me")
    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"id", "email", "full_name", "roles", "facilities", "is_corporate", "permissions"}
    assert body["email"] == "dev@local"
    assert body["full_name"]  # nunca vacío: cae al correo si no hay fila de usuario
    assert body["roles"] == []
    assert body["facilities"] == []
    assert body["is_corporate"] is True
    assert "ucca.create" in body["permissions"]
