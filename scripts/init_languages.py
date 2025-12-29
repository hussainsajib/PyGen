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
            session.add(Language(name='bengali', code='bn', font='kalpurush.ttf'))
        else:
            # Update font if not set or default
            if not lang.font or lang.font == 'arial.ttf':
                 lang.font = 'kalpurush.ttf'
            
        # Check and add English
        result = await session.execute(select(Language).filter_by(name='english'))
        lang = result.scalar_one_or_none()
        if not lang:
            print("Adding English...")
            session.add(Language(name='english', code='en', font='Segoe UI'))
        else:
            if not lang.font or lang.font == 'Arial': # Update from Arial too
                lang.font = 'Segoe UI'
        
        await session.commit()
    
    print("Language initialization complete.")

if __name__ == "__main__":
    asyncio.run(init_languages())
