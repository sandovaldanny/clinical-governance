"""
Motor de reglas desacoplado (sección 8 de la arquitectura técnica).

UCCA, JAWDA/OMH001 y CPG comparten la misma necesidad: decidir si un criterio aplica a un
profesional/paciente/caso dado, según reglas configurables y VERSIONADAS. En vez de que cada
módulo reimplemente su propio `if profesion == "..."`, todos llaman a `evaluate()` con un
`ruleset` explícito. Esto hace el resultado reproducible: dado el mismo contexto y la misma
versión de ruleset, siempre se obtiene el mismo veredicto — lo que se necesita para poder
justificar un "No aplica" ante un auditor externo (regla global de negocio #5 del funcional).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass
class RuleContext:
    """Contexto mínimo común. Cada ruleset puede leer campos adicionales de `extra`."""

    facility_id: str
    subject_id: str  # profesional, paciente/URN, o caso, según el módulo
    profession_codes: list[str]
    scope_of_practice: list[str]
    extra: dict


@dataclass
class RuleVerdict:
    applicable: bool
    reason: str
    outcome: str | None = None  # solo si el ruleset también calcula cumplimiento (ej. OMH001)


class Ruleset(Protocol):
    version: str

    def evaluate(self, context: RuleContext) -> RuleVerdict: ...


_REGISTRY: dict[str, Callable[[], Ruleset]] = {}


def register_ruleset(code: str, factory: Callable[[], Ruleset]) -> None:
    _REGISTRY[code] = factory


def evaluate(ruleset_code: str, context: RuleContext) -> RuleVerdict:
    if ruleset_code not in _REGISTRY:
        raise KeyError(f"Ruleset no registrado: {ruleset_code}")
    ruleset = _REGISTRY[ruleset_code]()
    return ruleset.evaluate(context)
