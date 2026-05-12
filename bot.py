"""
🎬 Kino Bot — Aiogram v3 versiyasi
Ishga tushirish: python bot.py
"""
import asyncio
import logging
import traceback
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import load_config
from utils.database import Database
from middlewares.subscription_middleware import SubscriptionMiddleware
from handlers.admin_handlers import router as admin_router
from handlers.developer_handlers import router as dev_router
from handlers.guide_handlers import router as guide_router
from handlers.user_handlers import router as user_router

# ─────────────────── LOGGING ───────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, config, db: Database):
    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    await db.init()
    logger.info(f"📁 Data papkasi: {config.DATA_DIR}")

    me = await bot.get_me()
    logger.info(f"🤖 Bot ishga tushdi: @{me.username} (ID: {me.id})")
    logger.info(f"👮 Adminlar: {config.ADMIN_IDS}")

    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"✅ <b>Bot ishga tushdi!</b>\n\n"
                f"🤖 @{me.username}\n"
                f"📁 Data: <code>{config.DATA_DIR}</code>\n\n"
                f"🛠 Admin panel: /admin",
            )
        except Exception as e:
            logger.warning(f"Admin {admin_id} ga xabar yuborilmadi: {e}")


async def main():
    config = load_config()
    db = Database(config.DATA_DIR)

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Middleware — majburiy obuna
    sub_middleware = SubscriptionMiddleware(bot, db, config)
    dp.message.outer_middleware(sub_middleware)
    dp.callback_query.outer_middleware(sub_middleware)

    # Routerlarni qo'shish (tartib muhim!)
    # admin, dev, guide — avval (aniq handlerlar)
    # user — oxirida (catch-all state=None handler)
    dp.include_router(admin_router)
    dp.include_router(dev_router)
    dp.include_router(guide_router)
    dp.include_router(user_router)

    # Global xato handler
    @dp.errors()
    async def error_handler(event: ErrorEvent):
        tb = traceback.format_exc()
        logger.error(f"Global xatolik: {event.exception}\n{tb}")

        if not config.DEVELOPER_ID:
            return

        text = (
            "❌ <b>Xatolik yuz berdi!</b>\n\n"
            f"🛠 <b>Xato turi:</b> <code>{type(event.exception).__name__}</code>\n"
            f"📝 <b>Xabar:</b> <code>{str(event.exception)}</code>\n\n"
            f"📜 <b>Traceback:</b>\n<pre>{tb[-3000:]}</pre>"
        )
        try:
            await bot.send_message(config.DEVELOPER_ID, text)
        except Exception as e:
            logger.error(f"Developerga xabar yuborib bo'lmadi: {e}")

    await on_startup(bot, config, db)

    logger.info("🚀 Polling boshlandi...")
    await dp.start_polling(bot, db=db, config=config, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
