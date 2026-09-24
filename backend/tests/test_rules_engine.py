"""
Prueba de referencia del motor de reglas: mismo contexto + misma versión de ruleset debe
producir siempre el mismo veredicto (requisito de reproducibilidad, sección 8 de la
arquitectura técnica).
"""
from app.rules_engine.engine import evaluate
import app.rules_engine.rulesets.omh001_example  # noqa: F401 — registra el ruleset


def test_omh001_not_applicable_without_qualifying_medication(rule_context_factory):
    ctx = rule_context_factory(extra={"medication_name": "ibuprofen"})
    verdict = evaluate("omh001_example", ctx)
    assert verdict.applicable is False
    assert "No aplica" not in verdict.reason  # el motor da la razón, no una etiqueta genérica


def test_omh001_flags_missing_investigations(rule_context_factory):
    ctx = rule_context_factory(
        extra={"medication_name": "risperidone", "completed_investigations": ["ecg", "hba1c"]}
    )
    verdict = evaluate("omh001_example", ctx)
    assert verdict.applicable is True
    assert verdict.outcome == "non_compliant"
