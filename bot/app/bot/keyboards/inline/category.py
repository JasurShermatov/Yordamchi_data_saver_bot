from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.handlers.admin.category import get_all_categories


async def get_category_keyboard():
    categories = await get_all_categories()
    if not categories:
        return None
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=category.name, callback_data=f"{category.id}|{category.name}"
                )
            ]
            for category in categories
        ]
    )
    return keyboard


async def delete_category_button():
    categories = await get_all_categories()
    if not categories:
        return None
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌" + category.name,
                    callback_data=f"delete_category:{category.id}",
                )
            ]
            for category in categories
        ]
    )
    return keyboard


async def get_category_keyboard_cat():
    categories = await get_all_categories()
    if not categories:
        return None

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=category.name, callback_data=f"cat_|{category.id}"
                )
            ]
            for category in categories
        ]
    )

    return kb
