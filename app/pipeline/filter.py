from app.core.dtos import ItemDTO


def filter_valid(items: list[ItemDTO]) -> list[ItemDTO]:
    """Drop items missing title, url, or published_at."""
    return [
        item for item in items
        if item.title.strip()
        and item.url.strip()
        and item.published_at is not None
    ]
