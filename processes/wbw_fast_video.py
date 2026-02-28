import os
import tempfile
import asyncio
from fastapi.concurrency import run_in_threadpool
from factories.mushaf_ffmpeg_engine import FFmpegEngine
from processes.performance import PerformanceMonitor
from processes.video_configs import COMMON, VIDEO_ENCODING_THREADS
from db.database import async_session
from db_ops.crud_language import fetch_localized_metadata
from config_manager import config_manager
from factories.composite_clip import generate_intro, generate_outro
from processes.video_utils import build_wbw_video_clip
from processes.description import generate_details
from factories.file import get_filename

class MoviePyRenderer:
    def __init__(self, clip):
        self.clip = clip
        self.resolution = tuple(clip.size)
        
    def get_frame_at(self, timestamp_sec):
        return self.clip.get_frame(timestamp_sec)

async def generate_wbw_fast(
    surah_number: int, 
    start_verse: int, 
    end_verse: int, 
    reciter_key: str, 
    engine_type: str, 
    is_short: bool = False, 
    background_path: str = None, 
    custom_title: str = None
):
    """
    High-speed Word-by-Word video generation using FFmpeg pipeline.
    """
    monitor = PerformanceMonitor(f"WBWFast_{engine_type}")
    monitor.start()

    # Fetch localized metadata
    async with async_session() as session:
        reciter_db_obj, lang_obj, surah_db_obj = await fetch_localized_metadata(session, surah_number, reciter_key, config_manager)
    
    current_language = lang_obj.name if lang_obj else "bengali"
    active_background = background_path if background_path else config_manager.get("ACTIVE_BACKGROUND")

    export_dir = "exported_data/videos"
    os.makedirs(export_dir, exist_ok=True)
    
    # We use get_filename to maintain consistency, but replace 'quran_video' with 'fast_ffmpeg_wbw' if needed.
    # Actually, let's keep the standard naming so the UI finds it easily, but we'll prepend 'fast_' to identify it.
    std_filename = os.path.basename(get_filename(surah_number, start_verse, end_verse, reciter_db_obj.english_name, is_short))
    video_filename = f"fast_{engine_type}_{std_filename}"
    final_output_path = os.path.join(export_dir, video_filename)
    
    temp_dir = tempfile.mkdtemp()
    video_parts = []

    # 1. Conditionally generate and write Intro
    if not is_short and COMMON.get("enable_intro", True):
        intro_clip = generate_intro(surah_db_obj, reciter_db_obj, active_background, is_short, language=current_language)
        intro_path = os.path.join(temp_dir, "intro.mp4")
        await run_in_threadpool(
            intro_clip.write_videofile, intro_path, codec='libx264', fps=24, audio_codec="aac", 
            threads=VIDEO_ENCODING_THREADS, preset="ultrafast", logger=None
        )
        video_parts.append(intro_path)

    # 2. Main WBW Video using fast FFmpeg pipeline
    main_clip, _, _, _ = await build_wbw_video_clip(
        surah_number, start_verse, end_verse, reciter_key, is_short, background_path, include_intro_outro=False
    )
    
    if not main_clip:
        return None
        
    main_path = os.path.join(temp_dir, "main.mp4")
    
    # Save audio temporarily
    audio_path = os.path.join(temp_dir, "main_audio.m4a")
    if main_clip.audio:
        await run_in_threadpool(main_clip.audio.write_audiofile, audio_path, fps=44100, codec="aac", logger=None)
    else:
        audio_path = None
        
    renderer = MoviePyRenderer(main_clip)
    engine = FFmpegEngine(renderer=renderer, output_path=main_path, fps=24)
    
    await engine.generate(
        duration_sec=main_clip.duration, 
        audio_path=audio_path, 
        performance_monitor=monitor
    )
    
    video_parts.append(main_path)

    # 3. Conditionally generate and write Outro
    if not is_short and COMMON.get("enable_outro", True):
        outro_clip = generate_outro(active_background, is_short)
        outro_path = os.path.join(temp_dir, "outro.mp4")
        await run_in_threadpool(
            outro_clip.write_videofile, outro_path, codec='libx264', fps=24, audio_codec="aac", 
            threads=VIDEO_ENCODING_THREADS, preset="ultrafast", logger=None
        )
        video_parts.append(outro_path)

    # 4. Concatenate all parts
    if len(video_parts) > 1:
        await run_in_threadpool(FFmpegEngine.concat_videos, video_parts, final_output_path)
    elif video_parts:
        import shutil
        shutil.copy(video_parts[0], final_output_path)
        
    info_file_path = generate_details(surah_db_obj, reciter_db_obj, True, start_verse, end_verse, is_short=is_short, custom_title=custom_title, language=current_language)

    monitor.stop()

    return {
        "video": final_output_path,
        "info": info_file_path,
        "performance": monitor.get_report(),
        "surah_number": surah_number,
        "reciter": reciter_db_obj.reciter_key,
        "is_short": is_short,
        "start_ayah": start_verse,
        "end_ayah": end_verse
    }
