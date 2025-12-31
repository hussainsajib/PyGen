import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from db.database import engine

async def migrate():
    print("Migrating languages table (youtube_channel_id)...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE languages ADD COLUMN youtube_channel_id VARCHAR"))
            print("Added youtube_channel_id column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
