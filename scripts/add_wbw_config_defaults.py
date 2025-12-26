import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

from db.models.config import Config

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_config_defaults():
    defaults = {
        "WBW_FONT_SIZE_REGULAR": "60",
        "WBW_FONT_SIZE_SHORT": "40",
        "WBW_CHAR_LIMIT_REGULAR": "30",
        "WBW_CHAR_LIMIT_SHORT": "15"
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
