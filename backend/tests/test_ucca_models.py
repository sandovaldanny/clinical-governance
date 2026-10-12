"""Los modelos UCCA exponen las columnas del diseño chart-audit (sin Postgres)."""
import uuid
from datetime import date


def test_chart_audit_columns():
    from app.domains.governance.ucca.models import ChartAudit

    audit = ChartAudit(
        cycle_id=uuid.uuid4(), facility_id=uuid.uuid4(), professional_id=uuid.uuid4(),
        auditor_user_id=uuid.uuid4(), case_reference="102453", audit_date=date(2026, 7, 20),
        status="draft", applicable_count=7, yes_count=7, score=100.0, outcome="compliant", notes="",
    )
    assert ChartAudit.__tablename__ == "ucca_chart_audits"
    assert audit.case_reference == "102453" and audit.score == 100.0


def test_result_finding_action_cycle_columns():
    from app.domains.governance.corrective_actions.models import CorrectiveAction
    from app.domains.governance.ucca.models import AuditCycle, AuditResult, Finding

    assert "chart_audit_id" in AuditResult.__table__.c and "comment" in AuditResult.__table__.c
    assert "chart_audit_id" in Finding.__table__.c and Finding.__table__.c.result_id.nullable
    for col in ("description", "closure_evidence", "closed_at"):
        assert col in CorrectiveAction.__table__.c
    assert "year" in AuditCycle.__table__.c and "quarter" in AuditCycle.__table__.c
