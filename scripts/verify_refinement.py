import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from processes.mushaf_fast_video import generate_mushaf_fast
from db.database import async_session
from config_manager import config_manager
from dotenv import load_dotenv
from moviepy.config import change_settings

load_dotenv()
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY")
if IMAGEMAGICK_BINARY:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

async def run_final_verification():
    surah_num = 108
    reciter_key = "ar.alafasy"
    engine = "ffmpeg"
    
    # Ensure config is loaded
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
    
    print(f"Starting Final Verification for Surah {surah_num} using {engine}...")
    
    try:
        result = await generate_mushaf_fast(surah_num, reciter_key, engine)
        
        if result:
            print("\n==================================================")
            print("VERIFICATION RESULTS")
            print("==================================================")
            print(f"Video Path: {result['video']}")
            print(f"Metadata Path: {result.get('info')}")
            
            # Check file existence
            video_exists = os.path.exists(result['video'])
            meta_exists = os.path.exists(result['info']) if result.get('info') else False
            
            print(f"Video File Exists: {video_exists}")
            print(f"Metadata File Exists: {meta_exists}")
            
            if video_exists and meta_exists:
                print("\n[PASS] All refinement requirements verified successfully.")
            else:
                print("\n[FAIL] Some files are missing.")
        else:
            print("\n[FAIL] Generation returned None.")
            
    except Exception as e:
        print(f"\n[ERROR] Verification failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(run_final_verification())
