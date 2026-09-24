"""
Configuración del scheduler de trabajos programados (sección 12 de la arquitectura técnica).
En este arquetipo se usa APScheduler embebido para simplicidad local; en producción se
recomienda un worker dedicado (ej. Celery beat) para que un reinicio del backend no afecte la
ejecución de jobs críticos como el reporte semanal.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.jobs.weekly_antipsychotic_report import run_weekly_antipsychotic_report

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    # Cada lunes 06:00 — reporte obligatorio de la semana anterior (sección M05 del funcional).
    scheduler.add_job(
        run_weekly_antipsychotic_report,
        CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="weekly_antipsychotic_report",
        replace_existing=True,
    )
    scheduler.start()
