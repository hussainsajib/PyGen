from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.language import Language

async def get_all_languages(db: AsyncSession):
    result = await db.execute(select(Language))
    return result.scalars().all()
