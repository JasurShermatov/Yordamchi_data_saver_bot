from sqlalchemy.future import select

from app.core.database.postgres import get_session
from app.bot.models.category import Category


async def get_all_categories():
    async with get_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        if not categories:
            return None
        return categories


async def get_category_by_name(name):
    async with get_session() as session:
        result = await session.execute(select(Category).where(Category.name == name))
        category = result.scalar_one_or_none()
        return category


async def is_exist(category_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        return category


async def delete_category(category_id: int):
    exist_category = await is_exist(category_id)
    if exist_category is None:
        return False
    async with get_session() as session:
        await session.delete(exist_category)
        await session.commit()
    return True


async def create_category(name):
    ct = await get_category_by_name(name)
    if ct is not None:
        return False
    async with get_session() as session:
        category = Category(name=name)
        session.add(category)
        await session.commit()
        return True


async def get_category_by_id(category_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        return category
