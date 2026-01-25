import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.config import Config
from sqlalchemy import select

async def add_video_background_speed_config():
    print("Adding VIDEO_BACKGROUND_SPEED config...")
    
    async with async_session() as session:
        result = await session.execute(select(Config).filter_by(key='VIDEO_BACKGROUND_SPEED'))
        if not result.scalar_one_or_none():
            print("Setting VIDEO_BACKGROUND_SPEED to '1.0'...")
            session.add(Config(key='VIDEO_BACKGROUND_SPEED', value='1.0'))
            await session.commit()
        else:
            print("VIDEO_BACKGROUND_SPEED config already exists.")

if __name__ == "__main__":
    asyncio.run(add_video_background_speed_config())
