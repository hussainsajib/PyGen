import asyncio
import time
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from processes.mushaf_video import generate_juz_video
from db.database import async_session
from config_manager import config_manager
from dotenv import load_dotenv
from moviepy.config import change_settings

load_dotenv()
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY")
if IMAGEMAGICK_BINARY:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

async def test_juz_integration():
    juz_number = 30
    reciter_key = "ar.alafasy"
    
    # Ensure config is loaded
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
    
    # In mushaf_video.py, generate_juz_video(juz_number, reciter_key, ...)
    # It will generate the full Juz unless we mock get_juz_boundaries to return a smaller page range
    # But let's just run it. If it takes too long, we can kill it and check the details file
    # since the details file is generated at the end.
    
    print(f"Starting Integration Test for Juz {juz_number}...")
    try:
        # Note: This might take a few minutes as it downloads audio and renders scenes
        video_path = await generate_juz_video(juz_number, reciter_key)
        if video_path:
            print(f"Video generated at: {video_path}")
            
            # Find the details file
            # exported_data/details/juz_30_mishary_alafasy.txt
            details_path = "exported_data/details/juz_30_mishary_alafasy.txt"
            if os.path.exists(details_path):
                print("--- Final Generated Details ---")
                with open(details_path, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("Details file not found!")
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_juz_integration())
