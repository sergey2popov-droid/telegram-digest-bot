from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

_HELP_TEXT = (
    "Available commands:\n"
    "/start — welcome message\n"
    "/help — show this list\n"
    "/add_source <url> <name> — add an RSS source\n"
    "/list_sources — list active sources\n"
    "/remove_source <id> — remove a source\n"
    "/digest — generate and send digest"
)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Hello! Digest bot is running.\n\n" + _HELP_TEXT)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(_HELP_TEXT)
