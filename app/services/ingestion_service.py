import logging

from app.collectors.rss.fetcher import fetch
from app.collectors.rss.parser import parse
from app.db.repositories.item_repo import ItemRepo
from app.db.repositories.source_repo import SourceRepo
from app.db.session import AsyncSessionFactory

logger = logging.getLogger(__name__)


class IngestionService:
    async def run(self) -> dict[str, int]:
        """
        Fetch and ingest all active RSS sources.
        Returns a summary: {source_name: items_added}.
        Per-source errors are logged and skipped.
        """
        summary: dict[str, int] = {}

        async with AsyncSessionFactory() as session:
            async with session.begin():
                sources = await SourceRepo(session).get_all_active()

        for source in sources:
            try:
                raw = await fetch(source.url)
                entries = parse(raw)

                added = 0
                async with AsyncSessionFactory() as session:
                    async with session.begin():
                        repo = ItemRepo(session)
                        for entry in entries:
                            result = await repo.add_or_skip(
                                source_id=source.id,
                                guid=entry.guid,
                                title=entry.title,
                                url=entry.url,
                                published_at=entry.published_at,
                            )
                            if result is not None:
                                added += 1

                summary[source.name] = added
                logger.info("Ingested source=%r added=%d", source.name, added)

            except Exception as exc:
                logger.error("Failed to ingest source=%r: %s", source.name, exc)
                summary[source.name] = 0

        return summary
