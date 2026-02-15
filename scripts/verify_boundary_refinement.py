import asyncio
import os
import sys

sys.path.append(os.getcwd())

from processes.mushaf_fast_video import generate_mushaf_fast

async def verify():
    reciter_key = "ar.alafasy"
    engine_type = "ffmpeg"
    
    # 1. Verify Surah 53 (Starts with Orphaned Header on Page 525)
    surah_53 = 53
    print(f"--- Generating Surah {surah_53} (Expecting Shifted Header) ---")
    res_53 = await generate_mushaf_fast(
        surah_number=surah_53,
        reciter_key=reciter_key,
        engine_type=engine_type,
        is_short=False
    )
    if res_53:
        print(f"[SUCCESS] Surah 53 video at: {res_53['video']}")
    else:
        print("[FAILURE] Surah 53 generation failed.")

    # 2. Verify Surah 108 (Starts mid-page with Ayahs)
    surah_108 = 108
    print(f"\n--- Generating Surah {surah_108} (Expecting No Shifting) ---")
    res_108 = await generate_mushaf_fast(
        surah_number=surah_108,
        reciter_key=reciter_key,
        engine_type=engine_type,
        is_short=False
    )
    if res_108:
        print(f"[SUCCESS] Surah 108 video at: {res_108['video']}")
    else:
        print("[FAILURE] Surah 108 generation failed.")

if __name__ == "__main__":
    asyncio.run(verify())
