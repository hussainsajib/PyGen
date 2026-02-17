import asyncio
import os
import sys

sys.path.append(os.getcwd())

from processes.mushaf_fast_video import generate_mushaf_fast

async def test_juz_30_fast():
    juz_number = 30
    reciter_key = "ar.alafasy"
    engine_type = "ffmpeg"
    
    print(f"--- Regression Testing Juz {juz_number} (Fast FFmpeg) ---")
    result = await generate_mushaf_fast(
        surah_number=juz_number,
        reciter_key=reciter_key,
        engine_type=engine_type,
        is_short=False,
        is_juz=True
    )
    
    if result:
        print(f"[SUCCESS] Fast Juz video generated at: {result}")
    else:
        print("[FAILURE] Fast Juz video generation failed.")

if __name__ == "__main__":
    asyncio.run(test_juz_30_fast())
