import os
import asyncio
import time
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processes.mushaf_video import generate_mushaf_video
from config_manager import config_manager

async def run_benchmark():
    print("--- Starting Mushaf Video Generation Benchmark ---")
    surah_number = 108
    reciter_key = "ar.alafasy"
    
    start_time = time.time()
    
    result = await generate_mushaf_video(
        surah_number=surah_number,
        reciter_key=reciter_key,
        is_short=False
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    if result:
        print(f"Benchmark completed successfully!")
        print(f"Output Video: {result['video']}")
        print(f"Total Execution Time: {total_time:.2f} seconds")
    else:
        print("Benchmark failed to generate video.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
