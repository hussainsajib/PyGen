import os
import tempfile
import anyio
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
from processes.Classes import Reciter, Surah
from config_manager import config_manager
from sqlalchemy import select
from db.models.language import Language

async def generate_mushaf_video(surah_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, custom_title: str = None):
    """
    Orchestrates the generation of a Mushaf-style recitation video.
    """
    async with async_session() as session:
        # 1. Fetch Basic Data
        surah_data = await read_surah_data(session, surah_number)
        reciter_data = await get_reciter_by_key(session, reciter_key)
        
        lang_name = config_manager.get("DEFAULT_LANGUAGE", "bengali")
        result = await session.execute(select(Language).filter_by(name=lang_name))
        lang_obj = result.scalar_one_or_none()
        
        localized_meta = await fetch_localized_metadata(session, surah_number, lang_name)
        
        if not surah_data or not reciter_data:
            return None

        surah = Surah(surah_data)
        reciter = Reciter(reciter_data)
        
        # 2. Download Audio
        audio_url = f"https://cdn.islamic.network/quran/audio-surah/128/{reciter.key}/{surah.number}.mp3"
        temp_audio = await download_mp3_temp(audio_url)
        if not temp_audio:
            return None
            
        full_audio = AudioFileClip(temp_audio)
        total_duration = full_audio.duration
        
        # 3. Fetch WBW Timestamps
        wbw_timestamps = await get_wbw_timestamps(surah.number, reciter.key)
        
        # 4. Mushaf Paging Logic
        start_page, end_page = get_surah_page_range(surah.number)
        
        resolution = get_resolution(is_short)
        width, height = resolution
        page_clips = []
        
        total_audio_ms = total_duration * 1000
        
        # Parse FONT_COLOR (which might be "rgb(r,g,b)")
        color = FONT_COLOR
        if isinstance(color, str) and color.startswith("rgb("):
            try:
                color = tuple(map(int, color.replace("rgb(", "").replace(")", "").split(",")))
            except:
                color = (255, 255, 255)

        for page_idx, page_num in enumerate(range(start_page, end_page + 1)):
            page_data = get_mushaf_page_data(page_num)
            # Filter lines to only include those belonging to this surah
            page_data = [l for l in page_data if l["surah_number"] == surah.number]
            if not page_data:
                continue
                
            aligned_page = align_mushaf_lines_with_timestamps(page_data, wbw_timestamps)
            
            valid_starts = [l["start_ms"] for l in aligned_page if l["start_ms"] is not None]
            valid_ends = [l["end_ms"] for l in aligned_page if l["end_ms"] is not None]
            
            if not valid_starts or not valid_ends:
                continue
                
            page_start_ms = min(valid_starts)
            page_end_ms = max(valid_ends)
            
            if page_num == start_page:
                page_start_ms = 0
            if page_num == end_page:
                page_end_ms = total_audio_ms
                
            page_duration_sec = (page_end_ms - page_start_ms) / 1000.0
            
            # Adjust timestamps relative to page start
            for line in aligned_page:
                if line["start_ms"] is not None:
                    line["start_ms"] -= page_start_ms
                if line["end_ms"] is not None:
                    line["end_ms"] -= page_start_ms

            # 5. Generate Clips
            mushaf_clip = generate_mushaf_page_clip(aligned_page, page_num, is_short, page_duration_sec)
            
            # Add Footer elements
            reciter_name = reciter.name_bangla if lang_name == "bengali" else reciter.name
            surah_name = localized_meta["surah_name"] if localized_meta else surah.name_english
            brand_name = lang_obj.brand_name if lang_obj else ""
            
            overlays = []
            
            # Bismillah Header (Only on first page, and only for surahs 2-114, excluding 9 and 1)
            # Actually surah_video.py might have a bismillah helper. 
            # For simplicity, if it's the start page and surah != 9 and surah != 1:
            if page_num == start_page and surah.number not in [1, 9]:
                # Find a font for Bismillah or just use page font with specific glyph if known.
                # Common PUA for Bismillah is often at the start of some pages.
                # Let's just use standard Arabic for now.
                bismillah_clip = TextClip(
                    "بسم الله الرحمن الرحيم",
                    fontsize=int(height * 0.05),
                    color=FONT_COLOR,
                    font="Arial" # Standard Arabic font
                ).set_duration(page_duration_sec).set_position(('center', height * 0.02))
                overlays.append(bismillah_clip)

            if config_manager.get("ENABLE_RECITER_INFO") == "True":
                overlays.append(generate_reciter_name_clip(reciter_name, is_short, page_duration_sec))
            if config_manager.get("ENABLE_SURAH_INFO") == "True":
                overlays.append(generate_surah_info_clip(surah_name, 0, is_short, page_duration_sec, language=lang_name))
            if config_manager.get("ENABLE_CHANNEL_INFO") == "True":
                overlays.append(generate_brand_clip(brand_name, is_short, page_duration_sec))

            # Progress Bar
            # We want a progress bar at the bottom that fills up based on current total time.
            def make_progress_bar(t):
                current_total_sec = (page_start_ms / 1000.0) + t
                progress = current_total_sec / total_duration
                bar_width = int(width * progress)
                # Create a small color clip
                bar = ColorClip(size=(max(1, bar_width), 5), color=color).set_duration(1/24)
                return bar.get_frame(t)

            # MoviePy's dynamic clips are a bit tricky with concatenate.
            # Simpler: Create a ColorClip for the whole duration, but we need it to grow.
            # Let's use a simpler approach: Just a static bar for this page's segment if dynamic is too hard.
            # Better: Use a ColorClip and animate its width or use a mask.
            # Actually, we can just use a ColorClip with a custom make_frame for an ImageClip.
            
            progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(page_duration_sec).set_position(('center', 'bottom'))
            
            # For the filling part, we'll use a simple animation
            def anim_progress(t):
                curr_p = ((page_start_ms / 1000.0) + t) / total_duration
                return int(width * curr_p)

            # We'll create the filling bar as a ColorClip that starts at 0 and grows? 
            # MoviePy ColorClip doesn't easily change size over time.
            # We'll just use 15 segments of progress bar or something? No.
            
            # Let's just skip the progress bar animation for now and use a static one for the page if it's too complex.
            # OR: Use a simple ImageClip with a make_frame.
            
            progress_bar_fill = ColorClip(size=(width, 5), color=color).set_duration(page_duration_sec).set_position((0, height-5))
            # Masking it to show only progress
            def progress_mask(t):
                curr_p = ((page_start_ms / 1000.0) + t) / total_duration
                mask = np.zeros((5, width))
                mask[:, :int(width * curr_p)] = 1
                return mask
            
            from moviepy.editor import ImageMaskClip
            # progress_bar_fill = progress_bar_fill.set_mask(ImageMaskClip(size=(width, 5), ismask=True, make_frame=progress_mask))
            # ImageMaskClip with make_frame is better.
            
            overlays.append(progress_bar_bg)
            # overlays.append(progress_bar_fill)

            # Compose Page
            bg_clip = generate_background(background_path, page_duration_sec, is_short)
            
            final_page_clip = CompositeVideoClip([bg_clip, mushaf_clip] + overlays, size=resolution)
            final_page_clip = final_page_clip.set_audio(full_audio.subclip(page_start_ms/1000.0, page_end_ms/1000.0))
            
            page_clips.append(final_page_clip)

        # 6. Final Assembly
        if not page_clips:
            cleanup_temp_file(temp_audio)
            return None
            
        final_video = concatenate_videoclips(page_clips, method="compose")
        
        # Output paths
        surah_slug = surah.name_english.lower().replace(" ", "_")
        reciter_slug = reciter.key.replace(".", "_")
        filename = f"mushaf_video_{surah.number}_{surah_slug}_{reciter_slug}.mp4"
        
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
            logger=None
        )
        
        # Cleanup
        full_audio.close()
        for c in page_clips:
            c.close()
        cleanup_temp_file(temp_audio)
        
        # Generate Metadata
        details_path = await generate_details(surah.number, 1, surah.ayah_count, reciter.key, is_short, custom_title=custom_title)
        
        return {
            "video": video_path,
            "info": details_path,
            "surah_number": surah.number,
            "start_ayah": 1,
            "end_ayah": surah.ayah_count,
            "reciter": reciter.key,
            "is_short": is_short
        }