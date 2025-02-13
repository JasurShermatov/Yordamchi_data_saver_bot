from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.bot.constants.admin import (
    CHANNEL_LIST,
    BACK,
    ADD_CHANNEL,
    REMOVE_CHANNEL,
)


async def channels_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_CHANNEL), KeyboardButton(text=REMOVE_CHANNEL)],
            [KeyboardButton(text=CHANNEL_LIST), KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
    )
