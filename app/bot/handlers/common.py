from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

_HELP_TEXT = (
    "Команды:\n"
    "/digest — получить дайджест прямо сейчас\n"
    "/add_source <url> <name> — добавить RSS-источник\n"
    "/list_sources — список активных источников\n"
    "/remove_source <id> — удалить источник\n"
    "/myid — узнать свой chat_id\n"
    "/help — это сообщение"
)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Бот дайджеста запущен.\n\n" + _HELP_TEXT)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(_HELP_TEXT)


@router.message(Command("myid"))
async def cmd_myid(message: Message) -> None:
    await message.answer(f"Ваш chat_id: <code>{message.chat.id}</code>", parse_mode="HTML")
