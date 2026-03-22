import logging

from app.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)


async def run_ingestion() -> None:
    logger.info("Ingestion job started")
    try:
        results = await IngestionService().run()
        total = sum(results.values())
        logger.info("Ingestion job finished: %d new items across %d sources", total, len(results))
    except Exception:
        logger.exception("Ingestion job failed")
