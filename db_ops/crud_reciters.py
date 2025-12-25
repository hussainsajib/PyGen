
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models.reciter import Reciter

async def get_all_reciters(db: AsyncSession):
    """Returns all reciters from the database."""
    result = await db.execute(select(Reciter).order_by(Reciter.english_name))
    return result.scalars().all()

async def get_reciter_by_id(db: AsyncSession, reciter_id: int):
    """Returns a single reciter by their ID."""
    result = await db.execute(select(Reciter).where(Reciter.id == reciter_id))
    return result.scalars().first()

async def get_reciter_by_key(db: AsyncSession, reciter_key: str):
    """Returns a single reciter by their key."""
    result = await db.execute(select(Reciter).where(Reciter.reciter_key == reciter_key))
    return result.scalars().first()

async def create_reciter(db: AsyncSession, reciter_data: dict):
    """Creates a new reciter in the database."""
    new_reciter = Reciter(**reciter_data)
    db.add(new_reciter)
    await db.commit()
    await db.refresh(new_reciter)
    return new_reciter

async def update_reciter(db: AsyncSession, reciter_id: int, reciter_data: dict):
    """Updates an existing reciter."""
    reciter = await get_reciter_by_id(db, reciter_id)
    if not reciter:
        return None
    
    for key, value in reciter_data.items():
        setattr(reciter, key, value)
    
    await db.commit()
    await db.refresh(reciter)
    return reciter

async def delete_reciter(db: AsyncSession, reciter_id: int):
    """Deletes a reciter from the database."""
    reciter = await get_reciter_by_id(db, reciter_id)
    if reciter:
        await db.delete(reciter)
        await db.commit()
        return True
    return False
