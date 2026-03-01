import asyncio
import time
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from processes.mushaf_video import generate_mushaf_video
from db.database import async_session
from config_manager import config_manager
from dotenv import load_dotenv
from moviepy.config import change_settings

load_dotenv()
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY")
if IMAGEMAGICK_BINARY:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

async def perf_test():
    surah_num = 108
    reciter_key = "ar.alafasy"
    
    # Ensure config is loaded
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
    
    print(f"Starting performance test for Surah {surah_num}...")
    start_time = time.time()
    
    try:
        result = await generate_mushaf_video(surah_num, reciter_key)
        end_time = time.time()
        
        if result:
            print(f"Video generated successfully in {end_time - start_time:.2f} seconds.")
            print(f"Output path: {result['video']}")
        else:
            print("Video generation failed (returned None).")
    except Exception as e:
        print(f"Performance test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(perf_test())
