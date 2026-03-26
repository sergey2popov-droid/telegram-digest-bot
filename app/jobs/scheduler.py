import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.jobs.digest_job import run_digest
from app.jobs.ingestion_job import run_ingestion

logger = logging.getLogger(__name__)


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)

    # Сбор новостей из RSS — каждые 30 минут, первый запуск сразу
    scheduler.add_job(
        run_ingestion,
        trigger="interval",
        minutes=settings.INGESTION_INTERVAL_MINUTES,
        id="ingestion",
        name="RSS ingestion",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc),
    )

    # Отправка дайджеста — каждый день в 10:00 по Москве
    scheduler.add_job(
        run_digest,
        trigger="cron",
        hour=10,
        minute=0,
        id="digest",
        name="Daily digest",
        replace_existing=True,
    )

    return scheduler
