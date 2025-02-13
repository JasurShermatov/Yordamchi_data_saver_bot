from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.bot.constants.admin import (
    ADD_CATEGORY,
    BACK,
    REMOVE_CATEGORY,
    CATEGORY_LIST,
)


async def category_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_CATEGORY), KeyboardButton(text=REMOVE_CATEGORY)],
            [KeyboardButton(text=CATEGORY_LIST), KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
    )
