from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dtos import DigestDTO, ItemDTO
from app.db.models.digest import Digest
from app.db.models.digest_item import DigestItem


class DigestRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, item_count: int) -> DigestDTO:
        digest = Digest(item_count=item_count)
        self._session.add(digest)
        await self._session.flush()
        await self._session.refresh(digest)
        return DigestDTO.model_validate(digest)

    async def add_items(self, digest_id: int, items: list[ItemDTO]) -> None:
        for position, item in enumerate(items, start=1):
            self._session.add(
                DigestItem(digest_id=digest_id, item_id=item.id, position=position)
            )
        await self._session.flush()

    async def get_last(self) -> DigestDTO | None:
        result = await self._session.execute(
            select(Digest).order_by(Digest.created_at.desc()).limit(1)
        )
        row = result.scalar_one_or_none()
        return DigestDTO.model_validate(row) if row else None
