from dataclasses import dataclass
from datetime import datetime, timezone

import io

import feedparser


@dataclass
class FeedEntry:
    guid: str
    title: str
    url: str
    published_at: datetime | None


def parse(raw: bytes) -> list[FeedEntry]:
    """Parse raw RSS/Atom bytes into a list of FeedEntry objects."""
    feed = feedparser.parse(io.BytesIO(raw))
    entries = []

    for entry in feed.entries:
        guid = entry.get("id") or entry.get("link") or ""
        title = (entry.get("title") or "").strip()
        url = entry.get("link") or ""

        if not guid or not title or not url:
            continue

        published_at = _parse_date(entry)
        entries.append(FeedEntry(guid=guid, title=title, url=url, published_at=published_at))

    return entries


def _parse_date(entry: dict) -> datetime | None:
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if struct is None:
        return None
    try:
        import calendar
        timestamp = calendar.timegm(struct)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except Exception:
        return None
