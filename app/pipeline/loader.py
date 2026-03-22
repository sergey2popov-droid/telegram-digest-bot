from app.core.dtos import ItemDTO
from app.db.repositories.item_repo import ItemRepo
from app.db.session import AsyncSessionFactory


async def load_recent() -> list[ItemDTO]:
    """Load all items fetched within the last 24 hours. Window is fixed — no expansion."""
    async with AsyncSessionFactory() as session:
        async with session.begin():
            return await ItemRepo(session).get_recent_24h()
