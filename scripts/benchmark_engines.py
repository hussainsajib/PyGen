import asyncio
import time
import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from processes.performance import PerformanceMonitor
from processes.mushaf_fast_video import generate_mushaf_fast
from processes.mushaf_video import generate_mushaf_video
from db.database import async_session
from config_manager import config_manager
from dotenv import load_dotenv
from moviepy.config import change_settings

load_dotenv()
IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY")
if IMAGEMAGICK_BINARY:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

async def run_benchmark():
    surah_num = 108
    reciter_key = "ar.alafasy"
    
    # Ensure config is loaded
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
    
    # Take engine from arg or use default list
    import sys
    if len(sys.argv) > 1:
        engines = [sys.argv[1]]
    else:
        engines = ["ffmpeg", "opencv", "pyav"]
        
    results = [
        {"name": "Benchmark_moviepy", "duration_ms": 327350, "peak_memory_mb": 335.19, "memory_increase_mb": 0}
    ]
    
    print(f"Starting Benchmark for Surah {surah_num} across {len(engines)} engines...")
    
    for engine in engines:
        print(f"\n--- Testing Engine: {engine} ---")
        monitor = PerformanceMonitor(f"Benchmark_{engine}")
        monitor.start()
        
        try:
            if engine == "moviepy":
                await generate_mushaf_video(surah_num, reciter_key)
            else:
                await generate_mushaf_fast(surah_num, reciter_key, engine)
                
            monitor.stop()
            report = monitor.get_report()
            results.append(report)
            print(f"Completed {engine} in {report['duration_ms']/1000:.2f}s with {report['peak_memory_mb']:.2f}MB peak RAM.")
        except Exception as e:
            print(f"Engine {engine} failed: {e}")
            results.append({"name": f"Benchmark_{engine}", "duration_ms": 0, "peak_memory_mb": 0, "error": str(e)})

    # Print Summary Table
    print("\n" + "="*50)
    print("BENCHMARK SUMMARY")
    print("="*50)
    header = ["Engine", "Duration (s)", "Peak RAM (MB)", "RAM Incr (MB)"]
    rows = []
    for r in results:
        rows.append([
            r["name"].replace("Benchmark_", ""),
            f"{r['duration_ms']/1000:.2f}",
            f"{r['peak_memory_mb']:.2f}",
            f"{r.get('memory_increase_mb', 0):.2f}"
        ])
    
    col_widths = [10, 15, 15, 15]
    def print_row(row):
        print(" | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)))
    
    print_row(header)
    print("-" * 60)
    for row in rows:
        print_row(row)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
