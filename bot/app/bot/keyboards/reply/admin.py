from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.bot.constants.admin import (
    STATISTICS,
    USERS_EXCEL,
    SEND_MESSAGE,
    CHANNEL_CONTROLLER,
    CATEGORY_CONTROLLER,
    DATA_CONTROLLER,
)


async def menu_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=STATISTICS), KeyboardButton(text=USERS_EXCEL)],
            [
                KeyboardButton(text=CATEGORY_CONTROLLER),
                KeyboardButton(text=DATA_CONTROLLER),
            ],
            [
                KeyboardButton(text=CHANNEL_CONTROLLER),
                KeyboardButton(text=SEND_MESSAGE),
            ],
        ],
        resize_keyboard=True,
    )
