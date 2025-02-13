from sqlalchemy import select

from app.bot.handlers.admin.category import get_category_by_id
from app.bot.models.files import Files
from app.core.database.postgres import get_session
from app.core.settings.config import get_settings, Settings
from aiogram import Bot

settings: Settings = get_settings()

bot = Bot(token=settings.BOT_TOKEN)


async def send_to_channel(
    file_id: str, file_type: str, file_name: str, category_name: str
) -> int:
    caption_text = f"{file_name}\nKategoriya: {category_name}"

    try:
        if file_type == "document":
            msg = await bot.send_document(
                chat_id=settings.get_channel_id, document=file_id, caption=caption_text
            )
        elif file_type == "photo":
            msg = await bot.send_photo(
                chat_id=settings.get_channel_id, photo=file_id, caption=caption_text
            )
        elif file_type == "video":
            msg = await bot.send_video(
                chat_id=settings.get_channel_id, video=file_id, caption=caption_text
            )
        elif file_type == "audio":
            msg = await bot.send_audio(
                chat_id=settings.get_channel_id, audio=file_id, caption=caption_text
            )
        elif file_type == "voice":
            # Voice xabar (ovozi)
            # Telegramda voice caption'ini hozircha ishlatish mumkin, ammo
            # baʼzan ayrim versiyalarda cheklov bo‘lishi mumkin.
            msg = await bot.send_voice(
                chat_id=settings.get_channel_id, voice=file_id, caption=caption_text
            )
        elif file_type == "video_note":
            # Dumaloq video
            # Ko‘pincha video_note caption'ga ruxsat bermaydi,
            # agar "caption" ishlamasa, alohida xabar yuborish kerak bo‘ladi.
            msg = await bot.send_video_note(
                chat_id=settings.get_channel_id, video_note=file_id
            )
            # Agar category_name'ni ham yetkazmoqchi bo‘lsak,
            # msg = await bot.send_video_note(chat_id=..., video_note=file_id)
            # so‘ng msg = await bot.send_message(..., text=caption_text)
        elif file_type == "text":
            # Oddiy matn
            full_text = f"{file_id}\n\nKategoriya: {category_name}"
            msg = await bot.send_message(
                chat_id=settings.get_channel_id, text=full_text
            )
        else:
            # fallback
            msg = await bot.send_document(
                chat_id=settings.get_channel_id, document=file_id, caption=caption_text
            )

        return msg.message_id

    except Exception as e:
        raise ValueError(f"Faylni kanalga yuborishda xatolik: {str(e)}")


async def create_file(name: str, category_id: int, data: str) -> Files:
    category = await get_category_by_id(category_id)
    if category is None:
        raise ValueError(f"{category_id} lik kategoriya topilmadi")
    message_id = await send_to_channel(data, name)
    async with get_session() as session:
        file = Files(name=name, category_id=category_id, message_id=message_id)
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file


async def get_files_by_category_id(category_id: int):
    async with get_session() as session:
        files = await session.execute(
            select(Files).where(Files.category_id == category_id)
        )
        return files.scalars().all()
