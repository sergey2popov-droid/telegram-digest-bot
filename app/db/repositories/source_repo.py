from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dtos import SourceDTO
from app.db.models.source import Source


class SourceRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, url: str, name: str) -> SourceDTO:
        source = Source(url=url, name=name, type="rss", is_active=True)
        self._session.add(source)
        await self._session.flush()
        await self._session.refresh(source)
        return SourceDTO.model_validate(source)

    async def get_all_active(self) -> list[SourceDTO]:
        result = await self._session.execute(
            select(Source).where(Source.is_active == True)  # noqa: E712
        )
        return [SourceDTO.model_validate(row) for row in result.scalars().all()]

    async def get_by_url(self, url: str) -> SourceDTO | None:
        result = await self._session.execute(
            select(Source).where(Source.url == url)
        )
        row = result.scalar_one_or_none()
        return SourceDTO.model_validate(row) if row else None

    async def deactivate(self, source_id: int) -> bool:
        result = await self._session.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()
        if source is None:
            return False
        source.is_active = False
        await self._session.flush()
        return True
