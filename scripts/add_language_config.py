import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.config import Config
from sqlalchemy import select

async def add_language_config():
    print("Adding DEFAULT_LANGUAGE config...")
    
    async with async_session() as session:
        result = await session.execute(select(Config).filter_by(key='DEFAULT_LANGUAGE'))
        if not result.scalar_one_or_none():
            print("Setting DEFAULT_LANGUAGE to 'bengali'...")
            session.add(Config(key='DEFAULT_LANGUAGE', value='bengali'))
            await session.commit()
        else:
            print("DEFAULT_LANGUAGE config already exists.")

if __name__ == "__main__":
    asyncio.run(add_language_config())
