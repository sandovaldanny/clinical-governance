"""
PATCH /identity/users/{id}/status activa o desactiva una cuenta (M01: activar/suspender/
desactivar; regla: las cuentas no se borran, se desactivan para preservar autoría).
Sin Postgres: sesión doble que devuelve un User en memoria.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"


class _EmptyScalars:
    def all(self):
        return []


class _FakeSession:
    def __init__(self, user):
        self.user = user
        self.committed = False

    def scalar(self, *_args, **_kwargs):
        return self.user

    def scalars(self, *_args, **_kwargs):
        return _EmptyScalars()

    def execute(self, *_args, **_kwargs):
        return None

    def commit(self):
        self.committed = True

    def refresh(self, *_args, **_kwargs):
        return None

    def close(self):
        return None


def _make_client(monkeypatch, user):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    from app.core.config import get_settings

    get_settings.cache_clear()
    from app.core.database import get_db
    from app.core import deps
    from app.main import app

    session = _FakeSession(user)
    def _fake_db():
        yield session

    app.dependency_overrides[get_db] = _fake_db
    # El bypass consulta al admin del seed; forzamos el usuario dev fijo.
    monkeypatch.setattr(deps, "_dev_bypass_user", lambda db: deps.CurrentUser(
        id=DEV_USER_ID, email="dev@local", facility_ids=[], is_corporate=True,
        effective_permissions={"users.manage", "users.view"},
    ))
    return TestClient(app), session


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    from app.core.config import get_settings
    from app.main import app

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _user(user_id: uuid.UUID, is_active: bool = True):
    from app.domains.identity.models import User

    return User(id=user_id, email="x@alkalma.health", full_name="X", is_active=is_active)


def test_deactivate_user(monkeypatch):
    target = _user(uuid.uuid4())
    client, session = _make_client(monkeypatch, target)
    response = client.patch(f"/identity/users/{target.id}/status", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert target.is_active is False
    assert session.committed is True


def test_cannot_deactivate_self(monkeypatch):
    me = _user(uuid.UUID(DEV_USER_ID))
    client, _ = _make_client(monkeypatch, me)
    response = client.patch(f"/identity/users/{me.id}/status", json={"is_active": False})
    assert response.status_code == 409
    assert me.is_active is True


def test_unknown_user_404(monkeypatch):
    client, _ = _make_client(monkeypatch, None)
    response = client.patch(f"/identity/users/{uuid.uuid4()}/status", json={"is_active": False})
    assert response.status_code == 404
