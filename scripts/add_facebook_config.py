import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.config import Config
from sqlalchemy import select

async def add_facebook_config():
    print("Adding Facebook configuration defaults...")
    
    async with async_session() as session:
        # ENABLE_FACEBOOK_UPLOAD
        result = await session.execute(select(Config).filter_by(key='ENABLE_FACEBOOK_UPLOAD'))
        if not result.scalar_one_or_none():
            print("Setting ENABLE_FACEBOOK_UPLOAD to 'false'...")
            session.add(Config(key='ENABLE_FACEBOOK_UPLOAD', value='false'))
        else:
            print("ENABLE_FACEBOOK_UPLOAD config already exists.")
            
        await session.commit()

if __name__ == "__main__":
    asyncio.run(add_facebook_config())
