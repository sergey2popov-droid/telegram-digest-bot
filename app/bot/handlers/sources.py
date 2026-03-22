from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.source_service import SourceService

router = Router()
_service = SourceService()


@router.message(Command("add_source"))
async def cmd_add_source(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Usage: /add_source <url> <name>")
        return

    _, url, name = parts
    _, reply = await _service.add_source(url=url, name=name)
    await message.answer(reply)


@router.message(Command("list_sources"))
async def cmd_list_sources(message: Message) -> None:
    sources = await _service.list_sources()
    if not sources:
        await message.answer("No active sources.")
        return

    lines = [f"id={s.id} [{s.type}] {s.name}\n{s.url}" for s in sources]
    await message.answer("\n\n".join(lines))


@router.message(Command("remove_source"))
async def cmd_remove_source(message: Message) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Usage: /remove_source <id>")
        return

    source_id = int(parts[1])
    _, reply = await _service.remove_source(source_id)
    await message.answer(reply)
