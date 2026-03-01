import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.config import Config
from sqlalchemy import select

async def check_config():
    key = 'MUSHAF_BASMALLAH_SILENCE_DURATION'
    async with async_session() as session:
        result = await session.execute(select(Config).filter_by(key=key))
        item = result.scalar_one_or_none()
        if item:
            print(f"Key: {item.key}, Value: {item.value}")
        else:
            print(f"Config {key} not found.")

if __name__ == "__main__":
    asyncio.run(check_config())
