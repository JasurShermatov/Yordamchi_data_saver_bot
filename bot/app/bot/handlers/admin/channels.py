from sqlalchemy.future import select

from app.core.database.postgres import get_session
from app.bot.models.channels import Channels


async def is_exist(channel_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(Channels).where(Channels.channel_id == channel_id)
        )
        channel = result.scalar_one_or_none()
        return channel


async def create_channels(name, link, channel_id):
    exist_channel = await is_exist(channel_id)
    if exist_channel is not None:
        return "Bu kanal allaqachon qo`shilgan"
    async with get_session() as session:
        try:
            channel = Channels(name=name, link=link, channel_id=channel_id)
            session.add(channel)
            await session.commit()
            return "Kanal muaffaqiyatli qo`shildi"
        except Exception as _e:
            return f"Kanal qo`shishda xatolik yuz berdi: {_e}"


async def get_all_channels():
    async with get_session() as session:
        result = await session.execute(select(Channels))
        channels = result.scalars().all()
        return channels


async def delete_channel(channel_id: int):
    exist_channel = await is_exist(channel_id)
    if exist_channel is None:
        return False
    async with get_session() as session:
        await session.delete(exist_channel)
        await session.commit()
    return True
