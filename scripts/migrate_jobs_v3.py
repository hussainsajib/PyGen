import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def migrate():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Adding custom_title column to jobs table...")
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN custom_title VARCHAR(100);"))
            print("Column added successfully.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("Column custom_title already exists.")
            else:
                print(f"Error adding custom_title: {e}")
                    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
