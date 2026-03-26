import re

from rapidfuzz import fuzz

from app.core.dtos import ItemDTO

DEDUP_RATIO_THRESHOLD = 38


def _content_stems(title: str) -> set[str]:
    """Extract 4-char stems of words with 4+ characters."""
    return {t[:4] for t in re.split(r"[^\w]", title.lower()) if len(t) >= 4}


def _are_duplicates(a: str, b: str) -> bool:
    if fuzz.token_set_ratio(a, b) < DEDUP_RATIO_THRESHOLD:
        return False
    return bool(_content_stems(a) & _content_stems(b))


def deduplicate(items: list[ItemDTO]) -> list[ItemDTO]:
    """
    Remove topically similar articles.
    Two articles are duplicates if token_set_ratio >= threshold AND they share
    at least one significant word stem. From each group keeps the longest title.
    """
    kept: list[ItemDTO] = []

    for item in items:
        merged = False
        for i, existing in enumerate(kept):
            if _are_duplicates(item.title, existing.title):
                if len(item.title) > len(existing.title):
                    kept[i] = item
                merged = True
                break
        if not merged:
            kept.append(item)

    return kept
