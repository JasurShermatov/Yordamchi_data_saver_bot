from aiogram.types import Message
from sqlalchemy.future import select
from datetime import datetime

from app.core.database.postgres import get_session
from app.bot.models.users import Users


async def get_all_users():
    async with get_session() as session:
        result = await session.execute(select(Users))
        users = result.scalars().all()
        return users


async def is_exist(user_id: int):
    async with get_session() as session:
        result = await session.execute(select(Users).where(Users.user_id == user_id))
        user = result.scalar_one_or_none()
        return user


async def create_or_update_user(message: Message):
    exist_user = await is_exist(message.from_user.id)
    async with get_session() as session:
        if exist_user is None:
            user = Users(
                user_id=message.from_user.id,
                username=message.from_user.username,
                full_name=(
                    f"{message.from_user.first_name} {message.from_user.last_name}"
                    if message.from_user.last_name
                    else message.from_user.first_name
                ),
                is_premium=message.from_user.is_premium,
            )
            session.add(user)
        else:
            exist_user.username = message.from_user.username
            exist_user.full_name = (
                f"{message.from_user.first_name} {message.from_user.last_name}"
                if message.from_user.last_name
                else message.from_user.first_name
            )
            exist_user.last_active_at = datetime.now()
            exist_user.is_premium = message.from_user.is_premium
            session.add(exist_user)
        await session.commit()
