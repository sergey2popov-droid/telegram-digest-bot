from app.core.dtos import ItemDTO


def select_top(items: list[ItemDTO], n: int) -> list[ItemDTO]:
    """Return the top-n items. Items must already be sorted by ranking score desc."""
    return items[:n]
