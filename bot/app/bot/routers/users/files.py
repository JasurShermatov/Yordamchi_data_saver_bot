from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram import Bot
from app.core.settings.config import get_settings, Settings
from app.bot.handlers.admin.files import get_files_by_category_id


settings: Settings = get_settings()

bot = Bot(token=settings.BOT_TOKEN)

router = Router()


@router.callback_query(F.data.startswith("cat_"))
async def show_files_by_category(callback: CallbackQuery):
    category_id = int(callback.data.split("|")[1])
    files = await get_files_by_category_id(category_id)
    if not files:
        await callback.message.answer(
            "❌ Ushbu kategoriyada hozircha file mavjud emas!"
        )
        return
    for row in files:
        try:
            await bot.copy_message(
                chat_id=callback.message.chat.id,
                from_chat_id=settings.get_channel_id,
                message_id=row.message_id,
            )
        except Exception as e:
            await callback.message.answer(f"Nusxa olishda xatolik: {str(e)}")

    await callback.answer()
