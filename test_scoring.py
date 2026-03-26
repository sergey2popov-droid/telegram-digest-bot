import asyncio

from app.pipeline.runner import run_pipeline
from app.services.scoring_service import ScoringService


async def main():
    items = await run_pipeline()
    ranked = await ScoringService().score(items)

    print(f"Ranked {len(ranked)} items")

    for i in ranked[:5]:
        print(f"score={i.final_score:.4f} | {i.published_at} | {i.title}")


asyncio.run(main())