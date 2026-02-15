import asyncio
import os
from processes.mushaf_video import generate_juz_video

async def reproduce_bug():
    # Attempt to generate Juz 30, Pages 1-2
    # This might fail on audio if not logged in, but we want to see the "Check alignment" error
    try:
        result = await generate_juz_video(
            juz_number=30,
            reciter_key="ar.alafasy",
            start_page=1,
            end_page=2,
            is_short=False
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(reproduce_bug())
