import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session, engine
from db.models.language import Language
from db.models.base import Base
from sqlalchemy import select

async def init_languages():
    print("Initializing languages...")
    
    # Ensure table exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Check and add Bengali
        result = await session.execute(select(Language).filter_by(name='bengali'))
        lang = result.scalar_one_or_none()
        if not lang:
            print("Adding Bengali...")
            session.add(Language(name='bengali', code='bn', font='Kalpurush', youtube_channel_id='UCVfyI5zQRcJxuJMxreY6I8g'))
        else:
            # Update font and youtube_channel_id if not set or default
            if not lang.font or lang.font == 'kalpurush.ttf':
                 lang.font = 'Kalpurush'
            if not lang.youtube_channel_id or lang.youtube_channel_id == 'UC-BENGALI-CHANNEL-ID':
                lang.youtube_channel_id = 'UCVfyI5zQRcJxuJMxreY6I8g'
            
        # Check and add English
        result = await session.execute(select(Language).filter_by(name='english'))
        lang = result.scalar_one_or_none()
        if not lang:
            print("Adding English...")
            session.add(Language(name='english', code='en', font='Segoe UI', youtube_channel_id='UC-TtqbMYI3TzOxfyEqT8VGQ'))
        else:
            if not lang.font or lang.font == 'arial.ttf' or lang.font == 'Arial':
                lang.font = 'Segoe UI'
            if not lang.youtube_channel_id or lang.youtube_channel_id == 'UC-ENGLISH-CHANNEL-ID':
                lang.youtube_channel_id = 'UC-TtqbMYI3TzOxfyEqT8VGQ'
        
        await session.commit()
    
    print("Language initialization complete.")

if __name__ == "__main__":
    asyncio.run(init_languages())
