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
        reciter_db_obj, lang_obj, surah_db_obj = await fetch_localized_metadata(session, surah_number, reciter_key, config_manager)
        
        if not surah_db_obj or not reciter_db_obj:
            return None

        surah_p = Surah(surah_number)
        reciter_p = Reciter(reciter_key)
        
        current_language = lang_obj.name if lang_obj else "bengali"
        brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
        
        # 2. Download Audio
        audio_url = read_surah_data(surah_number, reciter_db_obj.database)
        if not audio_url:
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
            wbw_timestamps = get_wbw_timestamps(wbw_db_path, surah_number, 1, surah_p.total_ayah)
        
        # 4. Mushaf Paging Logic
        page_range = get_surah_page_range(surah_number)
        if not page_range or page_range[0] is None:
            full_audio.close()
            cleanup_temp_file(temp_audio)
            return None
            
        start_page, end_page = page_range
        resolution = get_resolution(is_short)
        width, height = resolution
        page_clips = []
        
        total_audio_ms = total_duration * 1000

        for page_num in range(start_page, end_page + 1):
            try:
                page_data = get_mushaf_page_data(page_num)
                # Improved surah line detection
                filtered_page = []
                for line in page_data:
                    if line["surah_number"] == surah_number:
                        filtered_page.append(line)
                    elif line["words"]:
                        if any(w["surah"] == surah_number for w in line["words"]):
                            filtered_page.append(line)
                
                if not filtered_page:
                    continue
                    
                aligned_page = align_mushaf_lines_with_timestamps(filtered_page, wbw_timestamps)
                
                valid_starts = [l["start_ms"] for l in aligned_page if l["start_ms"] is not None]
                valid_ends = [l["end_ms"] for l in aligned_page if l["end_ms"] is not None]
                
                if not valid_starts or not valid_ends:
                    if page_num == start_page:
                        page_start_ms = 0
                        page_end_ms = 5000 # Default 5s
                    else:
                        continue
                else:
                    page_start_ms = min(valid_starts, default=0)
                    page_end_ms = max(valid_ends, default=page_start_ms + 5000)
                
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
                reciter_display_name = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
                surah_display_name = surah_p.bangla_name if current_language == "bengali" else surah_p.english_name
                
                overlays = []
                if page_num == start_page and surah_number not in [1, 9]:
                    bismillah_clip = TextClip(
                        "بسم الله الرحمن الرحيم",
                        fontsize=int(height * 0.05),
                        color=FONT_COLOR,
                        font="Arial"
                    ).set_duration(page_duration_sec).set_position(('center', height * 0.02))
                    overlays.append(bismillah_clip)

                if config_manager.get("ENABLE_RECITER_INFO") == "True":
                    overlays.append(generate_reciter_name_clip(reciter_display_name, is_short, page_duration_sec))
                if config_manager.get("ENABLE_SURAH_INFO") == "True":
                    overlays.append(generate_surah_info_clip(surah_display_name, 0, is_short, page_duration_sec, language=current_language))
                if config_manager.get("ENABLE_CHANNEL_INFO") == "True":
                    overlays.append(generate_brand_clip(brand_name, is_short, page_duration_sec))

                progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(page_duration_sec).set_position(('center', height-5))
                overlays.append(progress_bar_bg)

                # Compose Page
                bg_clip = generate_background(background_path, page_duration_sec, is_short)
                
                all_page_clips = [bg_clip, mushaf_clip] + overlays
                valid_page_clips = [c for c in all_page_clips if c is not None]
                
                if not valid_page_clips:
                    continue
                    
                final_page_clip = CompositeVideoClip(valid_page_clips, size=resolution).set_duration(page_duration_sec)
                
                audio_start = max(0, page_start_ms / 1000.0)
                audio_end = min(total_duration, page_end_ms / 1000.0)
                if audio_end > audio_start:
                    final_page_clip = final_page_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                
                page_clips.append(final_page_clip)
            except Exception as e:
                print(f"[ERROR] Page {page_num} failed: {e}", flush=True)
                continue

        # 6. Final Assembly
        if not page_clips:
            full_audio.close()
            cleanup_temp_file(temp_audio)
            return None
            
        final_video = concatenate_videoclips(page_clips, method="compose")
        
        surah_slug = surah_p.english_name.lower().replace(" ", "_")
        reciter_slug = reciter_key.replace(".", "_")
        filename = f"mushaf_video_{surah_number}_{surah_slug}_{reciter_slug}.mp4"
        
        export_dir = "exported_data/shorts" if is_short else "exported_data/videos"
        os.makedirs(export_dir, exist_ok=True)
        video_path = os.path.join(export_dir, filename)
        
        # Write Video
        final_video.write_videofile(
            video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=VIDEO_ENCODING_THREADS,
            preset="ultrafast",
            logger="bar"
        )
        
        full_audio.close()
        for c in page_clips:
            c.close()
        cleanup_temp_file(temp_audio)
        
        details_path = generate_details(
            surah_p, 
            reciter_p, 
            False, 
            1, 
            surah_p.total_ayah, 
            is_short, 
            custom_title=custom_title,
            language=current_language
        )
        
        return {
            "video": video_path,
            "info": details_path,
            "surah_number": surah_number,
            "start_ayah": 1,
            "end_ayah": surah_p.total_ayah,
            "reciter": reciter_key,
            "is_short": is_short
        }
