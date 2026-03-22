# Project rules

## Product scope
- This is a single-user Telegram digest bot.
- Do not introduce SaaS, multi-tenancy, billing, or web admin panel.
- Do not introduce AI summarization or AI categorization.

## Architecture
- Keep the project as a modular monolith.
- Business logic must not live in bot handlers.
- Use layers: bot, collectors, pipeline, ranking, services, db, jobs, core.
- Telethon is allowed only inside app/collectors/telegram.
- Use repository layer for DB access.
- Use service layer for orchestration.

## Sources
- Telegram delivery via Bot API.
- Sites via RSS only for MVP.
- Do not add HTML parsing for sites unless explicitly requested.
- Do not depend on Telegram client API for MVP startup.

## Ranking
- Use only reactions and comments.
- Do not use views in MVP.
- Use 24-hour time window only.
- Do not expand the time window if content is insufficient.

## Workflow
- Never implement multiple roadmap steps at once.
- Always wait for approval before starting the next step.
- When finishing a step, update ROADMAP.md.
- Keep files small and readable.
- Prefer explicit code over clever code.

## Safety
- Never hardcode secrets.
- Use .env / settings only.
- Do not expose secrets in logs or bot responses.
