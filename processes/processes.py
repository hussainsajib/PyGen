import os
import asyncio
import anyio
from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame
from processes.surah_video import generate_surah
from config_manager import config_manager
from db.database import async_session
from db_ops import crud_media_assets

async def record_media_asset(video_details: dict):
    """Records a new media asset in the database."""
    async with async_session() as session:
        asset_data = {
            "video_path": video_details["video"],
            "screenshot_path": video_details.get("screenshot"),
            "details_path": video_details.get("info"),
            "surah_number": video_details.get("surah_number"),
            "start_ayah": video_details.get("start_ayah"),
            "end_ayah": video_details.get("end_ayah"),
            "reciter_key": video_details.get("reciter"),
            "generation_status": "success",
            "file_size": os.path.getsize(video_details["video"]) / (1024 * 1024) if os.path.exists(video_details["video"]) else 0
        }
        await crud_media_assets.create_media_asset(session, asset_data)

async def update_media_asset_upload(video_path: str, video_id: str):
    """Updates the upload status of a media asset in the database."""
    async with async_session() as session:
        from sqlalchemy import select
        from db.models import MediaAsset
        result = await session.execute(
            select(MediaAsset).where(MediaAsset.video_path == video_path).order_by(MediaAsset.created_at.desc())
        )
        asset = result.scalars().first()
        if asset:
            asset.youtube_upload_status = "uploaded"
            asset.youtube_video_id = video_id
            await session.commit()

def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False):
    video_details = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    anyio.from_thread.run(record_media_asset, video_details)
    
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            video_id = upload_to_youtube(video_details)
            if video_id:
                anyio.from_thread.run(update_media_asset_upload, video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")
        
def create_surah_video(surah: int, reciter: str):
    video_details = generate_surah(surah, reciter)
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    anyio.from_thread.run(record_media_asset, video_details)
    
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            video_id = upload_to_youtube(video_details)
            if video_id:
                anyio.from_thread.run(update_media_asset_upload, video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

def create_wbw_video_job(surah: int, start_verse: int, end_verse:int, 
                        reciter: str, is_short:bool = False, 
                        upload_after_generation: bool = False,
                        playlist_id: str = None):
    """Generates a WBW video and optionally uploads it to YouTube."""
    video_details = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    anyio.from_thread.run(record_media_asset, video_details)
    
    # Upload to YouTube if requested
    if upload_after_generation:
        from processes import youtube_utils
        
        # Determine the target playlist behavior
        # 'none'    => Upload without playlist
        # 'default' => Use reciter's default from DB (if any)
        # ID        => Use specific override ID
        
        original_playlist = youtube_utils.playlist.get(reciter)
        override_applied = False
        
        if playlist_id == "none":
            # Temporarily clear the playlist for this reciter if it exists
            if reciter in youtube_utils.playlist:
                del youtube_utils.playlist[reciter]
            override_applied = True
        elif playlist_id == "default":
            # 'default' means we don't apply an override, use what's in youtube_utils.playlist
            pass
        elif playlist_id:
            # Apply specific override ID
            youtube_utils.playlist[reciter] = playlist_id
            override_applied = True
            
        try:
            video_id = upload_to_youtube(video_details)
            if video_id:
                anyio.from_thread.run(update_media_asset_upload, video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")
        finally:
            # Restore original state if we applied an override
            if override_applied:
                if original_playlist:
                    youtube_utils.playlist[reciter] = original_playlist
                else:
                    if reciter in youtube_utils.playlist:
                        del youtube_utils.playlist[reciter]

def manual_upload_to_youtube(video_filename: str, reciter_key: str, playlist_id: str, details_filename: str):
    import os
    import re
    from processes.youtube_utils import upload_to_youtube
    
    video_path = os.path.join("exported_data/videos", video_filename)
    details_path = os.path.join("exported_data/details", details_filename)
    
    # Try to find screenshot
    match = re.match(r'quran_video_(\d+)_(.+)\.mp4', video_filename)
    screenshot_path = None
    if match:
        surah_num = match.group(1)
        rest = match.group(2)
        screenshot_dir = "exported_data/screenshots"
        potential_path = os.path.join(screenshot_dir, f"screenshot_quran_video_{surah_num}_{rest}.png")
        if os.path.exists(potential_path):
            screenshot_path = potential_path
        else:
            def normalize(s):
                return re.sub(r'[^a-z0-9]', '', s.lower())
            for s_file in os.listdir(screenshot_dir):
                if s_file.startswith(f"screenshot_quran_video_{surah_num}_") and normalize(s_file) == normalize(f"screenshot_quran_video_{surah_num}_{rest}.png"):
                    screenshot_path = os.path.join(screenshot_dir, s_file)
                    break

    video_details = {
        "video": video_path,
        "info": details_path,
        "screenshot": screenshot_path,
        "reciter": reciter_key,
        "is_short": False
    }
    
    from processes import youtube_utils
    original_playlist = youtube_utils.playlist.copy()
    if playlist_id:
        youtube_utils.playlist[reciter_key] = playlist_id
    
    try:
        video_id = upload_to_youtube(video_details)
        if video_id:
            anyio.from_thread.run(update_media_asset_upload, video_path, video_id)
    finally:
        youtube_utils.playlist = original_playlist
