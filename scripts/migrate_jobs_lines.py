import asyncio
from sqlalchemy import text
from db.database import engine

async def migrate():
    print("Migrating jobs table to add lines_per_page...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN lines_per_page INTEGER DEFAULT 15;"))
            print("Successfully added lines_per_page column.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("Column lines_per_page already exists.")
            else:
                print(f"Error migrating: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
