import logging

from app.core.dtos import ItemDTO
from app.pipeline.dedup import deduplicate
from app.pipeline.filter import filter_valid
from app.pipeline.loader import load_recent

logger = logging.getLogger(__name__)


async def run_pipeline() -> list[ItemDTO]:
    """
    Load items from the last 24 hours, filter invalid ones, deduplicate by topic.
    Returns empty list if no items pass — time window is never extended.
    """
    items = await load_recent()
    logger.info("Pipeline: loaded=%d", len(items))
    filtered = filter_valid(items)
    logger.info("Pipeline: after_filter=%d", len(filtered))
    result = deduplicate(filtered)
    logger.info("Pipeline: after_dedup=%d", len(result))
    return result
