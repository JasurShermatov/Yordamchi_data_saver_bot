from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.bot.constants.admin import ADD_CHANNEL, CHANNEL_LIST, REMOVE_CHANNEL
from app.bot.filters.admin import AdminFilter
from app.bot.handlers.admin.channels import create_channels
from app.bot.keyboards.inline.channels import (
    get_channel_keyboard,
    get_delete_channel_keyboard,
    get_channel_keyboard_nd,
)
from app.bot.states.channels import ChannelStates
from app.bot.handlers.admin.channels import delete_channel as delete_channel_by_id

router = Router()


@router.message(AdminFilter(), F.text == CHANNEL_LIST)
async def get_channels(message: Message):
    buttons = await get_channel_keyboard_nd()
    await message.answer("Barcha kanallar ro'yxati!\n", reply_markup=buttons)


@router.message(AdminFilter(), F.text == ADD_CHANNEL)
async def add_channel(message: Message, state: FSMContext):
    await message.answer(
        "📢 <b>Kanal qo'shish uchun quyidagi formatda ma'lumot kiriting:</b>\n\n"
        "🔹 <code>nom|link|ID</code>\n\n"
        "📝 <b>Misol uchun:</b>\n"
        "<code>myKanal|https://t.me/mykanaluz|-1001234567890</code>\n\n"
        "❗️ <b>Diqqat:</b> Link to'g'ri formatda bo'lishi shart.\n"
        "✅ Faqat <b>https://t.me/</b> bilan boshlanuvchi linklarni kiritish mumkin.\n"
        "🔹 Kanal ID ni olish uchun: <code>@username</code> ni kanalga yuboring va `/id` botidan foydalaning."
    )
    await state.set_state(ChannelStates.add_channel)


@router.message(ChannelStates.add_channel)
async def process_add_channel(message: Message, state: FSMContext):
    try:
        data = message.text.split("|")
        if len(data) != 3:
            raise ValueError(
                "❌ Noto‘g‘ri format! To‘g‘ri format: <code>nom|link|ID</code> bo‘lishi kerak"
            )
        name, link, channel_id = data
        name, link, channel_id = name.strip(), link.strip(), channel_id.strip()
        if not channel_id.lstrip("-").isdigit():
            raise ValueError(
                "❌ Kanal ID noto‘g‘ri! ID faqat sonlardan iborat bo‘lishi kerak."
            )

        channel_id = int(channel_id)

        result = await create_channels(name=name, link=link, channel_id=channel_id)
        await message.answer(f"✅ {result}")

    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    finally:
        await state.clear()


@router.message(AdminFilter(), F.text == REMOVE_CHANNEL)
async def delete_channel(message: Message):
    keyboard = await get_delete_channel_keyboard()
    if not keyboard:
        await message.answer("❌ Bazada kanallar mavjud emas!")
        return

    await message.answer(
        "🗑 O'chirmoqchi bo'lgan kanalingizni tanlang:", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("delete_channel:"))
async def process_delete_channel(callback: CallbackQuery):
    channel_id = int(callback.data.split(":")[1])
    try:
        await delete_channel_by_id(channel_id)
        await callback.message.answer(
            "✅ Kanal muvaffaqiyatli o‘chirildi!", show_alert=True
        )
    except Exception as e:
        await callback.answer(f"❌ Xatolik yuz berdi: {e}", show_alert=True)

    new_keyboard = await get_delete_channel_keyboard()
    if new_keyboard:
        await callback.message.edit_text(
            "🗑 O'chirmoqchi bo'lgan kanalingizni tanlang:", reply_markup=new_keyboard
        )
    else:
        await callback.message.edit_text("✅ Barcha kanallar o‘chirildi!")
