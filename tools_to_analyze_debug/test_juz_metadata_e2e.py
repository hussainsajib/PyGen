import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from processes.mushaf_video import prepare_juz_data_package, get_juz_boundaries
from processes.description import generate_juz_details
from processes.Classes import Reciter
from db.database import async_session
from config_manager import config_manager
from dotenv import load_dotenv

load_dotenv()

async def test_juz_metadata_e2e():
    juz_number = 30
    reciter_key = "ar.alafasy"
    
    # Ensure config is loaded
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
    
    boundaries = get_juz_boundaries(juz_number)
    
    # Simplified mock of the data preparation for testing details generation
    # We just need some offsets.
    
    # Mocking what prepare_juz_data_package returns
    # But let's call the real one (it downloads audio but doesn't render)
    
    from db_ops.crud_reciters import get_reciter_by_key
    async with async_session() as session:
        reciter_db_obj = await get_reciter_by_key(session, reciter_key)
        
    print(f"Preparing data for Juz {juz_number}...")
    prep_res = await prepare_juz_data_package(juz_number, reciter_db_obj, boundaries)
    full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, _ = prep_res
    
    # Apply the shift as in generate_juz_video
    recitation_start_offset_ms = 5000
    for s_num in offsets:
        offsets[s_num] += recitation_start_offset_ms
        
    # Generate Details
    reciter_p = Reciter(reciter_key)
    current_language = "bengali"
    
    print("Generating details file...")
    filename = generate_juz_details(juz_number, reciter_p, offsets, False, current_language)
    
    if os.path.exists(filename):
        print(f"Details file generated at: {filename}")
        print("--- Content ---")
        with open(filename, "r", encoding="utf-8") as f:
            print(f.read())
            
    # Cleanup temp files from prepare_juz_data_package
    from processes.video_utils import cleanup_temp_file
    for tf in temp_files:
        cleanup_temp_file(tf)
    full_audio.close()
    for c in surah_clips:
        c.close()

if __name__ == "__main__":
    asyncio.run(test_juz_metadata_e2e())
