from datetime import timedelta

from sqlalchemy.future import select

from app.core.database.postgres import get_session
from app.bot.models.users import Users


async def count_users():
    async with get_session() as session:
        result = await session.execute(select(Users))
        return len(result.scalars().all())


async def count_users_by_date(date):
    async with get_session() as session:
        result = await session.execute(
            select(Users).where(
                Users.created_at >= date, Users.created_at < date + timedelta(days=1)
            )
        )
        return len(result.scalars().all())


async def count_users_between(start_date, end_date):
    async with get_session() as session:
        result = await session.execute(
            select(Users).where(
                Users.created_at >= start_date, Users.created_at < end_date
            )
        )
        return len(result.scalars().all())
