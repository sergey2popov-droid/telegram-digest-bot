from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dtos import ItemDTO
from app.db.models.item import Item


class ItemRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_or_skip(
        self,
        source_id: int,
        guid: str,
        title: str,
        url: str,
        published_at: datetime | None,
    ) -> ItemDTO | None:
        existing = await self._session.execute(
            select(Item).where(Item.guid == guid)
        )
        if existing.scalar_one_or_none() is not None:
            return None

        item = Item(
            source_id=source_id,
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            raw_score=0.0,
            final_score=0.0,
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return ItemDTO.model_validate(item)

    async def get_recent_24h(self) -> list[ItemDTO]:
        cutoff_fetch = datetime.now(timezone.utc) - timedelta(hours=24)
        cutoff_publish = datetime.now(timezone.utc) - timedelta(days=3)
        result = await self._session.execute(
            select(Item).where(
                Item.fetched_at >= cutoff_fetch,
                (Item.published_at >= cutoff_publish) | (Item.published_at.is_(None)),
            )
        )
        return [ItemDTO.model_validate(row) for row in result.scalars().all()]

    async def update_score(
        self, item_id: int, raw_score: float, final_score: float
    ) -> None:
        result = await self._session.execute(
            select(Item).where(Item.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item is not None:
            item.raw_score = raw_score
            item.final_score = final_score
            await self._session.flush()
