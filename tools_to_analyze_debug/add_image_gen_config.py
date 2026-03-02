import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from db.database import init_db, async_session
from db.models.config import Config
from sqlalchemy import select

async def add_config_keys():
    await init_db()
    async with async_session() as session:
        keys_to_add = {
            "IMAGE_GEN_DEFAULT_HASHTAGS": "#Quran #TaqwaBangla #IslamicPost #Deen",
            "IMAGE_GEN_CAPTION_TEMPLATE": "{user_description}\n\n{surah_name} আয়াত {ayah_number}\n\n{hashtags}"
        }
        
        for key, value in keys_to_add.items():
            stmt = select(Config).where(Config.key == key)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                print(f"Adding config key: {key}")
                new_config = Config(key=key, value=value)
                session.add(new_config)
            else:
                print(f"Config key already exists: {key}")
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(add_config_keys())
