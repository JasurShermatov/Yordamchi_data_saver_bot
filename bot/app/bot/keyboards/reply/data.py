from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.bot.constants.admin import (
    ADD_DATA,
    BACK,
    REMOVE_DATA,
)


async def data_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_DATA), KeyboardButton(text=REMOVE_DATA)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
    )
