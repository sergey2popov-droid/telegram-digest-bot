from app.core.dtos import ItemDTO
from app.pipeline.filter import filter_valid
from app.pipeline.loader import load_recent


async def run_pipeline() -> list[ItemDTO]:
    """
    Load items from the last 24 hours and filter invalid ones.
    Returns empty list if no items pass — time window is never extended.
    """
    items = await load_recent()
    return filter_valid(items)
