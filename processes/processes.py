import os
import asyncio
import anyio
from fastapi.concurrency import run_in_threadpool
from processes.video_utils import generate_video, get_video_duration
from processes.youtube_utils import upload_to_youtube
from processes.facebook_utils import FacebookClient
from processes.screenshot import extract_frame
from processes.surah_video import generate_surah
from processes.mushaf_video import generate_mushaf_video, generate_juz_video
from processes.mushaf_fast_video import generate_mushaf_fast
from processes.logger import logger
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

async def _upload_to_facebook_if_enabled(video_details: dict):
    """Checks if Facebook upload is enabled and performs the upload if it is."""
    if config_manager.get("ENABLE_FACEBOOK_UPLOAD") == "True":
        fb_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        fb_page_id = os.getenv("FB_PAGE_ID")
        
        if not fb_token or not fb_page_id:
            print("Facebook credentials missing from environment variables.")
            return

        fb_client = FacebookClient(fb_token, fb_page_id)
        
        # Parse metadata from info file if available
        title = "Quran Recitation"
        description = ""
        
        info_path = video_details.get("info")
        if info_path and os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        title = lines[0].strip()
                        description = "".join(lines[1:]).strip()
            except Exception as e:
                print(f"Error reading info file for Facebook upload: {e}")

        try:
            video_id = await run_in_threadpool(
                fb_client.upload_to_facebook,
                video_path=video_details["video"],
                title=title,
                description=description
            )
            if video_id:
                print(f"Facebook upload successful: {video_id}")
        except Exception as e:
            print(f"Facebook upload failed: {e}")

async def record_media_asset(video_details: dict):
    """Records a new media asset in the database."""
    async with async_session() as session:
        # Default surah_number to 0 if not present (common for Juz videos)
        s_num = video_details.get("surah_number")
        if s_num is None:
            s_num = 0
            
        asset_data = {
            "video_path": video_details["video"],
            "screenshot_path": video_details.get("screenshot"),
            "details_path": video_details.get("info"),
            "surah_number": s_num,
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
        
async def create_surah_video(surah: int, reciter: str, custom_title: str = None, upload_after_generation: bool = False):
    video_details = await generate_surah(surah, reciter, custom_title=custom_title)
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Upload to YouTube if enabled in config
    if upload_after_generation:
        try:
            target_channel_id = await _get_target_youtube_channel_id()
            video_id = await run_in_threadpool(upload_to_youtube, video_details, target_channel_id)
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")
            
    # Sleep for 20 seconds before uploading to Facebook if YouTube upload was attempted/enabled
    if upload_after_generation:
        await asyncio.sleep(20)

    # Upload to Facebook if enabled
    await _upload_to_facebook_if_enabled(video_details)

async def create_wbw_video_job(surah: int, start_verse: int, end_verse:int, 
                        reciter: str, is_short:bool = False, 
                        upload_after_generation: bool = False,
                        playlist_id: str = None,
                        custom_title: str = None,
                        background_path: str = None):
    """Generates a WBW video and optionally uploads it to YouTube."""
    video_details = await generate_video(surah, start_verse, end_verse, reciter, is_short, custom_title=custom_title, background_path=background_path)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Check duration for Shorts duration limit (YouTube)
    duration = await run_in_threadpool(get_video_duration, video_details["video"])
    can_upload_to_youtube = True
    if is_short and duration > 60:
        logger.warning(f"Short exceeds 60s ({duration:.2f}s). Skipping YouTube upload.")
        can_upload_to_youtube = False
    
    # Upload to YouTube if requested
    if upload_after_generation and can_upload_to_youtube:
        target_channel_id = await _get_target_youtube_channel_id()
        
        target_playlist_id = None
        if playlist_id == "default":
            target_playlist_id = await _get_playlist_for_reciter(reciter)
        elif playlist_id and playlist_id != "none":
            target_playlist_id = playlist_id
        
        try:
            video_id = await run_in_threadpool(
                upload_to_youtube,
                video_details=video_details,
                target_channel_id=target_channel_id,
                playlist_id=target_playlist_id
            )
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

    # Sleep for 20 seconds before uploading to Facebook if YouTube upload was attempted/enabled
    if upload_after_generation:
        await asyncio.sleep(20)

    # Upload to Facebook if enabled
    await _upload_to_facebook_if_enabled(video_details)

async def create_mushaf_video_job(surah: int, reciter: str, is_short: bool = False, 
                             background_path: str = None,
                             upload_after_generation: bool = False,
                             playlist_id: str = None,
                             custom_title: str = None,
                             lines_per_page: int = 15):
    """Generates a Mushaf-style video and optionally uploads it to YouTube."""
    video_details = await generate_mushaf_video(surah, reciter, is_short, background_path, custom_title=custom_title, lines_per_page=lines_per_page)
    
    if not video_details:
        raise Exception("Error generating Mushaf video")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Check duration for Shorts duration limit (YouTube)
    duration = await run_in_threadpool(get_video_duration, video_details["video"])
    can_upload_to_youtube = True
    if is_short and duration > 60:
        logger.warning(f"Short exceeds 60s ({duration:.2f}s). Skipping YouTube upload.")
        can_upload_to_youtube = False
    
    # Upload to YouTube if requested
    if upload_after_generation and can_upload_to_youtube:
        target_channel_id = await _get_target_youtube_channel_id()
        
        target_playlist_id = None
        if playlist_id == "default":
            target_playlist_id = await _get_playlist_for_reciter(reciter)
        elif playlist_id and playlist_id != "none":
            target_playlist_id = playlist_id
        
        try:
            video_id = await run_in_threadpool(
                upload_to_youtube,
                video_details=video_details,
                target_channel_id=target_channel_id,
                playlist_id=target_playlist_id
            )
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

    # Sleep for 20 seconds before uploading to Facebook if YouTube upload was attempted/enabled
    if upload_after_generation:
        await asyncio.sleep(20)

    # Upload to Facebook if enabled
    await _upload_to_facebook_if_enabled(video_details)

async def manual_upload_to_youtube(video_filename: str, reciter_key: str, playlist_id: str, details_filename: str):
    import os
    import re
    
    target_channel_id = await _get_target_youtube_channel_id() # Fetch channel ID
    
    if video_filename.startswith("quran_shorts_"):
        video_path = os.path.join("exported_data/shorts", video_filename)
        is_short = True
    else:
        video_path = os.path.join("exported_data/videos", video_filename)
        is_short = False
        
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
        "is_short": is_short
    }
    
    try:
        video_id = await run_in_threadpool(
            upload_to_youtube,
            video_details=video_details,
            target_channel_id=target_channel_id,
            playlist_id=playlist_id
        )
        if video_id:
            await update_media_asset_upload(video_path, video_id)
    except Exception as e:
        print(f"YouTube upload failed: {e}")

async def manual_upload_to_facebook(video_filename: str, details_filename: str):
    import os
    
    if video_filename.startswith("quran_shorts_"):
        video_path = os.path.join("exported_data/shorts", video_filename)
    else:
        video_path = os.path.join("exported_data/videos", video_filename)
        
    details_path = os.path.join("exported_data/details", details_filename)
    
    video_details = {
        "video": video_path,
        "info": details_path,
    }
    
    fb_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    fb_page_id = os.getenv("FB_PAGE_ID")
    
    if not fb_token or not fb_page_id:
        print("Facebook credentials missing from environment variables.")
        return

    fb_client = FacebookClient(fb_token, fb_page_id)
    
    # Parse metadata
    title = "Quran Recitation"
    description = ""
    if os.path.exists(details_path):
        try:
            with open(details_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    title = lines[0].strip()
                    description = "".join(lines[1:]).strip()
        except Exception as e:
            print(f"Error reading info file for Facebook upload: {e}")

    try:
        video_id = await run_in_threadpool(
            fb_client.upload_to_facebook,
            video_path=video_path,
            title=title,
            description=description
        )
        if video_id:
            print(f"Manual Facebook upload successful: {video_id}")
    except Exception as e:
        print(f"Facebook manual upload failed: {e}")

async def create_juz_video_job(juz: int, reciter: str, is_short: bool = False, 
                             background_path: str = None,
                             upload_after_generation: bool = False,
                             playlist_id: str = None,
                             custom_title: str = None,
                             lines_per_page: int = 15,
                             start_page: int = None,
                             end_page: int = None):
    """Generates a Juz Mushaf-style video and optionally uploads it to YouTube."""
    logger.info(f"Starting Juz video generation job for Juz {juz}, Reciter: {reciter}, Pages: {start_page}-{end_page}")
    video_details = await generate_juz_video(
        juz, 
        reciter, 
        is_short, 
        background_path, 
        custom_title=custom_title, 
        lines_per_page=lines_per_page,
        start_page=start_page,
        end_page=end_page
    )
    
    if not video_details:
        logger.error(f"Failed to generate Juz video for Juz {juz}")
        raise Exception("Error generating Juz video")
    
    logger.info(f"Juz video generated successfully: {video_details['video']}")
    
    screenshot_path = await run_in_threadpool(extract_frame, video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Persist to database
    await record_media_asset(video_details)
    
    # Check duration for Shorts duration limit (YouTube)
    duration = await run_in_threadpool(get_video_duration, video_details["video"])
    can_upload_to_youtube = True
    if is_short and duration > 60:
        logger.warning(f"Short exceeds 60s ({duration:.2f}s). Skipping YouTube upload.")
        can_upload_to_youtube = False
    
    # Upload to YouTube if requested
    if upload_after_generation and can_upload_to_youtube:
        target_channel_id = await _get_target_youtube_channel_id()
        
        target_playlist_id = None
        if playlist_id == "default":
            target_playlist_id = await _get_playlist_for_reciter(reciter)
        elif playlist_id and playlist_id != "none":
            target_playlist_id = playlist_id
        
        try:
            video_id = await run_in_threadpool(
                upload_to_youtube,
                video_details=video_details,
                target_channel_id=target_channel_id,
                playlist_id=target_playlist_id
            )
            if video_id:
                await update_media_asset_upload(video_details["video"], video_id)
        except Exception as e:
            print(f"YouTube upload failed: {e}")

    # Sleep for 20 seconds before uploading to Facebook if YouTube upload was attempted/enabled
    if upload_after_generation:
        await asyncio.sleep(20)

    # Upload to Facebook if enabled
    await _upload_to_facebook_if_enabled(video_details) 
 a s y n c   d e f   c r e a t e _ m u s h a f _ f a s t _ j o b ( s u r a h :   i n t ,   r e c i t e r :   s t r ,   e n g i n e _ t y p e :   s t r ,   i s _ s h o r t :   b o o l   =   F a l s e ,   b a c k g r o u n d _ p a t h :   s t r   =   N o n e ,   i s _ j u z :   b o o l   =   F a l s e ,   j o b _ i d :   i n t   =   N o n e ) :  
         \  
 \ \ G e n e r a t e s  
 a  
 M u s h a f  
 v i d e o  
 u s i n g  
 a  
 h i g h - s p e e d  
 e n g i n e  
 a n d  
 r e c o r d s  
 p e r f o r m a n c e . \ \ \  
         v i d e o _ d e t a i l s   =   a w a i t   g e n e r a t e _ m u s h a f _ f a s t ( s u r a h ,   r e c i t e r ,   e n g i n e _ t y p e ,   i s _ s h o r t ,   b a c k g r o u n d _ p a t h ,   i s _ j u z = i s _ j u z )  
          
         i f   n o t   v i d e o _ d e t a i l s :  
                 r a i s e   E x c e p t i o n ( \ E r r o r  
 g e n e r a t i n g  
 f a s t  
 M u s h a f  
 v i d e o \ )  
          
         #   R e c o r d   p e r f o r m a n c e   i n   D B   i f   j o b _ i d   i s   p r o v i d e d  
         i f   j o b _ i d :  
                 a s y n c   w i t h   a s y n c _ s e s s i o n ( )   a s   s e s s i o n :  
                         f r o m   d b . m o d e l s   i m p o r t   J o b  
                         j o b   =   a w a i t   s e s s i o n . g e t ( J o b ,   j o b _ i d )  
                         i f   j o b :  
                                 j o b . p e r f o r m a n c e _ r e p o r t   =   j s o n . d u m p s ( v i d e o _ d e t a i l s [ \ p e r f o r m a n c e \ ] )  
                                 a w a i t   s e s s i o n . c o m m i t ( )  
          
         #   P r o c e e d   w i t h   s t a n d a r d   p o s t - g e n e r a t i o n   s t e p s   ( r e c o r d i n g   a s s e t )  
         #   ( N o t e :   s c r e e n s h o t   e x t r a c t i o n   m i g h t   s t i l l   u s e   M o v i e P y / O p e n C V )  
         s c r e e n s h o t _ p a t h   =   a w a i t   r u n _ i n _ t h r e a d p o o l ( e x t r a c t _ f r a m e ,   v i d e o _ p a t h = v i d e o _ d e t a i l s [ \ v i d e o \ ] )  
         v i d e o _ d e t a i l s [ \ s c r e e n s h o t \ ]   =   s c r e e n s h o t _ p a t h  
          
         a w a i t   r e c o r d _ m e d i a _ a s s e t ( v i d e o _ d e t a i l s )  
         r e t u r n   v i d e o _ d e t a i l s  
 