import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.router import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.jobs.scheduler import build_scheduler

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()

    scheduler = build_scheduler()
    scheduler.start()
    logger.info(
        "Scheduler started — ingestion every %d min",
        settings.INGESTION_INTERVAL_MINUTES,
    )

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
