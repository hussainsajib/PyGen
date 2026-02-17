import asyncio
import os
import sys

sys.path.append(os.getcwd())

from processes.mushaf_video import generate_mushaf_video

async def test_surah_108_moviepy():
    surah_number = 108
    reciter_key = "ar.alafasy"
    
    print(f"--- Regression Testing Surah {surah_number} (MoviePy) ---")
    result = await generate_mushaf_video(
        surah_number=surah_number,
        reciter_key=reciter_key,
        is_short=False
    )
    
    if result:
        print(f"[SUCCESS] MoviePy video generated at: {result}")
    else:
        print("[FAILURE] MoviePy video generation failed.")

if __name__ == "__main__":
    asyncio.run(test_surah_108_moviepy())
