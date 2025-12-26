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
        print("Checking if column exists...")
        # PostgreSQL specific query to check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reciters' AND column_name='wbw_database';
        """)
        result = await conn.execute(check_query)
        column_exists = result.scalar() is not None
        
        if not column_exists:
            print("Adding wbw_database column to reciters table...")
            await conn.execute(text("ALTER TABLE reciters ADD COLUMN wbw_database VARCHAR(100);"))
            print("Column added successfully.")
        else:
            print("Column already exists.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
