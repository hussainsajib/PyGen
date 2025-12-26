import os
import re
import asyncio
import json
import sys

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_session, init_db
from db.models import Reciter, MediaAsset
from db_ops import crud_reciters, crud_media_assets

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

async def scan_and_map_assets(session: AsyncSession):
    video_dir = "exported_data/videos"
    screenshot_dir = "exported_data/screenshots"
    detail_dir = "exported_data/details"
    
    if not os.path.exists(video_dir):
        print(f"Directory {video_dir} not found.")
        return []
        
    reciters = await crud_reciters.get_all_reciters(session)
    reciter_map = {}
    for r in reciters:
        name = getattr(r, 'english_name', None)
        if name:
            reciter_map[normalize(name)] = {
                "english_name": name,
                "reciter_key": getattr(r, 'reciter_key', None)
            }

    video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
    assets_to_create = []

    for video_file in video_files:
        match = re.match(r'quran_video_(\d+)_(.+)\.mp4', video_file)
        if not match:
            continue
            
        surah_num = int(match.group(1))
        rest = match.group(2)
        normalized_rest = normalize(rest)
        
        # Screenshot
        screenshot_path = None
        if os.path.exists(screenshot_dir):
            screenshot_name = f"screenshot_quran_video_{surah_num}_{rest}.png"
            if os.path.exists(os.path.join(screenshot_dir, screenshot_name)):
                screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            else:
                for s_file in os.listdir(screenshot_dir):
                    if s_file.startswith(f"screenshot_quran_video_{surah_num}_") and normalize(s_file) == normalize(f"screenshot_quran_video_{surah_num}_{rest}.png"):
                        screenshot_path = os.path.join(screenshot_dir, s_file)
                        break

        # Details
        details_path = None
        start_ayah = None
        end_ayah = None
        if os.path.exists(detail_dir):
            for d_file in os.listdir(detail_dir):
                if d_file.startswith(f"{surah_num}_") and d_file.endswith(".txt"):
                    d_base = d_file[:-4]
                    if normalize(d_base) in normalized_rest or normalized_rest in normalize(d_base):
                        details_path = os.path.join(detail_dir, d_file)
                        # Extract ayah range if possible
                        # Pattern: {surah}_{start}_{end}_{reciter}.txt
                        d_match = re.match(r'(\d+)_(\d+)_(\d+)_(.+)', d_file)
                        if d_match:
                            start_ayah = int(d_match.group(2))
                            end_ayah = int(d_match.group(3))
                        break
        
        # Reciter
        reciter_key = "unknown"
        for norm_name, r_info in reciter_map.items():
            if norm_name in normalized_rest:
                reciter_key = r_info["reciter_key"]
                break

        asset_data = {
            "video_path": os.path.join(video_dir, video_file),
            "screenshot_path": screenshot_path,
            "details_path": details_path,
            "surah_number": surah_num,
            "start_ayah": start_ayah,
            "end_ayah": end_ayah,
            "reciter_key": reciter_key,
            "generation_status": "success",
            "youtube_upload_status": "pending",
            "file_size": os.path.getsize(os.path.join(video_dir, video_file)) / (1024 * 1024) # MB
        }
        assets_to_create.append(asset_data)
        
    return assets_to_create

async def main():
    await init_db()
    async with async_session() as session:
        print("Scanning exported_data...")
        assets = await scan_and_map_assets(session)
        print(f"Found {len(assets)} assets. Migrating to database...")
        
        for asset_data in assets:
            # Check if already exists to avoid duplicates
            from sqlalchemy import select
            result = await session.execute(
                select(MediaAsset).where(MediaAsset.video_path == asset_data["video_path"])
            )
            if not result.scalar_one_or_none():
                await crud_media_assets.create_media_asset(session, asset_data)
                print(f"Imported: {asset_data['video_path']}")
            else:
                print(f"Skipped (already exists): {asset_data['video_path']}")
        
        print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(main())
