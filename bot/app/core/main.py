import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.middlewares.subscribe import CheckSubscriptionMiddleware
from app.core.settings.config import get_settings, Settings

from app.bot.routers.admin.send_message import router as send_message_router
from app.bot.routers.start import router as start_router
from app.bot.routers.admin.admin import router as admin_router
from app.bot.routers.admin.channels import router as channels_router
from app.bot.routers.admin.category import router as category_router
from app.bot.routers.admin.files import router as data_router
from app.bot.routers.users.files import router as user_routers

settings: Settings = get_settings()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


def setup_handlers(dp: Dispatcher):
    middleware = CheckSubscriptionMiddleware()

    start_router.message.middleware(middleware)
    start_router.callback_query.middleware(middleware)

    dp.include_router(admin_router)
    dp.include_router(data_router)
    dp.include_router(category_router)
    dp.include_router(send_message_router)
    dp.include_router(channels_router)
    dp.include_router(user_routers)
    dp.include_router(start_router)
    os.makedirs("media/files", exist_ok=True)


async def main():
    dp = Dispatcher()

    setup_handlers(dp)

    try:
        logger.info("Bot ishga tushdi")
        await dp.start_polling(bot)
    except Exception as e_:
        logger.error(f"Bot ishga tushishida xatolik: {e_}")
    finally:
        await bot.session.close()
        logger.info("Bot va barcha resurslar to'xtatildi")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot administrativ tarzda to'xtatildi")
    except Exception as e:
        logger.error(f"Kutilmagan xatolik: {e}")
        sys.exit(1)
