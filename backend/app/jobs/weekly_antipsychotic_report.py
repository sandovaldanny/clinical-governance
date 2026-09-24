"""
Esqueleto del job crítico descrito en la sección 9 de la arquitectura técnica: debe fallar de
forma RUIDOSA, nunca en silencio — un reporte de los lunes que no se genera tiene impacto
regulatorio directo (riesgo técnico #3 del documento de arquitectura).
"""
from __future__ import annotations

import logging

logger = logging.getLogger("aegis.jobs.weekly_antipsychotic_report")


def run_weekly_antipsychotic_report() -> None:
    """
    Pendiente de implementación real (M05). Debe:
    1. Leer la población clasificada de la semana anterior (motor de reglas / omh001 ruleset).
    2. Generar la vista de población antipsicótica + URNs únicos.
    3. Renderizar y distribuir el reporte a Medical Directors y destinatarios configurados.
    4. Registrar la ejecución (éxito/fallo/cantidad de registros) y ALERTAR a IT si falla o si
       el volumen es anómalo respecto a semanas anteriores — no debe fallar silenciosamente.
    """
    try:
        logger.info("Ejecutando reporte semanal de antipsicóticos (placeholder de arquetipo).")
        raise NotImplementedError("Implementar en M05 siguiendo el patrón de app/rules_engine.")
    except Exception:
        logger.exception("Fallo en el job del reporte semanal de antipsicóticos — requiere alerta a IT.")
        raise
