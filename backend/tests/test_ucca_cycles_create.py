"""Ciclos UCCA: creación por centro + año + trimestre, etiqueta derivada, duplicado 409."""
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client

PERMS = frozenset({"ucca.view", "ucca.create"})


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _version():
    from app.domains.governance.ucca.models import AuditTemplateVersion

    return AuditTemplateVersion(id=uuid.uuid4(), template_id=uuid.uuid4(), version_number=1, is_current=True)


def test_create_cycle_derives_period_label(monkeypatch):
    facility = uuid.uuid4()
    # scalar #1 duplicado (None) · #2 versión vigente · #3 nombre del centro
    session = FakeSession(scalar_results=[None, _version(), "Al Bateen"])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(facility), "year": 2026, "quarter": "Q2"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["period_label"] == "Q2-2026" and body["year"] == 2026 and body["quarter"] == "Q2"
    assert body["facility_name"] == "Al Bateen" and body["audits_count"] == 0 and body["average_score"] is None
    assert session.committed


def test_create_cycle_duplicate_409(monkeypatch):
    from app.domains.governance.ucca.models import AuditCycle

    facility = uuid.uuid4()
    existing = AuditCycle(id=uuid.uuid4(), facility_id=facility, template_version_id=uuid.uuid4(),
                          period_label="Q2-2026", year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.uuid4())
    client = make_client(monkeypatch, FakeSession(scalar_results=[existing]), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(facility), "year": 2026, "quarter": "Q2"})
    assert r.status_code == 409


def test_create_cycle_invalid_quarter_422(monkeypatch):
    client = make_client(monkeypatch, FakeSession(), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(uuid.uuid4()), "year": 2026, "quarter": "Q5"})
    assert r.status_code == 422


def test_create_cycle_without_template_422(monkeypatch):
    client = make_client(monkeypatch, FakeSession(scalar_results=[None, None]), PERMS)
    r = client.post("/ucca/cycles", json={"facility_id": str(uuid.uuid4()), "year": 2026, "quarter": "Q1"})
    assert r.status_code == 422


def test_list_cycles_enriched(monkeypatch):
    from app.domains.governance.ucca.models import AuditCycle

    cycle = AuditCycle(id=uuid.uuid4(), facility_id=uuid.uuid4(), template_version_id=uuid.uuid4(),
                       period_label="Q2-2026", year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.uuid4())
    session = FakeSession(execute_rows=[[(cycle, "Al Bateen", 5, 92.5)]])
    client = make_client(monkeypatch, session, PERMS)
    r = client.get("/ucca/cycles")
    assert r.status_code == 200, r.text
    row = r.json()[0]
    assert row["facility_name"] == "Al Bateen" and row["audits_count"] == 5 and row["average_score"] == 92.5
