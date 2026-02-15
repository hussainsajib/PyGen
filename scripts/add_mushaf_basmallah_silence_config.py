import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.config import Config
from sqlalchemy import select

async def add_mushaf_basmallah_silence_config():
    key = 'MUSHAF_BASMALLAH_SILENCE_DURATION'
    default_value = '1.0'
    print(f"Adding {key} config...")
    
    async with async_session() as session:
        result = await session.execute(select(Config).filter_by(key=key))
        if not result.scalar_one_or_none():
            print(f"Setting {key} to '{default_value}'...")
            session.add(Config(key=key, value=default_value))
            await session.commit()
        else:
            print(f"{key} config already exists.")

if __name__ == "__main__":
    asyncio.run(add_mushaf_basmallah_silence_config())
