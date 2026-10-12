"""Criterios de evaluación (UCCA): listar, crear, editar y activar/inactivar desde Administración.
Sin Postgres: sesión doble (ver tests/_fakes.py)."""
import json
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client

PERMS = frozenset({"ucca.view", "catalogs.manage"})
VERSION_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _version():
    from app.domains.governance.ucca.models import AuditTemplateVersion

    return AuditTemplateVersion(id=VERSION_ID, template_id=uuid.uuid4(), version_number=1, is_current=True)


def _criterion(code="CCA", active=True):
    from app.domains.governance.ucca.models import AuditCriterion

    return AuditCriterion(
        id=uuid.uuid4(),
        template_version_id=VERSION_ID,
        code=code,
        domain="Clinical Assessment",
        universal_question="Was an appropriate assessment completed?",
        profession_interpretation="Psychiatric history, MSE.",
        examples_evidence="Psychiatric history, MSE.",
        is_active=active,
    )


def _audit_events(session):
    return [p for _, p in session.executed if p and "action" in p]


def test_list_criteria_exposes_five_fields_and_status(monkeypatch):
    session = FakeSession(scalar_results=[_version()], scalars_results=[[_criterion()]])
    client = make_client(monkeypatch, session, PERMS)
    r = client.get("/ucca/criteria")
    assert r.status_code == 200, r.text
    row = r.json()[0]
    assert row["code"] == "CCA"
    assert row["domain"] == "Clinical Assessment"
    assert row["universal_question"].startswith("Was an appropriate")
    assert row["profession_interpretation"] and row["examples_evidence"]
    assert row["is_active"] is True
    assert "severity" not in row


def test_create_criterion_links_current_version_and_audits(monkeypatch):
    # scalar #1: versión vigente; #2: código duplicado → None
    session = FakeSession(scalar_results=[_version(), None])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(
        "/ucca/criteria",
        json={
            "code": "CRS",
            "domain": "Clinical Risk & Safety",
            "universal_question": "Were relevant risks identified and documented?",
            "profession_interpretation": "Suicide, violence, safeguarding risks.",
            "examples_evidence": "Safety plan/escalation when indicated.",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["code"] == "CRS" and body["is_active"] is True
    assert body["template_version_id"] == str(VERSION_ID)
    created = session.added[0]
    assert created.template_version_id == VERSION_ID
    events = _audit_events(session)
    assert events and events[0]["action"] == "create" and events[0]["module"] == "ucca"
    assert session.committed


def test_create_criterion_duplicate_code_is_409(monkeypatch):
    session = FakeSession(scalar_results=[_version(), _criterion("CRS")])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(
        "/ucca/criteria",
        json={"code": "CRS", "domain": "X", "universal_question": "Q?"},
    )
    assert r.status_code == 409


def test_create_criterion_without_template_version_is_422(monkeypatch):
    client = make_client(monkeypatch, FakeSession(scalar_results=[None]), PERMS)
    r = client.post("/ucca/criteria", json={"code": "CRS", "domain": "X", "universal_question": "Q?"})
    assert r.status_code == 422


def test_update_criterion_partial_and_deactivate(monkeypatch):
    crit = _criterion()
    session = FakeSession(scalar_results=[crit])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/ucca/criteria/{crit.id}", json={"domain": "Assessment", "is_active": False})
    assert r.status_code == 200, r.text
    assert crit.domain == "Assessment" and crit.is_active is False
    assert crit.code == "CCA"  # el código no cambia por PATCH
    update = next(e for e in _audit_events(session) if e["action"] == "update")
    assert json.loads(update["new_values"]) == {"domain": "Assessment", "is_active": "False"}
    assert json.loads(update["previous_values"]) == {"domain": "Clinical Assessment", "is_active": "True"}


def test_update_criterion_not_found(monkeypatch):
    client = make_client(monkeypatch, FakeSession(scalar_results=[None]), PERMS)
    assert client.patch(f"/ucca/criteria/{uuid.uuid4()}", json={"domain": "X"}).status_code == 404


def test_list_criteria_only_active_filter(monkeypatch):
    from app.domains.governance.ucca import service

    captured = {}

    def fake_list(db, *, only_active=False):
        captured["only_active"] = only_active
        return []

    monkeypatch.setattr(service, "list_criteria", fake_list)
    client = make_client(monkeypatch, FakeSession(), PERMS)
    assert client.get("/ucca/criteria?only_active=true").status_code == 200
    assert captured["only_active"] is True
