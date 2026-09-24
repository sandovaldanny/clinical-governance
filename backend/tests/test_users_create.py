"""POST /identity/users — flujo del documento M01: identidad → cargo → centro → profesión → roles.
La contraseña la genera el sistema y se devuelve UNA vez; queda hasheada y con cambio forzado."""
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _payload(**overrides):
    base = {
        "first_name": "Laila",
        "last_name": "Hassan",
        "employee_number": "EMP-900",
        "email": "laila@alkalma.health",
        "mobile": "+971500000000",
        "organizational_position_id": str(uuid.uuid4()),
        "profession_id": str(uuid.uuid4()),
        "facility_ids": [str(uuid.uuid4())],
        "role_ids": [str(uuid.uuid4())],
        "is_corporate_scope": False,
    }
    base.update(overrides)
    return base


def test_create_user_returns_temporary_password(monkeypatch):
    from app.core.security import verify_password
    from app.domains.identity.models import User

    # scalar #1: email existente → None; scalars #1: códigos de rol → ["auditor"]
    session = FakeSession(scalars_results=[["auditor"]])
    client = make_client(monkeypatch, session)
    response = client.post("/identity/users", json=_payload())
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user"]["email"] == "laila@alkalma.health"
    assert body["user"]["full_name"] == "Laila Hassan"
    assert body["user"]["status"] == "active"
    temp = body["temporary_password"]
    assert len(temp) >= 10
    user = next(o for o in session.added if isinstance(o, User))
    assert user.hashed_password and verify_password(temp, user.hashed_password)
    assert user.must_change_password is True
    assert str(user.created_by_user_id) == "00000000-0000-0000-0000-000000000001"
    assert session.committed


def test_create_user_requires_facility_and_role(monkeypatch):
    client = make_client(monkeypatch, FakeSession())
    assert client.post("/identity/users", json=_payload(facility_ids=[])).status_code == 422
    assert client.post("/identity/users", json=_payload(role_ids=[])).status_code == 422


def test_clinician_requires_profession(monkeypatch):
    session = FakeSession(scalars_results=[["clinician"]])
    client = make_client(monkeypatch, session)
    response = client.post("/identity/users", json=_payload(profession_id=None))
    assert response.status_code == 422
    assert "profesi" in response.json()["detail"].lower()


def test_duplicate_email_conflict(monkeypatch):
    from app.domains.identity.models import User

    existing = User(id=uuid.uuid4(), email="laila@alkalma.health", full_name="Dup")
    session = FakeSession(scalar_results=[existing])
    client = make_client(monkeypatch, session)
    assert client.post("/identity/users", json=_payload()).status_code == 409
