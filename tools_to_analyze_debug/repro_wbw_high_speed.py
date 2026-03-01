import asyncio
import os
from processes.wbw_fast_video import generate_wbw_fast

async def repro():
    surah_number = 1
    start_verse = 1
    end_verse = 1
    reciter_key = "ar.alafasy"
    engine_type = "pillow_opencv"
    is_short = False
    
    print(f"Reproducing High-Speed WBW for Surah {surah_number}:{start_verse}...")
    result = await generate_wbw_fast(
        surah_number, start_verse, end_verse, reciter_key, engine_type, is_short
    )
    
    if result and "video" in result:
        print(f"Video generated: {result['video']}")
        print(f"Performance: {result['performance']}")
    else:
        print("Generation failed.")

if __name__ == "__main__":
    asyncio.run(repro())
