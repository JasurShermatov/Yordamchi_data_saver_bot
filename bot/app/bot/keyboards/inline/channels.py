from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.handlers.admin.channels import get_all_channels


async def chunk_list(values, chunk_size=1):
    return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]


async def get_channel_keyboard_nd(
    missing_channels: list | None = None,
):
    if missing_channels is None:
        channels = await get_all_channels()
    else:
        channels = missing_channels

    if not channels:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Sizda hali kanallar mavjud emas!",
                        callback_data="all_subscribed",
                    )
                ]
            ]
        )

    buttons = [
        InlineKeyboardButton(text=f"{channel.name}", url=channel.link)
        for channel in channels
    ]

    inline_buttons = await chunk_list(buttons, chunk_size=1)

    inline_buttons.append(
        [
            InlineKeyboardButton(
                text="✅OBUNA BO'LDIM", callback_data="check_subscription"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


async def get_channel_keyboard(
    missing_channels: list | None = None,
) -> InlineKeyboardMarkup:
    if missing_channels is None:
        channels = await get_all_channels()
    else:
        channels = missing_channels

    if not channels:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Sizda hali kanallar mavjud emas!",
                        callback_data="all_subscribed",
                    )
                ]
            ]
        )

    buttons = [
        InlineKeyboardButton(text=f"{channel['name']}", url=channel["link"])
        for channel in channels
    ]

    inline_buttons = await chunk_list(buttons, chunk_size=1)

    inline_buttons.append(
        [
            InlineKeyboardButton(
                text="✅OBUNA BO'LDIM", callback_data="check_subscription"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


async def get_delete_channel_keyboard():
    channels = await get_all_channels()

    if not channels:
        return None

    buttons = [
        InlineKeyboardButton(
            text=f"❌ {channel.name}",
            callback_data=f"delete_channel:{channel.channel_id}",
        )
        for channel in channels
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=await chunk_list(buttons, chunk_size=1)
    )

    return keyboard
