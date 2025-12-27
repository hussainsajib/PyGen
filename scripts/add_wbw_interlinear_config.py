import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

# Ensure we can import from project root
import sys
sys.path.append(os.getcwd())

from db.models.config import Config

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_config_defaults():
    defaults = {
        "WBW_INTERLINEAR_ENABLED": "False",
        "WBW_TRANSLATION_FONT_SIZE": "20"
    }
    
    async with async_session() as session:
        for key, value in defaults.items():
            stmt = select(Config).where(Config.key == key)
            result = await session.execute(stmt)
            if not result.scalars().first():
                print(f"Adding config: {key}={value}")
                new_config = Config(key=key, value=value)
                session.add(new_config)
            else:
                print(f"Config already exists: {key}")
        await session.commit()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_config_defaults())
