import asyncio
import sys
import os
import json
from sqlalchemy import select

sys.path.append(os.getcwd())
from db.database import engine, async_session
from db.models.surah import Surah
from db.models.base import Base

async def seed_surahs():
    print("Seeding Surahs table...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Ensure table exists
    
    async with async_session() as session:
        with open("data/surah_data.json", "r", encoding="utf-8") as f:
            surah_data = json.load(f)
            
            for key, data in surah_data.items():
                surah_number = int(data["serial"])
                
                result = await session.execute(select(Surah).filter_by(number=surah_number))
                existing_surah = result.scalar_one_or_none()
                
                if not existing_surah:
                    print(f"Adding Surah {surah_number}: {data['english_name']}")
                    session.add(Surah(
                        number=surah_number,
                        english_name=data["english_name"],
                        bangla_name=data["bangla_name"],
                        arabic_name=data["arabic_name"],
                        english_meaning=data["english_meaning"],
                        bangla_meaning=data["bangla_meaning"],
                        total_ayah=int(data["total_ayah"])
                    ))
                else:
                    # Optional: Update existing surah if data changes
                    # For now, just print a message
                    print(f"Surah {surah_number}: {data['english_name']} already exists.")
            
            await session.commit()
    print("Surahs seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_surahs())
