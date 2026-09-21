"""
Ejemplo de ruleset para OMH001 (sección 9 del funcional): un paciente solo se evalúa contra
OMH001 si tiene un antipsicótico calificador. Este archivo es una MUESTRA para orientar la
implementación real del módulo M05 (Monitoreo de Medicación Psicotrópica y JAWDA), que deberá
incluir la lista oficial de antipsicóticos calificadores (pendiente de confirmación regulatoria,
sección 14.6 del funcional) en lugar del set de ejemplo usado aquí.
"""
from __future__ import annotations

from app.rules_engine.engine import RuleContext, RuleVerdict, register_ruleset

# Placeholder — reemplazar con la lista oficial confirmada por Farmacia/Calidad.
_EXAMPLE_QUALIFYING_ANTIPSYCHOTICS = {"risperidone", "olanzapine", "quetiapine", "clozapine"}

_REQUIRED_INVESTIGATIONS = [
    "ecg",
    "full_blood_count",
    "hba1c",
    "lipid_profile",
    "alt",
    "ast",
    "urea",
    "sodium",
    "potassium",
    "creatinine",
]


class Omh001Ruleset:
    version = "0.1.0-example"

    def evaluate(self, context: RuleContext) -> RuleVerdict:
        medication = (context.extra or {}).get("medication_name", "").lower()
        if medication not in _EXAMPLE_QUALIFYING_ANTIPSYCHOTICS:
            return RuleVerdict(
                applicable=False,
                reason="El medicamento no está en la lista de antipsicóticos calificadores "
                "(lista de ejemplo — pendiente de confirmación regulatoria).",
            )

        completed = set((context.extra or {}).get("completed_investigations", []))
        missing = [inv for inv in _REQUIRED_INVESTIGATIONS if inv not in completed]
        outcome = "compliant" if not missing else "non_compliant"
        reason = "Todas las investigaciones requeridas están registradas." if not missing else (
            f"Faltan investigaciones: {', '.join(missing)}"
        )
        return RuleVerdict(applicable=True, reason=reason, outcome=outcome)


register_ruleset("omh001_example", lambda: Omh001Ruleset())
