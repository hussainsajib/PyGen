import asyncio
from sqlalchemy import text
from db.database import engine

async def migrate():
    print("Migrating jobs table to add start_page and end_page...")
    async with engine.begin() as conn:
        for col in ["start_page", "end_page"]:
            try:
                await conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {col} INTEGER;"))
                print(f"Successfully added {col} column.")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column {col} already exists.")
                else:
                    print(f"[ERROR] Migrating {col}: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
