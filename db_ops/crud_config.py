from sqlalchemy import select
from db.models import Config
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_session
from config_store import config_values

async def get_all_config(session: AsyncSession):
    result = await session.execute(select(Config))
    return result.scalars().all()

async def set_config_value(session: AsyncSession, key: str, value: str):
    result = await session.execute(select(Config).where(Config.key == key))
    config = result.scalar_one_or_none()
    if config:
        config.value = value
    else:
        config = Config(key=key, value=value)
        session.add(config)
    await session.commit()

async def reload_config():
    async with async_session() as session:
        config_items = await get_all_config(session)
        config_values.clear()
        config_values.update({item.key: item.value for item in config_items})