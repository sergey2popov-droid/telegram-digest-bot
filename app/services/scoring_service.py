from datetime import datetime, timezone

from app.core.dtos import ItemDTO
from app.db.repositories.item_repo import ItemRepo
from app.db.session import AsyncSessionFactory
from app.ranking.scorer import compute_ranking_score, compute_score


def _age_hours(item: ItemDTO) -> float:
    """Hours since item was published. Falls back to fetched_at if published_at is None."""
    reference = item.published_at or item.fetched_at
    delta = datetime.now(timezone.utc) - reference
    return delta.total_seconds() / 3600


class ScoringService:
    async def score(self, items: list[ItemDTO]) -> list[ItemDTO]:
        """
        Compute raw_score and final_score for each item, persist to DB,
        and return items sorted by final_score desc, then published_at desc.

        For RSS MVP items reactions=0 and comments=0, so raw_score=0
        and final_score=0 — ordering falls back to published_at.
        """
        scored: list[ItemDTO] = []

        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = ItemRepo(session)
                for item in items:
                    raw = compute_score(reactions=0, comments=0)
                    age = _age_hours(item)
                    final = compute_ranking_score(raw, age)
                    await repo.update_score(
                        item_id=item.id,
                        raw_score=raw,
                        final_score=final,
                    )
                    scored.append(item.model_copy(update={"raw_score": raw, "final_score": final}))

        scored.sort(key=lambda i: (i.final_score, i.published_at or i.fetched_at), reverse=True)
        return scored
