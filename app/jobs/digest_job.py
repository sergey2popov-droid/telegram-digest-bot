import logging

from aiogram import Bot

from app.core.config import settings
from app.services.digest_service import DigestService

logger = logging.getLogger(__name__)


async def run_digest() -> None:
    logger.info("Digest job started")
    try:
        text = await DigestService().build()
        bot = Bot(token=settings.BOT_TOKEN)
        try:
            await bot.send_message(
                chat_id=settings.CHAT_ID,
                text=text,
                parse_mode="HTML",
            )
            logger.info("Digest sent to chat_id=%s", settings.CHAT_ID)
        finally:
            await bot.session.close()
    except Exception:
        logger.exception("Digest job failed")
