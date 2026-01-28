from config_manager import config_manager
from db.database import async_session
import asyncio

async def add_font_scale():
    async with async_session() as session:
        # Load existing config to cache
        await config_manager.load_from_db(session)
        
        # Check if it exists
        val = config_manager.get('MUSHAF_FONT_SCALE')
        if not val:
            print("Adding MUSHAF_FONT_SCALE default value 0.8...")
            await config_manager.set(session, 'MUSHAF_FONT_SCALE', '0.8')
        else:
            print(f"MUSHAF_FONT_SCALE already exists: {val}")

if __name__ == "__main__":
    asyncio.run(add_font_scale())
