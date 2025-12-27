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
        print("Adding new columns to jobs table...")
        # Check and add columns if they don't exist
        columns = {
            "job_type": "VARCHAR(50) DEFAULT 'standard'",
            "upload_after_generation": "INTEGER DEFAULT 0",
            "playlist_id": "VARCHAR(100)",
            "start_verse": "INTEGER",
            "end_verse": "INTEGER",
            "is_short": "INTEGER DEFAULT 0"
        }
        
        for col, col_type in columns.items():
            try:
                await conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {col} {col_type};"))
                print(f"Added column: {col}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"Column {col} already exists.")
                else:
                    print(f"Error adding {col}: {e}")
                    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
