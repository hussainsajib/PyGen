import numpy as np

from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger
from processes.Classes import Surah, Reciter
from processes.video_configs import *
from processes.description import generate_details
from config_manager import config_manager
from factories.file import *
from factories.video import make_silence # Import from factories.video

from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation
from db_ops.crud_wbw import get_wbw_timestamps
from db_ops.crud_reciters import get_reciter_by_key
from db.database import async_session
from db.models.language import Language
from sqlalchemy import select
from net_ops.download_file import download_mp3_temp
from processes.surah_video import create_ayah_clip, create_wbw_ayah_clip, create_wbw_advanced_ayah_clip # Import all
from db_ops.crud_language import fetch_localized_metadata
from factories.composite_clip import generate_intro, generate_outro

async def generate_video(surah_number: int, start_verse: int, end_verse: int, reciter_key: str, is_short: bool, custom_title: str = None):
    # Fetch localized metadata (reciter, lang_obj, surah_obj)
    async with async_session() as session:
        reciter_db_obj, lang_obj, surah_db_obj = await fetch_localized_metadata(session, surah_number, reciter_key, config_manager)
    
    # Check if surah was found
    if not surah_db_obj:
        raise ValueError(f"Could not find Surah {surah_number} in the database.")
        
    # Extract info from language object, with fallbacks
    translation_font = lang_obj.font if lang_obj else "arial.ttf"
    brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
    current_language = lang_obj.name if lang_obj else "bengali"
    full_translation_db = lang_obj.full_translation_db if lang_obj and lang_obj.full_translation_db else "rawai_al_bayan"
    
    # Use the fetched Surah and Reciter objects
    surah = surah_db_obj
    reciter = reciter_db_obj # This is the Reciter model instance from DB
    
    # Now proceed with video generation using the fetched localized data
    surah_url = read_surah_data(surah.number, reciter.database)
    if not surah_url:
        raise ValueError(f"Could not find audio URL for Surah {surah.number} and Reciter '{reciter.database}'.")

    downloaded_surah_file = download_mp3_temp(surah_url)

    full_audio = AudioFileClip(downloaded_surah_file)
    
    surah_data = read_text_data(surah.number)
    translation_data = read_translation(surah.number)
    timestamp_data = read_timestamp_data(surah.number, reciter.database)

    if not timestamp_data:
        raise ValueError(f"No timestamp data found for Surah {surah.number} and Reciter '{reciter.database_name}'.")

    # 2. Filter timestamps for the desired verse range
    verse_range_timestamps = [t for t in timestamp_data if start_verse <= t[1] <= end_verse]
    if not verse_range_timestamps:
        raise ValueError(f"No timestamp data found for verses {start_verse}-{end_verse} in Surah {surah.number}.")

    # Fetch WBW data if reciter has it
    wbw_data = {}
    if reciter and reciter.wbw_database:
        print(f"[INFO] - WBW database found: {reciter.wbw_database}", flush=True)
        db_path = os.path.join("databases", "word-by-word", reciter.wbw_database)
        wbw_data = get_wbw_timestamps(db_path, surah_number, start_verse, end_verse)

    active_background = config_manager.get("ACTIVE_BACKGROUND")
    
    clips = []
    
    # 3. Conditionally create Intro
    if not is_short and COMMON["enable_intro"]:
        intro = generate_intro(surah, reciter, active_background, is_short, language=current_language)
        clips.append(intro)
    
    # 4. Loop through the filtered timestamps and create a clip for each ayah
    for tdata in verse_range_timestamps:
        surah_num, ayah, gstart_ms, gend_ms, seg_str = tdata
        try:
            if ayah in wbw_data:
                print(f"[INFO] - Creating Advanced WBW clip for Ayah {ayah}", flush=True)
                clip = create_wbw_advanced_ayah_clip(surah, ayah, reciter, full_audio, is_short=is_short, segments=wbw_data[ayah], background_image_path=active_background, translation_font=translation_font, brand_name=brand_name, language=current_language, full_translation_db=full_translation_db)
                if clip is None:
                    print(f"[INFO] - Falling back to standard clip for Ayah {ayah}", flush=True)
                    clip = create_ayah_clip(surah, ayah, reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short=is_short, background_image_path=active_background, translation_font=translation_font, brand_name=brand_name, language=current_language)
            else:
                clip = create_ayah_clip(surah, ayah, reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short=is_short, background_image_path=active_background, translation_font=translation_font, brand_name=brand_name, language=current_language)
            clips.append(clip)
        except Exception as e:
            logger.error(f"Error creating clip for Surah {surah_num}, Ayah {ayah}: {e}")
            raise

    # 5. Check if clips list is empty before concatenation
    if not clips:
        logger.warning("No valid clips were generated for the given verse range.")
        return None

    if not is_short and COMMON["enable_outro"]:
        outro = generate_outro(None, is_short)
        clips.append(outro)

    final_video = concatenate_videoclips(clips)
    output_path = get_filename(surah_number, start_verse, end_verse, reciter.english_name, is_short)
    
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac", threads=VIDEO_ENCODING_THREADS)
    
    info_file_path = generate_details(surah, reciter, True, start_verse, end_verse, is_short=is_short, custom_title=custom_title)
    
    return {
        "video": output_path, 
        "info": info_file_path, 
        "is_short": is_short, 
        "reciter": reciter.reciter_key,
        "surah_number": surah_number,
        "start_ayah": start_verse,
        "end_ayah": end_verse
    }


def discover_assets(reciters=None):
    import os
    import re
    
    video_dir = "exported_data/videos"
    screenshot_dir = "exported_data/screenshots"
    detail_dir = "exported_data/details"
    
    if not os.path.exists(video_dir):
        return []
        
    videos = []
    
    # List all mp4 files in video_dir
    video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
    
    # Helper to normalize strings for matching
    def normalize(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())

    # Pre-normalize reciter names if provided
    reciter_map = {}
    if reciters:
        for r in reciters:
            # Assuming r is a SQLAlchemy model instance or similar with english_name and playlist_id
            name = getattr(r, 'english_name', None)
            if name:
                reciter_map[normalize(name)] = {
                    "english_name": name,
                    "playlist_id": getattr(r, 'playlist_id', None),
                    "reciter_key": getattr(r, 'reciter_key', None)
                }

    for video_file in video_files:
        # Extract surah and other info from filename
        # Pattern: quran_video_{surah}_{rest}.mp4
        match = re.match(r'quran_video_(\d+)_(.+)\.mp4', video_file)
        if not match:
            continue
            
        surah_num = match.group(1)
        rest = match.group(2)
        
        # Normalize rest (contains range and/or reciter)
        normalized_rest = normalize(rest)
        
        # Check for screenshot
        screenshot_present = False
        if os.path.exists(screenshot_dir):
            screenshot_pattern = f"screenshot_quran_video_{surah_num}_{rest}.png"
            if os.path.exists(os.path.join(screenshot_dir, screenshot_pattern)):
                screenshot_present = True
            else:
                for s_file in os.listdir(screenshot_dir):
                    if s_file.startswith(f"screenshot_quran_video_{surah_num}_") and normalize(s_file) == normalize(f"screenshot_quran_video_{surah_num}_{rest}.png"):
                        screenshot_present = True
                        break

        # Check for details
        details_present = False
        details_filename = ""
        if os.path.exists(detail_dir):
            for d_file in os.listdir(detail_dir):
                if d_file.startswith(f"{surah_num}_") and d_file.endswith(".txt"):
                    d_base = d_file[:-4]
                    if normalize(d_base) in normalized_rest or normalized_rest in normalize(d_base):
                        details_present = True
                        details_filename = d_file
                        break
        
        # Identify reciter and playlist
        reciter_name = re.sub(r'[\d_]+', ' ', rest).strip()
        playlist_id = None
        reciter_key = None
        
        # Try to find a better reciter name and playlist_id from the map
        for norm_name, r_info in reciter_map.items():
            if norm_name in normalized_rest:
                reciter_name = r_info["english_name"]
                playlist_id = r_info["playlist_id"]
                reciter_key = r_info["reciter_key"]
                break

        videos.append({
            "filename": video_file,
            "surah_number": surah_num,
            "reciter": reciter_name,
            "reciter_key": reciter_key,
            "screenshot_present": screenshot_present,
            "details_present": details_present,
            "details_filename": details_filename,
            "playlist_id": playlist_id,
            "playlist_status": playlist_id if playlist_id else "No Playlist"
        })
        
    return videos

