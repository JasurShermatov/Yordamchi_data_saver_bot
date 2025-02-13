import os
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.future import select
from typing import Any, Dict, Callable

from app.core.settings.config import Settings, get_settings

settings: Settings = get_settings()
from app.bot.keyboards.inline.channels import get_channel_keyboard
from app.bot.models import Channels
from app.core.database.postgres import get_session


class CheckSubscriptionMiddleware(BaseMiddleware):
    @staticmethod
    async def check_all_subscriptions(user_id: int, bot) -> list:
        if user_id in settings.admins:
            return []

        unsubscribe_channels = []
        async with get_session() as session:
            query = await session.execute(select(Channels))
            channels = query.scalars().all()

            for channel in channels:
                channel_link = channel.link.replace("https://t.me/", "@")
                channel_id = channel.channel_id
                try:
                    if channel_id:
                        member = await bot.get_chat_member(
                            chat_id=int(channel_id), user_id=user_id
                        )
                    else:
                        member = await bot.get_chat_member(
                            chat_id=channel_link, user_id=user_id
                        )

                    if member.status not in ["member", "administrator", "creator"]:
                        unsubscribe_channels.append(
                            {"name": channel.name, "link": channel.link}
                        )
                except Exception:
                    pass

        return unsubscribe_channels

    async def __call__(
        self, handler: Callable, event: Message | CallbackQuery, data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        bot = data["bot"]

        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)
        if isinstance(event, Message) and event.text in ["/start", "/help"]:
            return await handler(event, data)

        unsubscribe_channels = await self.check_all_subscriptions(user_id, bot)

        if unsubscribe_channels:
            buttons = await get_channel_keyboard(unsubscribe_channels)
            message_text = f"📢 Iltimos, quyidagi {len(unsubscribe_channels)} ta kanalga obuna bo'ling:"

            try:
                if isinstance(event, CallbackQuery):
                    await event.message.edit_text(
                        text=message_text, reply_markup=buttons
                    )
                    await event.answer(
                        "Botdan foydalanish uchun kanallarga obuna bo‘ling!",
                        show_alert=True,
                    )
                elif isinstance(event, Message):
                    await event.answer(text=message_text, reply_markup=buttons)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e):
                    raise e
            return
        return await handler(event, data)
