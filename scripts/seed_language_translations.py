import asyncio
import sys
import os
import json
from sqlalchemy import select

sys.path.append(os.getcwd())
from db.database import engine, async_session
from db.models.language import Language
from db.models.language_translation import LanguageTranslation
from db.models.base import Base

async def seed_language_translations():
    print("Seeding LanguageTranslations table...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Ensure table exists
    
    async with async_session() as session:
        # Get language IDs
        result_bengali = await session.execute(select(Language).filter_by(name='bengali'))
        bengali_lang = result_bengali.scalar_one_or_none()
        
        result_english = await session.execute(select(Language).filter_by(name='english'))
        english_lang = result_english.scalar_one_or_none()
        
        if bengali_lang:
            # Check and add Rawai Al Bayan
            result = await session.execute(select(LanguageTranslation).filter_by(db_name='rawai_al_bayan'))
            if not result.scalar_one_or_none():
                session.add(LanguageTranslation(language_id=bengali_lang.id, db_name='rawai_al_bayan', display_name='Rawai Al Bayan'))
            
            # Check and add Taisirul Quran
            result = await session.execute(select(LanguageTranslation).filter_by(db_name='taisirul_quran'))
            if not result.scalar_one_or_none():
                session.add(LanguageTranslation(language_id=bengali_lang.id, db_name='taisirul_quran', display_name='Taisirul Quran'))
        
        if english_lang:
            # Check and add Saheeh International
            result = await session.execute(select(LanguageTranslation).filter_by(db_name='saheeh_international'))
            if not result.scalar_one_or_none():
                session.add(LanguageTranslation(language_id=english_lang.id, db_name='saheeh_international', display_name='Saheeh International'))
                
        await session.commit()
    print("LanguageTranslations seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_language_translations())
