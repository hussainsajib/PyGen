import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def check():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reciters' AND column_name='wbw_database';
        """))
        found = result.scalar() is not None
        print(f"Column found: {found}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
