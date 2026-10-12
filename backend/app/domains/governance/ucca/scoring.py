"""
Score y outcome de una auditoría por expediente. Réplica exacta de las fórmulas del Excel UCCA:
  Score   = IF(Applicable=0, "", YesCount/Applicable)
  Outcome = IF(Score="", "", IF(Score>=90%,"Compliant", IF(Score>=80%,"Minor Improvement",
            IF(Score>=70%,"Improvement Required","Priority Corrective Action"))))
Función pura: sin DB, sin FastAPI. El frontend la replica en `modules/ucca/scoring.ts`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ANSWER_YES = "compliant"
ANSWER_NO = "non_compliant"
ANSWER_NA = "not_applicable"
ANSWER_VALUES = (ANSWER_YES, ANSWER_NO, ANSWER_NA)

# (outcome, umbral mínimo en %) — evaluados en orden. Por debajo del último → PRIORITY_OUTCOME.
OUTCOME_BANDS: tuple[tuple[str, float], ...] = (
    ("compliant", 90.0),
    ("minor_improvement", 80.0),
    ("improvement_required", 70.0),
)
PRIORITY_OUTCOME = "priority_corrective_action"
OUTCOME_VALUES = tuple(o for o, _ in OUTCOME_BANDS) + (PRIORITY_OUTCOME,)


@dataclass(frozen=True)
class ScoreResult:
    applicable_count: int
    yes_count: int
    score: float | None
    outcome: str | None


def outcome_for(score: float | None) -> str | None:
    if score is None:
        return None
    for outcome, threshold in OUTCOME_BANDS:
        if score >= threshold:
            return outcome
    return PRIORITY_OUTCOME


def compute_score(outcomes: Iterable[str]) -> ScoreResult:
    answers = list(outcomes)
    for value in answers:
        if value not in ANSWER_VALUES:
            raise ValueError(f"Respuesta no válida: {value!r}")
    applicable = sum(1 for a in answers if a != ANSWER_NA)
    yes = sum(1 for a in answers if a == ANSWER_YES)
    score = None if applicable == 0 else round(yes / applicable * 100, 2)
    return ScoreResult(applicable_count=applicable, yes_count=yes, score=score, outcome=outcome_for(score))
