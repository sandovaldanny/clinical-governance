"""Agregados UCCA (summary por ciclo y dashboard). Función pura sobre filas simples para poder
probarla sin DB. Solo cuentan auditorías `submitted`/`approved`; los borradores se reportan aparte."""
from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date

from app.domains.governance.ucca.scoring import ANSWER_NA, ANSWER_YES, OUTCOME_VALUES, outcome_for

COUNTED_STATUSES = ("submitted", "approved")


@dataclass(frozen=True)
class AuditRow:
    id: uuid.UUID
    professional_id: uuid.UUID
    employee_number: str
    professional_name: str
    profession_name: str | None
    status: str
    score: float | None
    outcome: str | None
    year: int
    quarter: str


@dataclass(frozen=True)
class AnswerRow:
    audit_id: uuid.UUID
    code: str
    outcome: str


@dataclass(frozen=True)
class OpenActionRow:
    id: uuid.UUID
    audit_id: uuid.UUID
    case_reference: str
    professional_name: str
    finding: str
    responsible_name: str | None
    due_date: date
    status: str


def _avg(values: list[float]) -> float | None:
    return None if not values else round(sum(values) / len(values), 2)


def _rate(yes: int, applicable: int) -> float | None:
    return None if applicable == 0 else round(yes / applicable * 100, 2)


def summarize(audits: list[AuditRow], answers: list[AnswerRow], criteria_codes: list[str],
              open_actions: list[OpenActionRow]) -> dict:
    counted = [a for a in audits if a.status in COUNTED_STATUSES]
    counted_ids = {a.id for a in counted}
    draft_count = sum(1 for a in audits if a.status == "draft")

    distribution = {o: 0 for o in OUTCOME_VALUES}
    for a in counted:
        if a.outcome in distribution:
            distribution[a.outcome] += 1

    # por criterio
    crit_app: dict[str, int] = defaultdict(int)
    crit_yes: dict[str, int] = defaultdict(int)
    # por profesional y criterio
    pro_app: dict[tuple, int] = defaultdict(int)
    pro_yes: dict[tuple, int] = defaultdict(int)
    audit_pro = {a.id: a.professional_id for a in counted}
    for ans in answers:
        if ans.audit_id not in counted_ids:
            continue
        pro = audit_pro[ans.audit_id]
        if ans.outcome != ANSWER_NA:
            crit_app[ans.code] += 1
            pro_app[(pro, ans.code)] += 1
            if ans.outcome == ANSWER_YES:
                crit_yes[ans.code] += 1
                pro_yes[(pro, ans.code)] += 1

    criteria = [
        {"code": code, "applicable": crit_app[code], "yes": crit_yes[code], "yes_rate": _rate(crit_yes[code], crit_app[code])}
        for code in criteria_codes
    ]

    by_pro: dict[uuid.UUID, list[AuditRow]] = defaultdict(list)
    for a in counted:
        by_pro[a.professional_id].append(a)
    professionals = []
    for pro_id, rows in by_pro.items():
        scores = [r.score for r in rows if r.score is not None]
        avg = _avg(scores)
        professionals.append({
            "professional_id": pro_id, "employee_number": rows[0].employee_number,
            "professional_name": rows[0].professional_name, "profession_name": rows[0].profession_name,
            "audits_count": len(rows), "average_score": avg, "outcome": outcome_for(avg),
            "criteria": {code: _rate(pro_yes[(pro_id, code)], pro_app[(pro_id, code)]) for code in criteria_codes},
        })
    professionals.sort(key=lambda p: p["professional_name"])

    by_period: dict[tuple[int, str], list[float]] = defaultdict(list)
    period_counts: dict[tuple[int, str], int] = defaultdict(int)
    for a in counted:
        period_counts[(a.year, a.quarter)] += 1
        if a.score is not None:
            by_period[(a.year, a.quarter)].append(a.score)
    trend = [
        {"year": y, "quarter": q, "audits_count": period_counts[(y, q)], "average_score": _avg(by_period[(y, q)])}
        for (y, q) in sorted(period_counts)
    ]

    return {
        "audits_count": len(counted),
        "draft_count": draft_count,
        "average_score": _avg([a.score for a in counted if a.score is not None]),
        "outcome_distribution": distribution,
        "criteria": criteria,
        "professionals": professionals,
        "trend": trend,
        "open_corrective_actions": [asdict(r) for r in open_actions],
    }
