from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.digest_service import DigestService

router = Router()
_service = DigestService()


@router.message(Command("digest"))
async def cmd_digest(message: Message) -> None:
    try:
        text = await _service.build()
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка при сборке дайджеста: {type(e).__name__}: {e}")
