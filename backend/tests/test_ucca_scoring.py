"""Score y outcome de una auditoría por expediente (fórmulas del Excel UCCA)."""
import pytest

from app.domains.governance.ucca.scoring import PRIORITY_OUTCOME, compute_score, outcome_for

C, N, NA = "compliant", "non_compliant", "not_applicable"


def test_all_yes_is_compliant_100():
    r = compute_score([C] * 7)
    assert (r.applicable_count, r.yes_count, r.score, r.outcome) == (7, 7, 100.0, "compliant")


def test_na_excluded_from_denominator():
    r = compute_score([C, C, C, C, C, NA, N])  # 5/6
    assert r.applicable_count == 6 and r.yes_count == 5
    assert r.score == 83.33 and r.outcome == "minor_improvement"


def test_all_not_applicable():
    r = compute_score([NA] * 7)
    assert r.applicable_count == 0 and r.yes_count == 0
    assert r.score is None and r.outcome is None


def test_empty_answers():
    r = compute_score([])
    assert r.score is None and r.outcome is None


@pytest.mark.parametrize(
    "score,expected",
    [
        (100.0, "compliant"), (90.0, "compliant"), (89.99, "minor_improvement"),
        (80.0, "minor_improvement"), (79.99, "improvement_required"),
        (70.0, "improvement_required"), (69.99, PRIORITY_OUTCOME), (0.0, PRIORITY_OUTCOME),
        (None, None),
    ],
)
def test_outcome_bands(score, expected):
    assert outcome_for(score) == expected


def test_unknown_answer_rejected():
    with pytest.raises(ValueError):
        compute_score([C, "maybe"])


def test_criterion_sort_key_follows_excel_order():
    from app.domains.governance.ucca.scoring import CRITERIA_ORDER, criterion_sort_key

    assert CRITERIA_ORDER == ("CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC")
    assert sorted(["CMC", "CDC", "CCA", "ZZZ", "CRS"], key=criterion_sort_key) == ["CCA", "CRS", "CDC", "CMC", "ZZZ"]
