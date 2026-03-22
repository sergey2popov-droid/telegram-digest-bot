import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.jobs.ingestion_job import run_ingestion

logger = logging.getLogger(__name__)


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
    scheduler.add_job(
        run_ingestion,
        trigger="interval",
        minutes=settings.INGESTION_INTERVAL_MINUTES,
        id="ingestion",
        name="RSS ingestion",
        replace_existing=True,
    )
    return scheduler
