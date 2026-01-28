from config_manager import config_manager
from db.database import async_session
import asyncio

async def add_opacity():
    async with async_session() as session:
        # Load existing config to cache
        await config_manager.load_from_db(session)
        
        # Check if it exists
        val = config_manager.get('MUSHAF_PAGE_OPACITY')
        if not val:
            print("Adding MUSHAF_PAGE_OPACITY default value 90...")
            await config_manager.set(session, 'MUSHAF_PAGE_OPACITY', '90')
        else:
            print(f"MUSHAF_PAGE_OPACITY already exists: {val}")

if __name__ == "__main__":
    asyncio.run(add_opacity())
