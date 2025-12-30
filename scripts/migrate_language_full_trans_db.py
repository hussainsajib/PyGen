import asyncio
import sys
import os
from sqlalchemy import text, select

sys.path.append(os.getcwd())
from db.database import engine, async_session
from db.models.language import Language

async def migrate():
    print("Migrating languages table (full_translation_db)...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE languages ADD COLUMN full_translation_db VARCHAR"))
            print("Added full_translation_db column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")
    
    # Update rows
    async with async_session() as session:
        # Bengali
        result = await session.execute(select(Language).filter_by(name='bengali'))
        lang = result.scalar_one_or_none()
        if lang:
            lang.full_translation_db = "rawai_al_bayan"
            print("Updated Bengali full_translation_db.")
            
        # English
        result = await session.execute(select(Language).filter_by(name='english'))
        lang = result.scalar_one_or_none()
        if lang:
            lang.full_translation_db = "saheeh_international"
            print("Updated English full_translation_db.")
            
        await session.commit()

if __name__ == "__main__":
    asyncio.run(migrate())
