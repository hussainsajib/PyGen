import os
import asyncio
from processes.wbw_fast_video import generate_wbw_fast

async def verify():
    surah_number = 1
    start_verse = 1
    end_verse = 7
    reciter_key = "ar.alafasy"
    engine_type = "pillow_opencv"
    
    print(f"Generating WBW video for Surah {surah_number}:{start_verse}-{end_verse}...")
    result = await generate_wbw_fast(
        surah_number, start_verse, end_verse, reciter_key, engine_type, is_short=False
    )
    
    if result and "video" in result:
        print(f"Video generated successfully: {result['video']}")
        print(f"Performance: {result['performance']}")
    else:
        print("Video generation failed.")

if __name__ == "__main__":
    asyncio.run(verify())
