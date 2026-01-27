import asyncio
import anyio
from processes.mushaf_video import generate_mushaf_video

async def main():
    print("Generating Mushaf Video for Surah 87 (Multi-Page Test)...")
    # Using a known reciter key
    reciter_key = "ar.alafasy" 
    result = await generate_mushaf_video(surah_number=87, reciter_key=reciter_key, is_short=False)
    
    if result:
        print(f"Video generated successfully: {result['video']}")
    else:
        print("Failed to generate video.")

if __name__ == "__main__":
    anyio.run(main)
