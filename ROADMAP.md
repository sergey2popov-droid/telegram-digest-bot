# Telegram Digest Bot — Implementation Roadmap

> Single-user, modular monolith, RSS-only MVP.
> One phase at a time. Wait for approval before proceeding.

---

## Progress Checklist

- [x] Phase 0 — Project structure fix
- [x] Phase 1 — Database models and Alembic
- [x] Phase 2 — Repositories and DTOs
- [x] Phase 3 — Bot skeleton and settings
- [x] Phase 4 — Source management
- [x] Phase 5 — RSS ingestion
- [x] Phase 6 — Pipeline
- [x] Phase 7 — Scoring
- [ ] Phase 8 — Deduplication (skipped by user decision)
- [x] Phase 9 — Selector and digest builder
- [x] Phase 10 — Scheduler, logs, polish

---

## Phase 0 — Project structure fix

### Goal
Fix the project layout so it is a valid Python package hierarchy. No logic changes, no new features, no refactoring — structure only.

### Files to create or modify
| Action | File |
|--------|------|
| Delete | `app/app/` (misplaced duplicate directory) |
| Create | `app/__init__.py` |
| Create | `app/bot/__init__.py` |
| Create | `app/collectors/__init__.py` |
| Create | `app/collectors/rss/__init__.py` |
| Create | `app/db/__init__.py` |
| Create | `app/db/models/__init__.py` |
| Create | `app/db/repositories/__init__.py` |
| Create | `app/pipeline/__init__.py` |
| Create | `app/ranking/__init__.py` |
| Create | `app/services/__init__.py` |
| Create | `app/jobs/__init__.py` |
| Create | `app/core/__init__.py` |

### What will be implemented
- All layer directories become valid Python packages via `__init__.py`
- Misplaced `app/app/` directory removed
- No code changes to existing `.py` files
- No new logic, no config, no settings

### Completion criteria
- All package directories contain `__init__.py`
- `app/app/` no longer exists
- All existing files (`bot.py`, `main.py`) still run unchanged

### Verification commands
```bash
python -c "import app.bot; import app.db; import app.pipeline; import app.ranking; import app.services; import app.jobs; print('OK')"
```

---

## Phase 1 — Database models and Alembic

### Goal
Define all SQLAlchemy ORM models required for the MVP and set up Alembic migrations. First migration creates all tables.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/db/base.py` |
| Create | `app/db/models/source.py` |
| Create | `app/db/models/item.py` |
| Create | `app/db/models/digest.py` |
| Create | `app/db/models/digest_item.py` |
| Modify | `app/db/models/__init__.py` |
| Create | `alembic.ini` |
| Create | `migrations/env.py` |
| Create | `migrations/versions/0001_initial.py` |

### What will be implemented
- `Base` — SQLAlchemy declarative base
- `Source` — `id`, `url`, `name`, `type` (rss), `is_active`, `created_at`
- `Item` — `id`, `source_id`, `guid`, `title`, `url`, `published_at`, `raw_score`, `final_score`, `fetched_at`
- `Digest` — `id`, `created_at`, `sent_at`, `item_count`
- `DigestItem` — `id`, `digest_id`, `item_id`, `position`
- Alembic configured to read `DATABASE_URL` from environment
- Initial migration generates all four tables

### Completion criteria
- `alembic upgrade head` runs without error
- All four tables exist in the database
- Models importable without DB connection

### Verification commands
```bash
alembic upgrade head
psql $DATABASE_URL -c "\dt"
python -c "from app.db.models import Source, Item, Digest, DigestItem; print('OK')"
```

---

## Phase 2 — Repositories and DTOs

### Goal
Implement the data access layer. Repositories handle all DB reads and writes. DTOs carry data between layers without leaking ORM types.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/db/session.py` |
| Create | `app/db/repositories/source_repo.py` |
| Create | `app/db/repositories/item_repo.py` |
| Create | `app/db/repositories/digest_repo.py` |
| Create | `app/core/dtos.py` |
| Modify | `app/db/repositories/__init__.py` |

### What will be implemented
- `session.py` — async SQLAlchemy engine and session factory using `DATABASE_URL` from config
- `SourceRepo`: `add`, `get_all_active`, `get_by_url`, `deactivate`
- `ItemRepo`: `add_or_skip` (dedup by `guid`), `get_recent_24h`, `update_score`
- `DigestRepo`: `create`, `add_items`, `get_last`
- `SourceDTO`, `ItemDTO`, `DigestDTO` as pydantic models
- No SQLAlchemy types cross the repository boundary

### Completion criteria
- All repos importable
- DTOs are pure pydantic — no ORM model fields
- `ItemRepo.add_or_skip` does not insert duplicates for the same `guid`

### Verification commands
```bash
python -c "from app.db.repositories import SourceRepo, ItemRepo, DigestRepo; print('OK')"
python -c "from app.core.dtos import SourceDTO, ItemDTO, DigestDTO; print('OK')"
```

---

## Phase 3 — Bot skeleton and settings

### Goal
Refactor the bot into a clean routed structure with thin handlers and stub commands. No business logic inside handlers — handlers only parse input and call services (or return stubs).

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/core/config.py` |
| Create | `app/core/constants.py` |
| Modify | `app/core/.env.example` |
| Create | `app/bot/router.py` |
| Create | `app/bot/handlers/__init__.py` |
| Create | `app/bot/handlers/common.py` |
| Create | `app/bot/handlers/sources.py` |
| Create | `app/bot/handlers/digest.py` |
| Modify | `app/bot/bot.py` |
| Modify | `app/main.py` |

### What will be implemented
- `config.py` — `Settings` via `pydantic-settings`: `BOT_TOKEN`, `DATABASE_URL`, `TIMEZONE`
- `constants.py` — empty, reserved for Phase 7+ values
- `router.py` — central aiogram `Router`, includes all handler sub-routers
- `handlers/common.py` — `/start`, `/help` with a list of available commands
- `handlers/sources.py` — stub handlers: `/add_source`, `/list_sources`, `/remove_source` (return "not yet implemented")
- `handlers/digest.py` — stub handler: `/digest` (returns "not yet implemented")
- `bot.py` — refactored: create `Bot(token=settings.BOT_TOKEN)`, include router, start polling
- `main.py` — instantiate settings, call bot entry point
- No DB calls anywhere in this phase

### Completion criteria
- `/start` and `/help` respond with real text
- `/add_source`, `/list_sources`, `/remove_source`, `/digest` respond with stub text
- No business logic in any handler
- `BOT_TOKEN` loaded exclusively via `Settings`

### Verification commands
```bash
python app/main.py
# In Telegram: /start → real reply
# /help → command list
# /digest → stub reply
```

---

## Phase 4 — Source management

### Goal
Implement full source CRUD via bot commands, wired through the service layer to `SourceRepo`. DB must be running.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/services/source_service.py` |
| Modify | `app/bot/handlers/sources.py` |

### What will be implemented
- `SourceService`: `add_source(url, name) -> SourceDTO`, `list_sources() -> list[SourceDTO]`, `remove_source(source_id) -> bool`
- URL format validation before saving (reject non-http URLs)
- `/add_source <url> <name>` — calls service, confirms success or reports error
- `/list_sources` — calls service, formats list with IDs
- `/remove_source <id>` — calls service, confirms deactivation
- Handlers contain only: parse args → call service → format result → send

### Completion criteria
- `/add_source https://example.com/rss MyFeed` saves to DB and replies with confirmation
- `/list_sources` shows the saved source
- `/remove_source 1` deactivates it; subsequent `/list_sources` excludes it
- Invalid URL rejected with a clear error message

### Verification commands
```bash
python app/main.py
# /add_source https://feeds.bbcrussian.com/world/rss.xml BBC
# /list_sources
# /remove_source 1
psql $DATABASE_URL -c "SELECT id, url, is_active FROM sources;"
```

---

## Phase 5 — RSS ingestion

### Goal
Implement the RSS collector: fetch active sources, parse feed items, save new items to DB via `ItemRepo`. No scoring in this phase.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/collectors/rss/fetcher.py` |
| Create | `app/collectors/rss/parser.py` |
| Create | `app/services/ingestion_service.py` |

### What will be implemented
- `fetcher.py` — `async fetch(url: str) -> bytes` using `httpx`; raises on non-200; no retries in MVP
- `parser.py` — `parse(raw: bytes) -> list[dict]` using `feedparser`; extracts `guid`, `title`, `url`, `published_at`; no HTML parsing
- `ingestion_service.py` — `async run()`: get active sources → fetch each → parse → `ItemRepo.add_or_skip`; per-source errors are logged and skipped
- `raw_score` and `final_score` default to `0.0` at insert time
- Title and URL only — no content, no description, no HTML

### Completion criteria
- Running ingestion with a live RSS URL inserts items into `items` table
- Re-running does not create duplicate rows (guid dedup)
- A source returning 404 or timeout does not crash the process

### Verification commands
```bash
python -c "
import asyncio
from app.services.ingestion_service import IngestionService
asyncio.run(IngestionService().run())
"
psql $DATABASE_URL -c "SELECT id, title, url FROM items LIMIT 10;"
```

---

## Phase 6 — Pipeline

### Goal
Implement the pipeline: load items from the last 24 hours, filter invalid ones, return a clean list ready for scoring. Strictly 24-hour window — no fallback, no expansion.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/pipeline/loader.py` |
| Create | `app/pipeline/filter.py` |
| Create | `app/pipeline/runner.py` |

### What will be implemented
- `loader.py` — `async load() -> list[ItemDTO]`: calls `ItemRepo.get_recent_24h()`; window is exactly 24 hours, fixed
- `filter.py` — `filter_valid(items: list[ItemDTO]) -> list[ItemDTO]`: drops items where `title` is empty, `url` is empty, or `published_at` is missing
- `runner.py` — `async run_pipeline() -> list[ItemDTO]`: chains `load → filter_valid`, returns result
- No time window expansion if result is empty — returns empty list
- Pure functions in `filter.py`; only `loader.py` touches DB

### Completion criteria
- Items older than 24h are excluded
- Items with missing `title`, `url`, or `published_at` are excluded
- Empty result is returned as-is, no fallback logic

### Verification commands
```bash
python -c "
import asyncio
from app.pipeline.runner import run_pipeline
items = asyncio.run(run_pipeline())
print(f'Pipeline returned {len(items)} items')
"
```

---

## Phase 7 — Scoring

### Goal
Implement item scoring. Score is based purely on reactions and comments. No weights. Ranking score normalizes by item age.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/ranking/scorer.py` |
| Create | `app/services/scoring_service.py` |
| Modify | `app/core/constants.py` |

### What will be implemented
- `scorer.py` — two pure functions:
  - `compute_score(reactions: int, comments: int) -> float` → `reactions + comments`
  - `compute_ranking_score(score: float, age_hours: float) -> float` → `score / age_hours` (age_hours floored at 1 to avoid division by zero)
- `scoring_service.py` — takes `list[ItemDTO]`, computes `raw_score` and `final_score` (= `ranking_score`) for each, writes back via `ItemRepo.update_score`
- For RSS MVP items: `reactions=0`, `comments=0` → `raw_score=0`, `final_score=0`; ordering falls back to `published_at`
- No configurable weights; formulas are fixed

### Completion criteria
- `compute_score(10, 3)` returns `13`
- `compute_ranking_score(13, 2.0)` returns `6.5`
- `compute_ranking_score(13, 0.5)` returns `13.0` (age floored at 1h)
- `final_score` is updated in DB after scoring run

### Verification commands
```bash
python -c "
from app.ranking.scorer import compute_score, compute_ranking_score
assert compute_score(10, 3) == 13
assert compute_ranking_score(13, 2.0) == 6.5
assert compute_ranking_score(13, 0.5) == 13.0
print('OK')
"
psql $DATABASE_URL -c "SELECT id, raw_score, final_score FROM items ORDER BY final_score DESC LIMIT 5;"
```

---

## Phase 8 — Deduplication

### Goal
Remove near-duplicate items from the scored list before selection. Uses fuzzy title matching via `rapidfuzz`. When duplicates found, keep the item with the higher `final_score`.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/pipeline/dedup.py` |
| Modify | `app/pipeline/runner.py` |
| Modify | `app/core/constants.py` |

### What will be implemented
- `dedup.py` — `deduplicate(items: list[ItemDTO], threshold: int) -> list[ItemDTO]`:
  - Pairwise title comparison using `rapidfuzz.fuzz.ratio`
  - Items exceeding threshold are considered duplicates; keep higher `final_score`
  - O(n²) acceptable for MVP (< 200 items expected)
- `runner.py` updated: `load → filter_valid → deduplicate → return`
- `DEDUP_THRESHOLD = 85` added to `constants.py`

### Completion criteria
- Two items with near-identical titles → only one survives
- The item with higher `final_score` is kept
- Threshold comes from `constants.py`, not hardcoded

### Verification commands
```bash
python -c "
from app.pipeline.dedup import deduplicate
from app.core.dtos import ItemDTO
from datetime import datetime, timezone
a = ItemDTO(id=1, source_id=1, guid='a', title='Breaking news today', url='http://a.com', published_at=datetime.now(timezone.utc), raw_score=5.0, final_score=5.0, fetched_at=datetime.now(timezone.utc))
b = ItemDTO(id=2, source_id=1, guid='b', title='Breaking news today!', url='http://b.com', published_at=datetime.now(timezone.utc), raw_score=2.0, final_score=2.0, fetched_at=datetime.now(timezone.utc))
result = deduplicate([a, b], threshold=85)
assert len(result) == 1
assert result[0].id == 1
print('OK')
"
```

---

## Phase 9 — Selector and digest builder

### Goal
Select top-N items from the deduplicated scored list, persist a `Digest` record, format a Telegram message, and wire the `/digest` command end-to-end.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/ranking/selector.py` |
| Create | `app/services/digest_service.py` |
| Modify | `app/bot/handlers/digest.py` |
| Modify | `app/core/constants.py` |

### What will be implemented
- `selector.py` — `select_top(items: list[ItemDTO], n: int) -> list[ItemDTO]`: sort by `final_score` desc, then `published_at` desc; take first `n`
- `digest_service.py` — `async build() -> str`:
  1. `run_pipeline()` → scored and deduped items
  2. `scoring_service.score(items)`
  3. `selector.select_top(items, n=DIGEST_SIZE)`
  4. `DigestRepo.create()` + `DigestRepo.add_items()`
  5. Return formatted message string
- Formatter: numbered list, item title as Telegram hyperlink, source name, time since published
- If no items: return a clear "no items available" string
- `/digest` handler: calls `DigestService.build()`, sends result — no logic in handler
- `DIGEST_SIZE = 10` added to `constants.py`

### Completion criteria
- `/digest` sends a real formatted message with real items
- `Digest` and `DigestItem` rows are created in DB after each `/digest` call
- Empty digest returns "no items available" message, no crash
- Handler contains no business logic

### Verification commands
```bash
python app/main.py
# In Telegram: /digest → formatted numbered list
psql $DATABASE_URL -c "SELECT * FROM digests ORDER BY created_at DESC LIMIT 1;"
psql $DATABASE_URL -c "SELECT * FROM digest_items ORDER BY position LIMIT 10;"
```

---

## Phase 10 — Scheduler, logs, polish

### Goal
Automate ingestion and digest delivery via APScheduler. Add structured logging. Finalize docker-compose, `.env.example`, and remove all remaining stubs.

### Files to create or modify
| Action | File |
|--------|------|
| Create | `app/jobs/scheduler.py` |
| Create | `app/jobs/ingestion_job.py` |
| Create | `app/jobs/digest_job.py` |
| Create | `app/core/logging.py` |
| Modify | `app/main.py` |
| Modify | `app/core/docker-compose.yml` |
| Modify | `app/core/.env.example` |

### What will be implemented
- `ingestion_job.py` — runs `IngestionService.run()` every 30 minutes
- `digest_job.py` — runs `DigestService.build()` and sends result at 08:00 and 18:00 Moscow time
- `scheduler.py` — configures APScheduler with both jobs; timezone from `Settings.TIMEZONE`
- `logging.py` — structured logging with timestamp, level, module name
- `main.py` — starts scheduler and bot polling concurrently
- `docker-compose.yml` — Postgres 16 with named volume and healthcheck
- `.env.example` — every key documented with description and example value
- All stub handler responses replaced or removed

### Completion criteria
- Bot starts with scheduler running concurrently (visible in logs)
- Ingestion job fires every 30 min (logged)
- Digest job fires at scheduled times and sends message to user
- `docker compose up -d` gives a working Postgres
- `.env.example` is complete and self-documenting
- No "not yet implemented" stubs remain

### Verification commands
```bash
docker compose -f app/core/docker-compose.yml up -d
alembic upgrade head
python app/main.py
# Observe logs: ingestion job ticks, digest at scheduled time
# /digest still works manually
```

---

## Architecture summary

```
app/
  core/         # config, constants, dtos, logging
  bot/          # router + thin handlers only
  collectors/   # rss fetcher + parser
  pipeline/     # loader, filter, dedup, runner
  ranking/      # scorer, selector
  services/     # orchestration (source, ingestion, scoring, digest)
  db/           # base, models, session, repositories
  jobs/         # scheduler + job definitions
  main.py       # entry point
```

**Data flow:**
```
APScheduler
  → IngestionService → fetcher → parser → ItemRepo.add_or_skip
  → DigestService → pipeline.runner → scoring_service → selector → DigestRepo → format → Bot.send
```
