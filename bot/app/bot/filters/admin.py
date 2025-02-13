from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.core.settings.config import get_settings, Settings

settings: Settings = get_settings()


class AdminFilter(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id
        return user_id in settings.admins
