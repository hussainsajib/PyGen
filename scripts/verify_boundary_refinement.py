import asyncio
from processes.mushaf_fast_video import generate_mushaf_fast
from config_manager import config_manager

async def run_verification():
    # Verify Surah 53 (Orphan Header Case)
    print("Generating Surah 53 (Expect Header merged with Page 526) using FFmpeg...")
    await generate_mushaf_fast(53, "ar.alafasy", "ffmpeg")

    # Verify Surah 108 (Standard Mid-Page Case)
    print("Generating Surah 108 (Expect Normal Header placement) using FFmpeg...")
    await generate_mushaf_fast(108, "ar.alafasy", "ffmpeg")

if __name__ == "__main__":
    asyncio.run(run_verification())
