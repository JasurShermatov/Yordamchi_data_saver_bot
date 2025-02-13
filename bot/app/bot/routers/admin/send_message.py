from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import asyncio

from app.bot.constants.admin import SEND_MESSAGE
from app.bot.filters.admin import AdminFilter
from app.bot.handlers.admin.users import get_all_users
from app.bot.states.message_users import BroadcastStates

router = Router()


@router.message(AdminFilter(), F.text == SEND_MESSAGE)
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "✍️ Yubormoqchi bo'lgan xabaringizni yuboring.\n"
        "🔔 Barcha turdagi xabarlarni yuborishingiz mumkin "
        "(Matn, rasm, video, audio va boshqalar)\n\n"
        "❌ Bekor qilish uchun /cancel buyrug'ini yuboring."
    )
    await state.set_state(BroadcastStates.waiting_message)


@router.message(AdminFilter(), BroadcastStates.waiting_message)
async def process_broadcast(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi")
        return

    users = await get_all_users()
    all_users = len(users)

    status_msg = await message.answer(
        f"📤 Xabar yuborish boshlandi...\n\n📊 Jami foydalanuvchilar: {all_users} ta"
    )

    asyncio.create_task(send_messages(users, message, status_msg))

    await message.answer(
        "✅ Xabar fonda yuborilmoqda. Boshqa buyruqlardan foydalanishingiz mumkin."
    )
    await state.clear()


async def send_messages(users, message: Message, status_msg: Message):
    sent_count = 0
    failed_count = 0

    for user in users:
        try:
            await message.copy_to(user.user_id)
            sent_count += 1
        except Exception:
            failed_count += 1

        if (sent_count + failed_count) % 100 == 0:
            await status_msg.edit_text(
                f"📤 Xabar yuborilmoqda...\n\n✅ Yuborildi: {sent_count}\n❌ Yuborilmadi: {failed_count}"
            )

        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ Xabar yuborish yakunlandi!\n\n✅ Jami yuborildi: {sent_count}\n❌ Yuborilmadi: {failed_count}"
    )


@router.message(Command("cancel"), BroadcastStates.waiting_message)
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Xabar yuborish bekor qilindi")
