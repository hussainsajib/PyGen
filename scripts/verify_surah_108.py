import asyncio
import os
import sys

sys.path.append(os.getcwd())

from processes.mushaf_fast_video import generate_mushaf_fast

async def test_surah_108():
    surah_number = 108
    reciter_key = "ar.alafasy"
    engine_type = "ffmpeg"
    
    print(f"--- Regression Testing Surah {surah_number} ---")
    result = await generate_mushaf_fast(
        surah_number=surah_number,
        reciter_key=reciter_key,
        engine_type=engine_type,
        is_short=False
    )
    
    if result:
        print(f"[SUCCESS] Video generated at: {result}")
    else:
        print("[FAILURE] Video generation failed.")

if __name__ == "__main__":
    asyncio.run(test_surah_108())
