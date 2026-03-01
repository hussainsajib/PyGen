import asyncio
import os
from processes.video_utils import generate_video
from db.database import async_session
from db_ops.crud_reciters import get_reciter_by_key

async def repro():
    surah_number = 1
    start_verse = 1
    end_verse = 1
    reciter_key = "ar.alafasy"
    is_short = False
    
    # Enable full translation
    from config_manager import config_manager
    config_manager.set_local_override("WBW_FULL_TRANSLATION_ENABLED", "True")
    
    print(f"Reproducing Standard WBW for Surah {surah_number}:{start_verse}...")
    result = await generate_video(
        surah_number, start_verse, end_verse, reciter_key, is_short
    )
    
    if result and "video" in result:
        print(f"Video generated: {result['video']}")
        print(f"Details: {result['info']}")
    else:
        print("Generation failed.")

if __name__ == "__main__":
    asyncio.run(repro())
