import pytest


@pytest.fixture
def rule_context_factory():
    from app.rules_engine.engine import RuleContext

    def _factory(**overrides):
        defaults = dict(
            facility_id="f1",
            subject_id="p1",
            profession_codes=["physician"],
            scope_of_practice=[],
            extra={},
        )
        defaults.update(overrides)
        return RuleContext(**defaults)

    return _factory
