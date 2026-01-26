import os
import tempfile
import anyio
import numpy as np
from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeVideoClip, ColorClip, TextClip
from db_ops.crud_surah import read_surah_data
from db_ops.crud_reciters import get_reciter_by_key
from db_ops.crud_mushaf import get_surah_page_range, get_mushaf_page_data, align_mushaf_lines_with_timestamps
from db_ops.crud_wbw import get_wbw_timestamps
from db_ops.crud_language import fetch_localized_metadata
from db.database import async_session
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from factories.single_clip import generate_background, generate_mushaf_page_clip, generate_reciter_name_clip, generate_surah_info_clip, generate_brand_clip
from factories.video import get_resolution
from processes.video_configs import VIDEO_ENCODING_THREADS, COMMON, FONT_COLOR
from processes.description import generate_details
from processes.Classes.surah import Surah
from processes.Classes.reciter import Reciter
from config_manager import config_manager
from sqlalchemy import select
from db.models.language import Language

async def generate_mushaf_video(surah_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, custom_title: str = None):
    """
    Orchestrates the generation of a Mushaf-style recitation video.
    """
    async with async_session() as session:
        # 1. Fetch Basic Data
        surah = Surah(surah_number)
        
        # Get reciter model from DB for database filenames
        reciter_db_obj = await get_reciter_by_key(session, reciter_key)
        if not reciter_db_obj:
            return None
            
        reciter = Reciter(reciter_key)
        
        lang_name = config_manager.get("DEFAULT_LANGUAGE", "bengali")
        result = await session.execute(select(Language).filter_by(name=lang_name))
        lang_obj = result.scalar_one_or_none()
        
        localized_meta = await fetch_localized_metadata(session, surah_number, lang_name)
        
        # 2. Download Audio
        # Use read_surah_data which correctly looks up the audio_url in the reciter's database
        audio_url = read_surah_data(surah.number, reciter_db_obj.database)
        if not audio_url:
            print(f"DEBUG: Audio URL not found for Surah {surah.number} and Reciter {reciter_key}")
            return None
            
        temp_audio = download_mp3_temp(audio_url)
        if not temp_audio:
            return None
            
        full_audio = AudioFileClip(temp_audio)
        total_duration = full_audio.duration
        
        # 3. Fetch WBW Timestamps
        wbw_timestamps = {}
        if reciter_db_obj.wbw_database:
            wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
            wbw_timestamps = get_wbw_timestamps(wbw_db_path, surah.number, 1, surah.total_ayah)
        
        # 4. Mushaf Paging Logic
        start_page, end_page = get_surah_page_range(surah.number)
        
        resolution = get_resolution(is_short)
        width, height = resolution
        page_clips = []
        
        total_audio_ms = total_duration * 1000
        
        # Parse FONT_COLOR
        color = FONT_COLOR
        if isinstance(color, str) and color.startswith("rgb("):
            try:
                color = tuple(map(int, color.replace("rgb(", "").replace(")", "").split(",")))
            except:
                color = (255, 255, 255)

        for page_num in range(start_page, end_page + 1):
            page_data = get_mushaf_page_data(page_num)
            page_data = [l for l in page_data if l["surah_number"] == surah.number]
            if not page_data:
                continue
                
            aligned_page = align_mushaf_lines_with_timestamps(page_data, wbw_timestamps)
            
            valid_starts = [l["start_ms"] for l in aligned_page if l["start_ms"] is not None]
            valid_ends = [l["end_ms"] for l in aligned_page if l["end_ms"] is not None]
            
            if not valid_starts or not valid_ends:
                # If no word-level timing, we skip highlighting but still show the page?
                # For now, if it's the first page of surah (e.g. Al-Fatihah), we might have Bismillah etc.
                if page_num == start_page:
                    page_start_ms = 0
                    page_end_ms = min(valid_starts) if valid_starts else 5000 # Fallback 5s
                else:
                    continue
            else:
                page_start_ms = min(valid_starts)
                page_end_ms = max(valid_ends)
            
            if page_num == start_page:
                page_start_ms = 0
            if page_num == end_page:
                page_end_ms = total_audio_ms
                
            page_duration_sec = (page_end_ms - page_start_ms) / 1000.0
            if page_duration_sec <= 0:
                continue
            
            # Adjust timestamps relative to page start
            for line in aligned_page:
                if line["start_ms"] is not None:
                    line["start_ms"] -= page_start_ms
                if line["end_ms"] is not None:
                    line["end_ms"] -= page_start_ms

            # 5. Generate Clips
            mushaf_clip = generate_mushaf_page_clip(aligned_page, page_num, is_short, page_duration_sec)
            
            # Add Overlays
            reciter_name = reciter.bangla_name if lang_name == "bengali" else reciter.english_name
            surah_name = localized_meta["surah_name"] if localized_meta else surah.english_name
            brand_name = lang_obj.brand_name if lang_obj else ""
            
            overlays = []
            
            if page_num == start_page and surah.number not in [1, 9]:
                bismillah_clip = TextClip(
                    "بسم الله الرحمن الرحيم",
                    fontsize=int(height * 0.05),
                    color=FONT_COLOR,
                    font="Arial"
                ).set_duration(page_duration_sec).set_position(('center', height * 0.02))
                overlays.append(bismillah_clip)

            if config_manager.get("ENABLE_RECITER_INFO") == "True":
                overlays.append(generate_reciter_name_clip(reciter_name, is_short, page_duration_sec))
            if config_manager.get("ENABLE_SURAH_INFO") == "True":
                overlays.append(generate_surah_info_clip(surah_name, 0, is_short, page_duration_sec, language=lang_name))
            if config_manager.get("ENABLE_CHANNEL_INFO") == "True":
                overlays.append(generate_brand_clip(brand_name, is_short, page_duration_sec))

            progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(page_duration_sec).set_position(('center', height-5))
            overlays.append(progress_bar_bg)

            # Compose Page
            bg_clip = generate_background(background_path, page_duration_sec, is_short)
            
            final_page_clip = CompositeVideoClip([bg_clip, mushaf_clip] + overlays, size=resolution)
            final_page_clip = final_page_clip.set_audio(full_audio.subclip(page_start_ms/1000.0, page_end_ms/1000.0))
            
            page_clips.append(final_page_clip)

        # 6. Final Assembly
        if not page_clips:
            full_audio.close()
            cleanup_temp_file(temp_audio)
            return None
            
        final_video = concatenate_videoclips(page_clips, method="compose")
        
        surah_slug = surah.english_name.lower().replace(" ", "_")
        reciter_slug = reciter_key.replace(".", "_")
        filename = f"mushaf_video_{surah.number}_{surah_slug}_{reciter_slug}.mp4"
        
        export_dir = "exported_data/shorts" if is_short else "exported_data/videos"
        os.makedirs(export_dir, exist_ok=True)
        video_path = os.path.join(export_dir, filename)
        
        final_video.write_videofile(
            video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=VIDEO_ENCODING_THREADS,
            logger=None
        )
        
        full_audio.close()
        for c in page_clips:
            c.close()
        cleanup_temp_file(temp_audio)
        
        # Determine language for details
        lang_name = config_manager.get("DEFAULT_LANGUAGE", "bengali")
        
        details_path = generate_details(
            surah, 
            reciter, 
            False, # has_translation
            1, 
            surah.total_ayah, 
            is_short, 
            custom_title=custom_title,
            language=lang_name
        )
        
        return {
            "video": video_path,
            "info": details_path,
            "surah_number": surah.number,
            "start_ayah": 1,
            "end_ayah": surah.total_ayah,
            "reciter": reciter_key,
            "is_short": is_short
        }
