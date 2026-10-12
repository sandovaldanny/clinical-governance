"""Agregados UCCA: solo auditorías enviadas/aprobadas; % por criterio; por profesional; tendencia."""
import uuid
from datetime import date

from app.domains.governance.ucca.summary import AnswerRow, AuditRow, OpenActionRow, summarize

CODES = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]
P1, P2 = uuid.uuid4(), uuid.uuid4()


def _audit(aid, pro, status, score, outcome, quarter="Q2"):
    name = "Dr. Divya Rani" if pro == P1 else "Dr. Ahmed"
    return AuditRow(id=aid, professional_id=pro, employee_number="CL-0029" if pro == P1 else "CL-0030",
                    professional_name=name, profession_name="Psychiatrist", status=status, score=score,
                    outcome=outcome, year=2026, quarter=quarter)


def _answers(aid, outcomes):
    return [AnswerRow(audit_id=aid, code=c, outcome=o) for c, o in zip(CODES, outcomes)]


def test_summarize_empty():
    s = summarize([], [], CODES, [])
    assert s["audits_count"] == 0 and s["draft_count"] == 0 and s["average_score"] is None
    assert s["outcome_distribution"] == {"compliant": 0, "minor_improvement": 0, "improvement_required": 0, "priority_corrective_action": 0}
    assert [c["code"] for c in s["criteria"]] == CODES and all(c["yes_rate"] is None for c in s["criteria"])
    assert s["professionals"] == [] and s["trend"] == [] and s["open_corrective_actions"] == []


def test_summarize_ignores_drafts():
    a1, a2 = uuid.uuid4(), uuid.uuid4()
    audits = [_audit(a1, P1, "approved", 100.0, "compliant"), _audit(a2, P1, "draft", 50.0, "priority_corrective_action")]
    answers = _answers(a1, ["compliant"] * 7) + _answers(a2, ["non_compliant"] * 7)
    s = summarize(audits, answers, CODES, [])
    assert s["audits_count"] == 1 and s["draft_count"] == 1 and s["average_score"] == 100.0
    assert s["criteria"][0]["yes_rate"] == 100.0


def test_summarize_by_criterion_and_professional():
    a1, a2, a3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    audits = [
        _audit(a1, P1, "approved", 100.0, "compliant"),
        _audit(a2, P1, "submitted", 66.67, "priority_corrective_action"),
        _audit(a3, P2, "approved", 85.71, "minor_improvement", quarter="Q3"),
    ]
    answers = (
        _answers(a1, ["compliant"] * 7)
        + _answers(a2, ["compliant"] * 4 + ["not_applicable", "non_compliant", "non_compliant"])
        + _answers(a3, ["compliant"] * 6 + ["non_compliant"])
    )
    s = summarize(audits, answers, CODES, [])
    assert s["audits_count"] == 3 and s["average_score"] == 84.13
    assert s["outcome_distribution"]["compliant"] == 1 and s["outcome_distribution"]["priority_corrective_action"] == 1
    cdc = next(c for c in s["criteria"] if c["code"] == "CDC")
    assert (cdc["applicable"], cdc["yes"], cdc["yes_rate"]) == (2, 2, 100.0)  # a2 fue N/A
    cmc = next(c for c in s["criteria"] if c["code"] == "CMC")
    assert (cmc["applicable"], cmc["yes"], cmc["yes_rate"]) == (3, 1, 33.33)
    p1 = next(p for p in s["professionals"] if p["professional_id"] == P1)
    assert p1["audits_count"] == 2 and p1["average_score"] == 83.34 and p1["outcome"] == "minor_improvement"
    assert p1["criteria"]["CDC"] == 100.0 and p1["criteria"]["CMC"] == 50.0
    assert s["trend"] == [{"year": 2026, "quarter": "Q2", "audits_count": 2, "average_score": 83.34},
                          {"year": 2026, "quarter": "Q3", "audits_count": 1, "average_score": 85.71}]


def test_summarize_open_actions_passthrough():
    row = OpenActionRow(id=uuid.uuid4(), audit_id=uuid.uuid4(), case_reference="102453", professional_name="Dr. Divya Rani",
                        finding="Risk missing", responsible_name="Sara", due_date=date(2026, 8, 30), status="assigned")
    s = summarize([], [], CODES, [row])
    assert s["open_corrective_actions"][0]["case_reference"] == "102453"


def test_dashboard_endpoint_empty(monkeypatch):
    from tests._fakes import FakeSession, cleanup, make_client

    # scalar #1 versión vigente (None → sin criterios) · execute #1 auditorías vacías
    client = make_client(monkeypatch, FakeSession(scalar_results=[None], execute_rows=[[]]), frozenset({"ucca.view"}))
    try:
        r = client.get("/ucca/dashboard?year=2026&quarter=Q2")
        assert r.status_code == 200, r.text
        assert r.json()["audits_count"] == 0 and r.json()["criteria"] == []
        assert client.get("/ucca/dashboard?quarter=Q9").status_code == 422
    finally:
        cleanup()
