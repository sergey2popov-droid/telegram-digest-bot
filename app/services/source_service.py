from urllib.parse import urlparse

from app.core.dtos import SourceDTO
from app.db.repositories.source_repo import SourceRepo
from app.db.session import AsyncSessionFactory


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


class SourceService:
    async def add_source(self, url: str, name: str) -> tuple[SourceDTO | None, str]:
        if not _is_valid_url(url):
            return None, "Invalid URL. Must start with http:// or https://"

        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = SourceRepo(session)
                existing = await repo.get_by_url(url)
                if existing:
                    return None, f"Source already exists: {existing.name} (id={existing.id})"
                source = await repo.add(url=url, name=name)

        return source, f"Source added: [{source.name}] id={source.id}"

    async def list_sources(self) -> list[SourceDTO]:
        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = SourceRepo(session)
                return await repo.get_all_active()

    async def remove_source(self, source_id: int) -> tuple[bool, str]:
        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = SourceRepo(session)
                removed = await repo.deactivate(source_id)

        if removed:
            return True, f"Source id={source_id} removed."
        return False, f"Source id={source_id} not found."
