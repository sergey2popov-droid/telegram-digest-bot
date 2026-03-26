from app.core.dtos import ItemDTO
from app.db.repositories.item_repo import ItemRepo
from app.db.session import AsyncSessionFactory
from app.ranking.scorer import compute_ranking_score, compute_score


class ScoringService:
    async def score(self, items: list[ItemDTO]) -> list[ItemDTO]:
        """
        Compute raw_score and final_score for each item, persist to DB,
        and return items sorted by final_score desc, then published_at desc.
        """
        scored: list[ItemDTO] = []

        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = ItemRepo(session)
                for item in items:
                    raw = compute_score(
                        reactions=0,
                        comments=0,
                        title=item.title or "",
                    )
                    final = compute_ranking_score(raw)
                    await repo.update_score(
                        item_id=item.id,
                        raw_score=raw,
                        final_score=final,
                    )
                    scored.append(item.model_copy(update={"raw_score": raw, "final_score": final}))

        scored.sort(key=lambda i: (i.final_score, i.published_at or i.fetched_at), reverse=True)
        return scored
