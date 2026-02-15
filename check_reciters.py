import anyio
from sqlalchemy import select
from db.database import async_session
from db.models.reciter import Reciter

async def get_reciters():
    async with async_session() as session:
        result = await session.execute(select(Reciter))
        reciters = result.scalars().all()
        for r in reciters:
            print(r.reciter_key)

if __name__ == "__main__":
    anyio.run(get_reciters)