"""Auditoría por expediente: crear con 7 respuestas, score/outcome calculados, hallazgo + acción
correctiva, editar solo en borrador, enviar/aprobar. Sin Postgres (tests/_fakes.py)."""
import json
import uuid
from datetime import date

import pytest

from tests._fakes import DEV_USER_ID, FakeSession, cleanup, make_client

PERMS = frozenset({"ucca.view", "ucca.create", "ucca.approve"})
FACILITY = uuid.uuid4()
VERSION = uuid.uuid4()
CODES = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _cycle():
    from app.domains.governance.ucca.models import AuditCycle

    return AuditCycle(
        id=uuid.uuid4(), facility_id=FACILITY, template_version_id=VERSION, period_label="Q2-2026",
        year=2026, quarter="Q2", status="draft", created_by_user_id=uuid.UUID(DEV_USER_ID),
    )


def _professional(facility=FACILITY, active=True):
    from app.domains.identity.models import Professional

    return Professional(
        id=uuid.uuid4(), employee_number="CL-0029", full_name="Dr. Divya Rani",
        profession_id=uuid.uuid4(), primary_facility_id=facility, scope_of_practice=[], is_active=active,
    )


def _criteria():
    from app.domains.governance.ucca.models import AuditCriterion

    return [
        AuditCriterion(id=uuid.uuid4(), template_version_id=VERSION, code=c, domain=c, universal_question="?",
                       profession_interpretation="", examples_evidence="", is_active=True)
        for c in CODES
    ]


def _answers(criteria, outcomes):
    return [
        {"criterion_id": str(c.id), "outcome": o, "not_applicable_reason": "Fuera de alcance" if o == "not_applicable" else None}
        for c, o in zip(criteria, outcomes)
    ]


def _payload(criteria, outcomes, finding=None):
    body = {
        "professional_id": str(_PRO.id), "case_reference": "102453", "audit_date": "2026-07-20",
        "notes": "", "answers": _answers(criteria, outcomes),
    }
    if finding is not None:
        body["finding"] = finding
    return body


_PRO = _professional()


def _events(session):
    return [p for _, p in session.executed if p and "action" in p]


def _create_session(cycle, professional, criteria, duplicate=None):
    # scalar #1 ciclo (router) · #2 profesional · #3 duplicado · scalars #1 criterios
    return FakeSession(scalar_results=[cycle, professional, duplicate], scalars_results=[criteria])


def test_create_all_yes_is_compliant(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    session = _create_session(cycle, _PRO, criteria)
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["compliant"] * 7))
    assert r.status_code == 201, r.text
    body = r.json()
    assert (body["applicable_count"], body["yes_count"], body["score"], body["outcome"]) == (7, 7, 100.0, "compliant")
    assert body["status"] == "draft" and body["employee_number"] == "CL-0029"
    assert {a["criterion_code"] for a in body["answers"]} == set(CODES)
    from app.domains.governance.ucca.models import AuditResult, ChartAudit

    assert sum(isinstance(o, ChartAudit) for o in session.added) == 1
    assert sum(isinstance(o, AuditResult) for o in session.added) == 7
    assert {e["entity_type"] for e in _events(session)} >= {"ChartAudit"}
    assert session.committed


def test_create_with_na_and_no_requires_finding(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    outcomes = ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"]  # 4/6 = 66.67
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, outcomes))
    assert r.status_code == 422 and "hallazgo" in r.json()["detail"].lower()


def test_create_with_finding_and_action(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    outcomes = ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"]
    owner = uuid.uuid4()
    finding = {
        "description": "Risk assessment missing",
        "corrective_action": {"description": "Retrain on risk documentation", "responsible_user_id": str(owner),
                              "due_date": "2026-08-30", "status": "assigned"},
    }
    session = _create_session(cycle, _PRO, criteria)
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, outcomes, finding))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["score"] == 66.67 and body["outcome"] == "priority_corrective_action"
    assert body["finding"]["description"] == "Risk assessment missing"
    assert body["finding"]["corrective_action"]["status"] == "assigned"
    from app.domains.governance.corrective_actions.models import CorrectiveAction
    from app.domains.governance.ucca.models import Finding

    assert any(isinstance(o, Finding) and o.chart_audit_id is not None for o in session.added)
    ca = next(o for o in session.added if isinstance(o, CorrectiveAction))
    assert ca.source_module == "ucca" and ca.responsible_user_id == owner and ca.description.startswith("Retrain")


def test_create_all_na_no_finding_required(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    r = client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["not_applicable"] * 7))
    assert r.status_code == 201, r.text
    assert r.json()["score"] is None and r.json()["outcome"] is None


def test_create_na_without_reason_422(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    body = _payload(criteria, ["compliant"] * 6 + ["not_applicable"])
    body["answers"][6]["not_applicable_reason"] = "   "
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def test_create_rejects_unknown_or_duplicate_criterion(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    body = _payload(criteria, ["compliant"] * 7)
    body["answers"][0]["criterion_id"] = str(uuid.uuid4())  # ajeno
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422
    body = _payload(criteria, ["compliant"] * 7)
    body["answers"][1]["criterion_id"] = body["answers"][0]["criterion_id"]  # repetido
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def test_create_duplicate_case_409(monkeypatch):
    from app.domains.governance.ucca.models import ChartAudit

    cycle, criteria = _cycle(), _criteria()
    existing = ChartAudit(id=uuid.uuid4(), cycle_id=cycle.id, facility_id=FACILITY, professional_id=_PRO.id,
                          auditor_user_id=uuid.uuid4(), case_reference="102453", audit_date=date.today(), status="draft")
    client = make_client(monkeypatch, _create_session(cycle, _PRO, criteria, duplicate=existing), PERMS)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=_payload(criteria, ["compliant"] * 7)).status_code == 409


def test_create_professional_other_facility_422(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    other = _professional(facility=uuid.uuid4())
    client = make_client(monkeypatch, _create_session(cycle, other, criteria), PERMS)
    body = _payload(criteria, ["compliant"] * 7)
    body["professional_id"] = str(other.id)
    assert client.post(f"/ucca/cycles/{cycle.id}/audits", json=body).status_code == 422


def _existing_audit(cycle, status="draft"):
    from app.domains.governance.ucca.models import ChartAudit

    return ChartAudit(id=uuid.uuid4(), cycle_id=cycle.id, facility_id=FACILITY, professional_id=_PRO.id,
                      auditor_user_id=uuid.UUID(DEV_USER_ID), case_reference="102453", audit_date=date(2026, 7, 20),
                      status=status, applicable_count=7, yes_count=7, score=100.0, outcome="compliant", notes="")


def _existing_results(audit, criteria):
    from app.domains.governance.ucca.models import AuditResult

    return [AuditResult(id=uuid.uuid4(), chart_audit_id=audit.id, facility_id=FACILITY, cycle_id=audit.cycle_id,
                        criterion_id=c.id, professional_id=_PRO.id, auditor_user_id=audit.auditor_user_id,
                        outcome="compliant", status="draft") for c in criteria]


def test_update_replaces_answers_and_recomputes(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    old_results = _existing_results(audit, criteria)
    # scalar #1 auditoría (router) · #2 ciclo · #3 profesional · #4 duplicado (None)
    # scalars #1 criterios · #2 resultados previos · scalar #5 finding previo (None)
    session = FakeSession(scalar_results=[audit, cycle, _PRO, None, None], scalars_results=[criteria, old_results])
    client = make_client(monkeypatch, session, PERMS)
    outcomes = ["compliant"] * 6 + ["non_compliant"]  # 6/7 = 85.71
    r = client.patch(f"/ucca/audits/{audit.id}", json=_payload(criteria, outcomes, {"description": "CMC gap"}))
    assert r.status_code == 200, r.text
    assert r.json()["score"] == 85.71 and r.json()["outcome"] == "minor_improvement"
    assert len(session.deleted) == 7  # respuestas viejas fuera
    from app.domains.governance.ucca.models import AuditResult

    assert sum(isinstance(o, AuditResult) for o in session.added) == 7
    update = next(e for e in _events(session) if e["entity_type"] == "ChartAudit" and e["action"] == "update")
    assert json.loads(update["new_values"])["score"] == "85.71"


def test_update_approved_409(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle, status="approved")
    client = make_client(monkeypatch, FakeSession(scalar_results=[audit]), PERMS)
    assert client.patch(f"/ucca/audits/{audit.id}", json=_payload(criteria, ["compliant"] * 7)).status_code == 409


def test_submit_then_approve(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    results = _existing_results(audit, criteria)
    # submit: scalar #1 auditoría · scalars #1 resultados · (detalle) scalar #2 profesional, #3 auditor name, scalars #2 answers rows, scalar #4 finding
    session = FakeSession(scalar_results=[audit, _PRO, "Dev", None], scalars_results=[results, []])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/audits/{audit.id}/submit")
    assert r.status_code == 200, r.text and r.json()["status"] == "submitted"
    assert all(res.status == "submitted" for res in results)

    session = FakeSession(scalar_results=[audit, _PRO, "Dev", None], scalars_results=[results, []])
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(f"/ucca/audits/{audit.id}/approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved" and all(res.status == "approved" for res in results)
    assert any(e["action"] == "approve" for e in _events(session))


def test_approve_from_draft_409(monkeypatch):
    cycle = _cycle()
    audit = _existing_audit(cycle, status="draft")
    client = make_client(monkeypatch, FakeSession(scalar_results=[audit]), PERMS)
    assert client.post(f"/ucca/audits/{audit.id}/approve").status_code == 409


def test_list_chart_audits_rows(monkeypatch):
    cycle, criteria = _cycle(), _criteria()
    audit = _existing_audit(cycle)
    header_rows = [(audit, "Dr. Divya Rani", "CL-0029", "Psychiatrist", "Dr Ramez Abu Sabha")]
    answer_rows = [(audit.id, c.code, "compliant") for c in criteria]
    finding_rows = []
    session = FakeSession(scalar_results=[cycle], execute_rows=[header_rows, answer_rows, finding_rows])
    client = make_client(monkeypatch, session, PERMS)
    r = client.get(f"/ucca/cycles/{cycle.id}/audits")
    assert r.status_code == 200, r.text
    row = r.json()[0]
    assert row["employee_number"] == "CL-0029" and row["profession_name"] == "Psychiatrist"
    assert row["answers"] == {c: "compliant" for c in CODES}
    assert row["score"] == 100.0 and row["outcome"] == "compliant" and row["has_finding"] is False
