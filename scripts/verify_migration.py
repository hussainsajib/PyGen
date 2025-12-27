import asyncio
from db.database import async_session
from sqlalchemy import func, select
from db.models import MediaAsset

async def count():
    async with async_session() as s:
        c = (await s.execute(select(func.count(MediaAsset.id)))).scalar()
        print(f"Assets in DB: {c}")

if __name__ == "__main__":
    asyncio.run(count())
