"""PATCH /identity/users/{id}: edición parcial con reemplazo de centros/roles y auditoría del diff."""
import json
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _user():
    from app.domains.identity.models import User

    return User(
        id=uuid.uuid4(), email="x@alkalma.health", first_name="X", last_name="Y", full_name="X Y",
        status="active", is_active=True,
    )


def test_update_user_fields_and_roles(monkeypatch):
    from app.domains.identity.models import UserRoleAssignment

    target = _user()
    old_role = UserRoleAssignment(id=uuid.uuid4(), user_id=target.id, role_id=uuid.uuid4())
    new_role_id = uuid.uuid4()
    # scalar #1: usuario objetivo. scalars #1: códigos de los roles nuevos; scalars #2: asignaciones actuales.
    session = FakeSession(scalar_results=[target], scalars_results=[["auditor"], [old_role]])
    client = make_client(monkeypatch, session)
    response = client.patch(
        f"/identity/users/{target.id}",
        json={"first_name": "Xavier", "mobile": "+971", "role_ids": [str(new_role_id)]},
    )
    assert response.status_code == 200, response.text
    assert target.first_name == "Xavier"
    assert target.full_name == "Xavier Y"
    assert old_role in session.deleted
    assert any(isinstance(o, UserRoleAssignment) and o.role_id == new_role_id for o in session.added)
    # evento de auditoría con diff
    stmt, params = next(e for e in session.executed if e[1] and e[1].get("action") == "update")
    assert json.loads(params["previous_values"])["first_name"] == "X"
    assert json.loads(params["new_values"])["first_name"] == "Xavier"
    assert session.committed


def test_update_unknown_user_404(monkeypatch):
    client = make_client(monkeypatch, FakeSession())
    assert client.patch(f"/identity/users/{uuid.uuid4()}", json={"first_name": "Z"}).status_code == 404


def test_status_enum(monkeypatch):
    target = _user()
    session = FakeSession(scalar_results=[target])
    client = make_client(monkeypatch, session)
    response = client.patch(f"/identity/users/{target.id}/status", json={"status": "suspended"})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "suspended"
    assert target.is_active is False


def test_status_invalid_value(monkeypatch):
    client = make_client(monkeypatch, FakeSession(scalar_results=[_user()]))
    assert client.patch(f"/identity/users/{uuid.uuid4()}/status", json={"status": "banned"}).status_code == 422
