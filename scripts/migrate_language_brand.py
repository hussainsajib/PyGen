import asyncio
import sys
import os
from sqlalchemy import text, select

sys.path.append(os.getcwd())
from db.database import engine, async_session
from db.models.language import Language

async def migrate():
    print("Migrating languages table (brand_name)...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE languages ADD COLUMN brand_name VARCHAR DEFAULT 'Taqwa'"))
            print("Added brand_name column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")
    
    # Update rows
    async with async_session() as session:
        # Bengali
        result = await session.execute(select(Language).filter_by(name='bengali'))
        lang = result.scalar_one_or_none()
        if lang:
            lang.brand_name = "তাকওয়া বাংলা"
            print("Updated Bengali brand name.")
            
        # English
        result = await session.execute(select(Language).filter_by(name='english'))
        lang = result.scalar_one_or_none()
        if lang:
            lang.brand_name = "Taqwa"
            print("Updated English brand name.")
            
        await session.commit()

if __name__ == "__main__":
    asyncio.run(migrate())
