from aiogram import Router

from app.bot.handlers import common, digest, sources

router = Router()

router.include_router(common.router)
router.include_router(sources.router)
router.include_router(digest.router)
