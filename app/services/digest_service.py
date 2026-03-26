from datetime import datetime

from app.core.constants import DIGEST_SIZE
from app.db.repositories.digest_repo import DigestRepo
from app.db.session import AsyncSessionFactory
from app.pipeline.runner import run_pipeline
from app.ranking.selector import select_top
from app.services.scoring_service import ScoringService


class DigestService:
    async def build(self) -> str:
        items = await run_pipeline()
        ranked = await ScoringService().score(items)
        top_items = select_top(ranked, n=DIGEST_SIZE)

        async with AsyncSessionFactory() as session:
            async with session.begin():
                repo = DigestRepo(session)
                digest = await repo.create(item_count=len(top_items))
                if top_items:
                    await repo.add_items(digest.id, top_items)

        if not top_items:
            return "Пока нет новостей для дайджеста."

        lines = ["📰 <b>Дайджест новостей о здоровье и ЗОЖ</b>", ""]

        for idx, item in enumerate(top_items, 1):
            title = self._trim(item.title)
            dt = self._format_dt(item.published_at)
            lines.append(f"{idx}. <a href=\"{item.url}\">{title}</a>")
            lines.append(f"🕒 {dt}")
            lines.append("")

        return "\n".join(lines).strip()

    def _trim(self, text: str, limit: int = 110) -> str:
        if not text:
            return "Без заголовка"
        text = text.strip()
        return text if len(text) <= limit else text[:limit].rstrip() + "..."

    def _format_dt(self, value: datetime | None) -> str:
        if not value:
            return "—"
        return value.strftime("%d.%m %H:%M")
