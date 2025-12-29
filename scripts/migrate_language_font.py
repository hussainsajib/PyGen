import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from db.database import engine

async def migrate():
    print("Migrating languages table...")
    async with engine.begin() as conn:
        try:
            # SQLite syntax doesn't strictly require VARCHAR length, Postgres does but generic is fine.
            # However, for SQLite, add column one by one is limited in older versions, but should be fine.
            # Using standard SQL.
            await conn.execute(text("ALTER TABLE languages ADD COLUMN font VARCHAR"))
            print("Added font column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
