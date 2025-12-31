import os
import asyncio
import anyio
from fastapi.concurrency import run_in_threadpool
from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame
from processes.surah_video import generate_surah
from config_manager import config_manager
from db.database import async_session
from db_ops import crud_media_assets
from db.models.language import Language
from sqlalchemy import select
from db_ops.crud_language import fetch_localized_metadata
from db_ops.crud_reciters import get_reciter_by_key


async def _get_target_youtube_channel_id():
    async with async_session() as session:
        # We need the language object to get the youtube_channel_id
        # For this, we fetch language object based on DEFAULT_LANGUAGE from config
        lang_name = config_manager.get("DEFAULT_LANGUAGE", "bengali")
        result = await session.execute(select(Language).filter_by(name=lang_name))
        lang_obj = result.scalar_one_or_none()
        
        if lang_obj and lang_obj.youtube_channel_id:
            return lang_obj.youtube_channel_id
    return None

async def _get_playlist_for_reciter(reciter_key: str):
    """Fetches the default playlist for a reciter from the database."""
    async with async_session() as session:
        reciter_obj = await get_reciter_by_key(session, reciter_key)
        if reciter_obj:
            return reciter_obj.playlist_id
    return None

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

async def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False, custom_title: str = None):
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            target_channel_id = await _get_target_youtube_channel_id() # Fetch channel ID
            video_id = await run_in_threadpool(upload_to_youtube, video_details, target_channel_id)
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")
        
async def create_surah_video(surah: int, reciter: str, custom_title: str = None):
    video_details = await generate_surah(surah, reciter, custom_title=custom_title)
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            target_channel_id = await _get_target_youtube_channel_id()
            video_id = await run_in_threadpool(upload_to_youtube, video_details, target_channel_id)
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

async def create_wbw_video_job(surah: int, start_verse: int, end_verse:int, 
                        reciter: str, is_short:bool = False, 
                        upload_after_generation: bool = False,
                        playlist_id: str = None,
                        custom_title: str = None):
    """Generates a WBW video and optionally uploads it to YouTube."""
    video_details = await generate_video(surah, start_verse, end_verse, reciter, is_short, custom_title=custom_title)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Upload to YouTube if requested
    if upload_after_generation:
        from processes import youtube_utils
        
        target_channel_id = await _get_target_youtube_channel_id() # Fetch channel ID
        
        # Determine the target playlist behavior
        # 'none'    => Upload without playlist
        # 'default' => Use reciter's default from DB (if any)
        # ID        => Use specific override ID
        
        original_playlist = await _get_playlist_for_reciter(reciter)
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
            video_id = await run_in_threadpool(upload_to_youtube, video_details, target_channel_id, original_playlist)
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

async def manual_upload_to_youtube(video_filename: str, reciter_key: str, playlist_id: str, details_filename: str):
    import os
    import re
    from processes.youtube_utils import upload_to_youtube
    
    target_channel_id = await _get_target_youtube_channel_id() # Fetch channel ID
    
    video_path = os.path.join("exported_data/videos", video_filename)
    details_path = os.path.join("exported_data/details", details_filename)
    
    # Try to find screenshot
    match = await run_in_threadpool(re.match, r'quran_video_(\d+)_(.+)\.mp4', video_filename)
    screenshot_path = None
    if match:
        surah_num = match.group(1)
        rest = match.group(2)
        screenshot_dir = "exported_data/screenshots"
        potential_path = os.path.join(screenshot_dir, f"screenshot_quran_video_{surah_num}_{rest}.png")
        if await run_in_threadpool(os.path.exists, potential_path):
            screenshot_path = potential_path
        else:
            def normalize(s):
                return re.sub(r'[^a-z0-9]', '', s.lower())
            for s_file in await run_in_threadpool(os.listdir, screenshot_dir):
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
        video_id = await run_in_threadpool(upload_to_youtube, video_details, target_channel_id, playlist_id) # Pass channel ID and playlist_id
        if video_id:
            await update_media_asset_upload(video_path, video_id)
    finally:
        youtube_utils.playlist = original_playlist