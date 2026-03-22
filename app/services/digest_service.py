from datetime import datetime


class DigestService:
    async def build(self, top_n: int = 5) -> str:
        from app.pipeline.runner import run_pipeline
        from app.services.scoring_service import ScoringService

        items = await run_pipeline()
        ranked = await ScoringService().score(items)
        top_items = ranked[:top_n]

        if not top_items:
            return "Пока нет новостей для дайджеста."

        lines = ["📰 Дайджест новостей", ""]

        for idx, item in enumerate(top_items, 1):
            title = self._trim(item.title)
            dt = self._format_dt(item.published_at)

            lines.append(f"{idx}. {title}")
            lines.append(f"🔗 {item.url}")
            lines.append(f"🕒 {dt}")
            lines.append("")

        return "\n".join(lines).strip()

    def _trim(self, text: str, limit: int = 110) -> str:
        if not text:
            return "Без заголовка"
        text = text.strip()
        return text if len(text) <= limit else text[:limit].rstrip() + "..."

    def _format_dt(self, value: datetime) -> str:
        return value.strftime("%d.%m %H:%M")
