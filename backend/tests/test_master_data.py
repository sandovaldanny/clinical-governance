"""CRUD de datos maestros M02 (cargos, centros, profesiones, catálogos): crear, editar parcial y
estado, siempre auditado. Sin Postgres: sesión doble."""
import json
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client

PERMS = frozenset({"users.view", "catalogs.manage", "facilities.manage"})


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _audit_actions(session):
    return [p["action"] for _, p in session.executed if p and "action" in p]


# ---------- positions ----------


def test_create_position(monkeypatch):
    session = FakeSession()
    client = make_client(monkeypatch, session, PERMS)
    r = client.post("/identity/positions", json={"title": "Clinical Director", "description": "Dirige un centro"})
    assert r.status_code == 201, r.text
    assert r.json()["title"] == "Clinical Director"
    assert r.json()["is_active"] is True
    assert "create" in _audit_actions(session) and session.committed


def test_create_position_duplicate_title(monkeypatch):
    from app.domains.identity.models import OrganizationalPosition

    existing = OrganizationalPosition(id=uuid.uuid4(), title="Clinical Director", is_active=True)
    client = make_client(monkeypatch, FakeSession(scalar_results=[existing]), PERMS)
    assert client.post("/identity/positions", json={"title": "Clinical Director"}).status_code == 409


def test_update_position_and_deactivate(monkeypatch):
    from app.domains.identity.models import OrganizationalPosition

    pos = OrganizationalPosition(id=uuid.uuid4(), title="Old", description="", is_active=True)
    session = FakeSession(scalar_results=[pos])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/positions/{pos.id}", json={"title": "New", "is_active": False})
    assert r.status_code == 200, r.text
    assert pos.title == "New" and pos.is_active is False
    _, params = next(e for e in session.executed if e[1] and e[1].get("action") == "update")
    assert json.loads(params["new_values"]) == {"title": "New", "is_active": "False"}


# ---------- facilities ----------


def test_create_facility_with_director(monkeypatch):
    from app.domains.identity.models import User

    director = User(id=uuid.uuid4(), email="d@alkalma.health", full_name="Dr. D", is_active=True, status="active")
    # scalar #1: nombre duplicado → None; #2: director; (#3 nombre director al serializar)
    session = FakeSession(scalar_results=[None, director, "Dr. D"])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(
        "/identity/facilities",
        json={"name": "Dubai", "country": "UAE", "city": "Dubai", "clinical_director_user_id": str(director.id)},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "active" and body["is_active"] is True
    assert body["clinical_director_name"] == "Dr. D"


def test_facility_close_syncs_is_active(monkeypatch):
    from app.domains.identity.models import Facility

    fac = Facility(id=uuid.uuid4(), name="Al Falah", city="Abu Dhabi", country="UAE", status="active", is_active=True)
    session = FakeSession(scalar_results=[fac])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/facilities/{fac.id}", json={"status": "closed"})
    assert r.status_code == 200, r.text
    assert fac.status == "closed" and fac.is_active is False


def test_facility_invalid_status(monkeypatch):
    client = make_client(monkeypatch, FakeSession(), PERMS)
    assert client.patch(f"/identity/facilities/{uuid.uuid4()}", json={"status": "gone"}).status_code == 422


# ---------- professions ----------


def test_create_profession_and_toggle(monkeypatch):
    from app.domains.identity.models import Profession

    session = FakeSession()
    client = make_client(monkeypatch, session, PERMS)
    r = client.post("/identity/professions", json={"name": "Nursing"})
    assert r.status_code == 201, r.text

    prof = Profession(id=uuid.uuid4(), name="Nursing", is_active=True)
    session2 = FakeSession(scalar_results=[prof])
    client2 = make_client(monkeypatch, session2, PERMS)
    r2 = client2.patch(f"/identity/professions/{prof.id}", json={"is_active": False})
    assert r2.status_code == 200 and prof.is_active is False


# ---------- catalogs ----------


def test_create_catalog_value_and_conflict(monkeypatch):
    from app.domains.identity.models import CatalogValue

    session = FakeSession()
    client = make_client(monkeypatch, session, PERMS)
    r = client.post("/identity/catalogs", json={"catalog_type": "specialty", "code": "neurology", "label": "Neurology"})
    assert r.status_code == 201, r.text
    assert r.json()["code"] == "neurology"

    existing = CatalogValue(id=uuid.uuid4(), catalog_type="specialty", code="neurology", label="Neurology", is_active=True)
    client2 = make_client(monkeypatch, FakeSession(scalar_results=[existing]), PERMS)
    r2 = client2.post("/identity/catalogs", json={"catalog_type": "specialty", "code": "neurology", "label": "Neuro"})
    assert r2.status_code == 409


def test_update_catalog_value(monkeypatch):
    from app.domains.identity.models import CatalogValue

    row = CatalogValue(id=uuid.uuid4(), catalog_type="specialty", code="neurology", label="Neurology", is_active=True)
    session = FakeSession(scalar_results=[row])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/catalogs/{row.id}", json={"label": "Neurología", "is_active": False})
    assert r.status_code == 200, r.text
    assert row.label == "Neurología" and row.is_active is False
