import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext

from app.bot.filters.admin import AdminFilter
from app.bot.handlers.admin.files import get_files_by_category_id
from app.bot.states.files import FileCreateState, FileDeleteState
from app.bot.constants.admin import ADD_DATA, REMOVE_DATA
from app.bot.keyboards.inline.category import get_category_keyboard_cat
from app.bot.handlers.admin.category import get_category_by_id, get_all_categories
from app.core.database.postgres import get_session
from app.bot.models.files import Files
from app.core.settings.config import get_settings
from aiogram import Bot

settings = get_settings()
bot = Bot(token=settings.BOT_TOKEN)

router = Router()


@router.message(AdminFilter(), F.text == ADD_DATA)
async def cmd_add_data(message: Message, state: FSMContext):
    await message.answer(
        "📂 <b>Fayllarni yuboring!</b>\n\n"
        "📌 <i>Ruxsat etilgan formatlar:</i> <b>doc, photo, video, audio</b>\n"
        "📌 Bitta yoki bir nechta fayl yuborishingiz mumkin.\n\n"
        "✍️ <b>Matn (caption) qo'shmoqchimisiz?</b>\n"
        "Har bir faylni alohida matn bilan yuboring.\n\n"
        "✅ Barcha fayllarni jo'natib bo'lgach, <b>/done</b> yozing deb yuboring."
    )
    await state.set_state(FileCreateState.waiting_for_files)
    await state.update_data(file_data=[])


@router.message(
    AdminFilter(),
    FileCreateState.waiting_for_files,
    F.text.in_(["/done", "done", "Tugadi", "tamom"]),
)
async def finish_uploading(message: Message, state: FSMContext):
    data = await state.get_data()
    file_list = data.get("file_data", [])
    if not file_list:
        await message.answer("📌Siz hali hech qanday fayl yubormadingiz.")
        return

    categories = await get_all_categories()
    if not categories:
        await message.answer(
            "❌ Hech qanday kategoriya topilmadi. Avval kategoriya qo'shing."
        )
        await state.clear()
        return

    keyboard = await get_category_keyboard_cat()
    await message.answer(
        f"Jami <b>{len(file_list)}</b> ta fayl qabul qilindi.\n"
        "Endi kategoriyani tanlang:",
        reply_markup=keyboard,
    )
    await state.set_state(FileCreateState.waiting_for_category)


@router.message(AdminFilter(), FileCreateState.waiting_for_files)
async def receive_files(message: Message, state: FSMContext):
    data = await state.get_data()
    file_list = data.get("file_data", [])

    file_info = None

    if message.document:
        file_info = {
            "file_id": message.document.file_id,
            "file_type": "document",
            "file_name": message.document.file_name or "Document",
        }
    elif message.photo:
        file_info = {
            "file_id": message.photo[-1].file_id,
            "file_type": "photo",
            "file_name": "Photo",
        }
    elif message.video:
        file_info = {
            "file_id": message.video.file_id,
            "file_type": "video",
            "file_name": message.video.file_name or "Video",
        }
    elif message.audio:
        file_info = {
            "file_id": message.audio.file_id,
            "file_type": "audio",
            "file_name": message.audio.file_name or "Audio",
        }
    elif message.voice:
        file_info = {
            "file_id": message.voice.file_id,
            "file_type": "voice",
            "file_name": "Voice",
        }
    elif message.video_note:
        file_info = {
            "file_id": message.video_note.file_id,
            "file_type": "video_note",
            "file_name": "VideoNote",
        }
    elif message.text:
        return
    else:
        await message.answer("❌ Noma'lum turdagi xabar. Qayta yuboring.")
        return

    if message.caption:
        file_info["file_name"] = message.caption

    file_list.append(file_info)
    await state.update_data(file_data=file_list)

    await message.answer(
        f"✅ Qabul qilindi. Hozircha {len(file_list)} ta fayl saqlandi.\n"
        "Yana yuboring yoki /done deb yakunlang."
    )


@router.callback_query(AdminFilter(), FileCreateState.waiting_for_category)
async def select_category(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split("|")
        category_id = int(data_parts[1])

        category_obj = await get_category_by_id(category_id)
        if not category_obj:
            await callback.answer("❌ Kategoriya topilmadi", show_alert=True)
            return

        data = await state.get_data()
        file_list = data.get("file_data", [])

        # Get current files count in the category
        async with get_session() as session:
            current_files = await get_files_by_category_id(category_id)
            initial_count = len(current_files) if current_files else 0

        message_ids = []
        success_count = 0

        for f in file_list:
            try:
                mid = await send_to_channel(
                    file_id=f["file_id"],
                    file_type=f["file_type"],
                    file_name=f["file_name"],
                    category_name=category_obj.name,
                )
                message_ids.append((f["file_name"], mid))
                success_count += 1
            except Exception as e:
                logging.error(f"Error sending file {f['file_name']}: {str(e)}")
                continue

        async with get_session() as session:
            for f_name, mid in message_ids:
                new_file = Files(name=f_name, category_id=category_id, message_id=mid)
                session.add(new_file)
            await session.commit()

        # Get new files count
        final_files = await get_files_by_category_id(category_id)
        final_count = len(final_files) if final_files else 0
        added_count = final_count - initial_count

        await callback.message.answer(
            f"✅ <b>{success_count}</b> ta fayl <b>{category_obj.name}</b> kategoriyasiga "
            f"muvaffaqiyatli qo'shildi!\n\n"
            f"📊 Kategoriyada jami: <b>{final_count}</b> ta fayl"
        )
        await callback.answer()

    except Exception as e:
        logging.exception(e)
        await callback.message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    finally:
        await state.clear()


async def send_to_channel(
    file_id: str, file_type: str, file_name: str, category_name: str
) -> int:
    caption_text = f"{file_name}\nKategoriya: {category_name}"
    send_functions = {
        "document": bot.send_document,
        "photo": bot.send_photo,
        "video": bot.send_video,
        "audio": bot.send_audio,
    }

    try:
        send_func = send_functions.get(file_type, bot.send_document)
        msg = await send_func(
            chat_id=settings.get_channel_id,
            **{file_type: file_id},
            caption=caption_text,
        )
        return msg.message_id
    except Exception as e:
        raise ValueError(f"❌ Faylni kanalga yuborishda xatolik: {str(e)}")


@router.message(AdminFilter(), F.text == REMOVE_DATA)
async def cmd_remove_data(message: Message, state: FSMContext):
    categories = await get_all_categories()
    if not categories:
        await message.answer("❌ Hech qanday kategoriya yo'q.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=c.name, callback_data=f"delcat|{c.id}")]
            for c in categories
        ]
    )

    await message.answer(
        "Qaysi kategoriyadagi fayllarni o'chirmoqchisiz?\n" "Kategoriyani tanlang:",
        reply_markup=kb,
    )
    await state.set_state(FileDeleteState.waiting_for_category)


async def show_category_files(
    callback: CallbackQuery, state: FSMContext, category_id: int
):
    async with get_session() as session:
        category = await get_category_by_id(category_id)
        files = await get_files_by_category_id(category_id)

    if not files:
        await callback.message.answer(f"{category.name} kategoriyasida hali fayl yo‘q")
        await state.clear()
        await callback.answer()
        return False

    file_buttons = []
    for f in files:
        display_name = f.caption if hasattr(f, "caption") and f.caption else f.name

        file_buttons.append(
            [InlineKeyboardButton(text=display_name, callback_data=f"delfile|{f.id}")]
        )

    file_buttons.append(
        [
            InlineKeyboardButton(
                text="🔙 Back to Categories", callback_data="🔙 Back to Categories"
            )
        ]
    )

    kb = InlineKeyboardMarkup(inline_keyboard=file_buttons)

    await callback.message.answer(
        f"{category.name} kategoriyasidagi fayllar:\n"
        f"Jami: {len(files)} ta fayl\n\n"
        "O'chirmoqchi bo'lgan faylni tanlang:",
        reply_markup=kb,
    )
    return True


@router.callback_query(
    AdminFilter(), FileDeleteState.waiting_for_category, F.data.startswith("delcat|")
)
async def remove_data_select_category(callback: CallbackQuery, state: FSMContext):
    try:
        category_id = int(callback.data.split("|")[1])
    except ValueError:
        await callback.answer("❌ Noto'g'ri kategoriya ID!", show_alert=True)
        return

    files_exist = await show_category_files(callback, state, category_id)
    if files_exist:
        await state.update_data(selected_category_id=category_id)
        await state.set_state(FileDeleteState.waiting_for_file)
    await callback.answer()


@router.callback_query(
    AdminFilter(), FileDeleteState.waiting_for_file, F.data.startswith("delfile|")
)
async def remove_file_handler(callback: CallbackQuery, state: FSMContext):
    try:
        file_id = int(callback.data.split("|")[1])
    except ValueError:
        await callback.answer("❌ Noto'g'ri fayl ID!", show_alert=True)
        return

    async with get_session() as session:
        file_obj = await session.get(Files, file_id)
        if not file_obj:
            await callback.message.answer("❌ Fayl topilmadi")
            await state.clear()
            await callback.answer()
            return

        category = await get_category_by_id(file_obj.category_id)
        display_name = (
            file_obj.caption
            if hasattr(file_obj, "caption") and file_obj.caption
            else file_obj.name
        )

        try:
            if await AdminFilter()(callback):
                try:
                    await bot.delete_message(
                        chat_id=settings.get_channel_id, message_id=file_obj.message_id
                    )
                except Exception as e:
                    logging.error(f"Kanal xabarini o'chirishda xatolik: {e}")

            await session.delete(file_obj)
            await session.commit()

        except Exception as e:
            logging.error(f"Faylni o'chirishda xatolik: {e}")
            await callback.answer("Xatolik yuz berdi", show_alert=True)
            return

    success_msg = (
        f"{display_name} fayli\n" f"{category.name} kategoriyasidan o'chirildi!"
    )
    await callback.message.answer(success_msg)

    data = await state.get_data()
    category_id = data.get("selected_category_id")
    await show_category_files(callback, state, category_id)
    await callback.answer()


@router.callback_query(
    FileDeleteState.waiting_for_file, F.data == "🔙 Back to Categories"
)
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await cmd_remove_data(callback.message, state)
    await callback.answer()


@router.callback_query(
    FileDeleteState.waiting_for_file, F.data == "🔙 Back to Categories"
)
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await cmd_remove_data(callback.message, state)
    await callback.answer()
