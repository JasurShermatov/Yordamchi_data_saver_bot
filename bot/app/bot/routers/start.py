from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.bot.handlers.admin.users import create_or_update_user
from app.bot.keyboards.inline.category import get_category_keyboard_cat
from app.bot.keyboards.inline.channels import (
    get_channel_keyboard as get_subscribe_channels,
)
from app.core.middlewares.subscribe import CheckSubscriptionMiddleware

router = Router()

check_sub_middleware = CheckSubscriptionMiddleware()


@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id

    await create_or_update_user(message)

    missing_channels = await check_sub_middleware.check_all_subscriptions(
        user_id=user_id, bot=message.bot
    )

    if missing_channels:
        keyboard = await get_subscribe_channels(missing_channels)
        await message.answer(
            f"📢 Iltimos, quyidagi {len(missing_channels)} ta kanalga obuna bo‘ling:",
            reply_markup=keyboard,
        )
    else:
        keyboard = await get_category_keyboard_cat()
        if not keyboard:
            await message.answer("<b>Kategoriyalar topilmadi!</b>")
            return
        await message.answer(
            "<b>📂 Mavjud bo‘limlar ro‘yxati</b>\n\n"
            "Quyidagi tugmalardan birini tanlab,\nkerakli bo‘limga kirishingiz mumkin👇",
            reply_markup=keyboard,
        )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    missing_channels = await check_sub_middleware.check_all_subscriptions(
        user_id=callback.from_user.id, bot=callback.bot
    )

    if missing_channels:
        keyboard = await get_subscribe_channels(missing_channels)
        await callback.message.edit_text(
            f"📢 Yana {len(missing_channels)} ta kanalga obuna bo'lishingiz kerak:",
            reply_markup=keyboard,
        )
        await callback.answer(
            f"Siz hali {len(missing_channels)} ta kanalga obuna bo'lmagansiz!",
            show_alert=True,
        )
    else:
        await show_main_menu(callback.message)


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "<b>ℹ️ Yordam bo‘limi</b>\n\n"
        "📌 <b>/start</b> — Botni ishga tushirish\n"
        "📌 <b>/help</b> — Yordam bo‘limi\n\n"
        "📂 Ushbu bot orqali mavjud kategoriyalar ichidagi ma’lumotlarni "
        "oson topishingiz va yuklab olishingiz mumkin.\n\n"
        "❓ Savollaringiz bo‘lsa, <a href='https://t.me/Shermatov_J05'>administrator</a> bilan bog‘laning."
    )


async def show_main_menu(message: Message):
    keyboard = await get_category_keyboard_cat()
    if not keyboard:
        await message.answer("<b>Kategoriyalar topilmadi!</b>")
        return
    await message.answer(
        "<b>📂 Mavjud bo‘limlar ro‘yxati</b>\n\n"
        "Quyidagi tugmalardan birini tanlab,\nkerakli bo‘limga kirishingiz mumkin👇",
        reply_markup=keyboard,
    )


@router.message()
async def unknown_command(message: Message):
    await message.answer(
        "❌ <b>Noto‘g‘ri buyruq kiritdingiz!</b>\n\n"
        "🔄 Iltimos, <b>/start</b> buyrug‘ini bosing\n"
        "🔄 Yoki, <b>/help</b> buyrug‘ini bosing, yordam olish uchun.",
    )
