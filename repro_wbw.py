
import asyncio
import os
from processes.video_utils import generate_video
from config_manager import config_manager
from db.database import async_session

async def repro():
    # Load config from DB
    async with async_session() as session:
        await config_manager.load_from_db(session)
    
    # Force Enable Full Translation
    config_manager.set_local_override("WBW_FULL_TRANSLATION_ENABLED", "True")
    config_manager.set_local_override("WBW_FULL_TRANSLATION_SOURCE", "rawai_al_bayan")
    config_manager.set_local_override("DEFAULT_LANGUAGE", "bengali")
    
    try:
        # Maher Al Muaiqly: ar.mahermuaiqly
        result = await generate_video(1, 1, 1, "ar.mahermuaiqly", False)
        print(f"Video generated at: {result['video']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(repro())
