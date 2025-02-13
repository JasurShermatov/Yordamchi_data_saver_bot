from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.constants.admin import ADD_CATEGORY, REMOVE_CATEGORY, CATEGORY_LIST
from app.bot.filters.admin import AdminFilter
from app.bot.handlers.admin.category import create_category
from app.bot.keyboards.inline.category import (
    delete_category_button,
    get_category_keyboard,
)
from app.bot.states.category import CategoryCreateState
from app.bot.handlers.admin.category import delete_category

router = Router()


@router.message(AdminFilter(), F.text == ADD_CATEGORY)
async def add_category(message: Message, state: FSMContext):
    await message.answer(
        "<b>📂 Yangi kategoriya qo‘shish</b>\n\n"
        "Kategoriya nomini yozing va botga yuboring.\n\n"
        "🔹 <b>Misol:</b> <code>📁 Ish rejalar</code>\n\n"
        "✍️ <b>Yozish tartibi:</b> Faqat nomni yozing, bot avtomatik ravishda qo‘shadi.\n"
        "✅ <i>Masalan:</i> <code>📁 Dasturlash</code>"
    )
    await state.set_state(CategoryCreateState.name_for_category)


@router.message(CategoryCreateState.name_for_category)
async def process_add_category(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        result = await create_category(name=name)
        if result:
            await message.answer(
                f"✅ <b>{name.upper()}</b> nomli kategoriya muvaffaqiyatli qo'shildi!"
            )
        else:
            await message.answer("❌ Ushbu kategoriya allaqachon mavjud!")
        await state.clear()
    except ValueError as e:
        await message.answer(f"⚠️ Xatolik: {e}")
    except Exception as e:
        await message.answer(f"❌ Noma'lum xatolik yuz berdi: {e}")


@router.message(AdminFilter(), F.text == REMOVE_CATEGORY)
async def remove_category(message: Message):
    categories = await delete_category_button()
    if not categories:
        await message.answer("📂 Hozircha hech qanday kategoriya yo'q.")
        return
    await message.answer(
        "🗑 O‘chirish uchun kerakli kategoriyani tanlang:",
        reply_markup=categories,
    )


@router.callback_query(F.data.startswith("delete_category:"))
async def delete_category_handler(callback: CallbackQuery):
    try:
        await delete_category(int(callback.data.split(":")[-1]))
        await callback.message.answer("✅ Kategoriya muvaffaqiyatli o‘chirildi!")
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik yuz berdi: {e}")

    categories = await delete_category_button()
    if not categories:
        await callback.message.answer("📂 Barcha kategoriyalar o‘chirildi.")
        return

    await callback.message.edit_text(
        "🗑 O‘chirish uchun kategoriya tanlang:",
        reply_markup=categories,
    )


@router.message(AdminFilter(), F.text == CATEGORY_LIST)
async def list_categories(message: Message):
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    categories = await get_category_keyboard()
    if not categories:
        await message.answer("📂 Hozircha hech qanday kategoriya yo'q.")
        return
    await message.answer(
        "Quyidagi tugmalardan birini tanlab, kerakli bo‘limga kirishingiz mumkin. 👇",
        reply_markup=await get_category_keyboard(),
    )
