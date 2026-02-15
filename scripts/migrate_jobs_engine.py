import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy import text
from db.database import engine

async def migrate():
    print("Migrating jobs table to add engine_type and performance_report...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN engine_type VARCHAR(20) DEFAULT 'moviepy'"))
            print("Added engine_type column.")
        except Exception as e:
            print(f"Failed to add engine_type (might exist): {e}")
            
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN performance_report TEXT"))
            print("Added performance_report column.")
        except Exception as e:
            print(f"Failed to add performance_report (might exist): {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
