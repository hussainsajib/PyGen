import asyncio
import os
import sys

sys.path.append(os.getcwd())

from processes.mushaf_video import generate_juz_video

async def test_juz_30():
    juz_number = 30
    reciter_key = "ar.alafasy"
    
    print(f"--- Regression Testing Juz {juz_number} ---")
    result = await generate_juz_video(
        juz_number=juz_number,
        reciter_key=reciter_key,
        is_short=False
    )
    
    if result:
        print(f"[SUCCESS] Juz video generated at: {result}")
    else:
        print("[FAILURE] Juz video generation failed.")

if __name__ == "__main__":
    asyncio.run(test_juz_30())
