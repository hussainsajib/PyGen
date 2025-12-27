import asyncio
import os
from db.database import async_session
from sqlalchemy import select
from db.models.config import Config

async def check():
    async with async_session() as s:
        res = await s.execute(select(Config).where(Config.key.like('WBW%')))
        print([f"{c.key}={c.value}" for c in res.scalars().all()])

if __name__ == "__main__":
    asyncio.run(check())
