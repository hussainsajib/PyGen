import asyncio
import os
from sqlalchemy import text
from db.database import engine

async def migrate():
    print("Migrating jobs table to add background_path...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN background_path VARCHAR(255);"))
            print("Successfully added background_path column.")
        except Exception as e:
            if "already exists" in str(e):
                print("Column background_path already exists.")
            else:
                print(f"Error migrating: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
