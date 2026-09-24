"""
PATCH /identity/users/{id}/status activa / inactiva / suspende una cuenta (M01: las cuentas no se
borran, se desactivan para preservar autoría). Sin Postgres: sesión doble.
"""
import uuid

import pytest

from tests._fakes import DEV_USER_ID, FakeSession, cleanup, make_client


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _user(user_id: uuid.UUID, is_active: bool = True):
    from app.domains.identity.models import User

    return User(
        id=user_id, email="x@alkalma.health", full_name="X", is_active=is_active,
        status="active" if is_active else "inactive",
    )


def test_deactivate_user(monkeypatch):
    target = _user(uuid.uuid4())
    session = FakeSession(scalar_results=[target])
    client = make_client(monkeypatch, session)
    response = client.patch(f"/identity/users/{target.id}/status", json={"status": "inactive"})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "inactive"
    assert response.json()["is_active"] is False
    assert target.is_active is False
    assert session.committed is True


def test_cannot_deactivate_self(monkeypatch):
    me = _user(uuid.UUID(DEV_USER_ID))
    client = make_client(monkeypatch, FakeSession(scalar_results=[me]))
    response = client.patch(f"/identity/users/{me.id}/status", json={"status": "suspended"})
    assert response.status_code == 409
    assert me.is_active is True


def test_unknown_user_404(monkeypatch):
    client = make_client(monkeypatch, FakeSession())
    response = client.patch(f"/identity/users/{uuid.uuid4()}/status", json={"status": "inactive"})
    assert response.status_code == 404
