import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from processes.mushaf_video import generate_juz_video

async def test_range():
    print("--- Testing Juz Range Selection ---")
    # Juz 1, Surah 1, Ayahs 1-3
    result = await generate_juz_video(
        juz_number=1,
        reciter_key="ar.alafasy",
        is_short=False,
        start_ayah=1,
        end_ayah=3
    )
    
    if result:
        print(f"SUCCESS: Generated video at {result['video']}")
    else:
        print("FAILURE: No video generated")

if __name__ == "__main__":
    asyncio.run(test_range())
