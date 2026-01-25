import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.database import async_session
from db.models.language import Language
from sqlalchemy import select

async def check_langs():
    async with async_session() as session:
        result = await session.execute(select(Language))
        languages = result.scalars().all()
        print("Languages:")
        for lang in languages:
            print(f"  - {lang.name}: channel_id='{lang.youtube_channel_id}'")

if __name__ == "__main__":
    asyncio.run(check_langs())
