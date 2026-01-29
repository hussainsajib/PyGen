from config_manager import config_manager
from db.database import async_session
import asyncio

async def add_border_width_config():
    async with async_session() as session:
        # Load existing config to cache
        await config_manager.load_from_db(session)
        
        # Check if it exists
        val = config_manager.get('MUSHAF_BORDER_WIDTH_PERCENT')
        if not val:
            print("Adding MUSHAF_BORDER_WIDTH_PERCENT default value 40...")
            await config_manager.set(session, 'MUSHAF_BORDER_WIDTH_PERCENT', '40')
        else:
            print(f"MUSHAF_BORDER_WIDTH_PERCENT already exists: {val}")

if __name__ == "__main__":
    asyncio.run(add_border_width_config())
