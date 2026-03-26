from app.core.dtos import ItemDTO
from app.pipeline.dedup import deduplicate
from app.pipeline.filter import filter_valid
from app.pipeline.loader import load_recent


async def run_pipeline() -> list[ItemDTO]:
    """
    Load items from the last 24 hours, filter invalid ones, deduplicate by topic.
    Returns empty list if no items pass — time window is never extended.
    """
    items = await load_recent()
    filtered = filter_valid(items)
    return deduplicate(filtered)
