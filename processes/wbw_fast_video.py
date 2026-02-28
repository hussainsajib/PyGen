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

from factories.wbw_fast_render import WBWFastRenderer, FastWBWVideoRenderer
from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation, get_full_translation_for_ayah
from db_ops.crud_wbw import get_wbw_timestamps, get_wbw_text_for_ayah, get_wbw_translation_for_ayah
from processes.wbw_utils import segment_words_with_timestamps
from net_ops.download_file import download_mp3_temp
from moviepy.editor import AudioFileClip, concatenate_audioclips
from factories.video import make_silence

# ... (MoviePyRenderer class remains)

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
    translation_font = lang_obj.font if lang_obj else "arial.ttf"
    brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"

    export_dir = "exported_data/videos"
    os.makedirs(export_dir, exist_ok=True)
    
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

    # 2. Main WBW Video
    main_path = os.path.join(temp_dir, "main.mp4")
    
    if engine_type == "pillow_opencv":
        # --- NEW FAST PATH ---
        # Fetch all required data
        surah_url = read_surah_data(surah_number, reciter_db_obj.database)
        downloaded_surah_file = download_mp3_temp(surah_url)
        full_audio = AudioFileClip(downloaded_surah_file)
        
        timestamp_data = read_timestamp_data(surah_number, reciter_db_obj.database)
        verse_range_timestamps = [t for t in timestamp_data if start_verse <= t[1] <= end_verse]
        
        db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
        wbw_timestamps = get_wbw_timestamps(db_path, surah_number, start_verse, end_verse)
        
        text_db = "databases/text/qpc-hafs-word-by-word.db"
        if current_language == "bengali":
            trans_db = os.path.abspath("databases/translation/bengali/bangali-word-by-word-translation.sqlite")
        else:
            trans_db = os.path.abspath(f"databases/translation/{current_language}/word-by-word-translation.sqlite")

        interlinear_enabled = config_manager.get("WBW_INTERLINEAR_ENABLED", "False") == "True"
        layout = "interlinear" if interlinear_enabled else "standard"
        
        delay_sec = float(config_manager.get("WBW_DELAY_BETWEEN_AYAH", 0.5))
        
        scenes = []
        audio_clips = []
        current_global_sec = 0.0
        
        for tdata in verse_range_timestamps:
            ayah = tdata[1]
            segments = wbw_timestamps.get(ayah, [])
            if not segments: continue
            
            arabic_words = get_wbw_text_for_ayah(text_db, surah_number, ayah)
            trans_words = get_wbw_translation_for_ayah(trans_db, surah_number, ayah)
            
            # Duration for this ayah
            ayah_duration = (segments[-1][2] - segments[0][1]) / 1000.0
            
            scene_data = {
                "words": arabic_words,
                "translations": trans_words,
                "start_ms": 0,
                "end_ms": int(ayah_duration * 1000),
                "word_segments": [{"start_ms": int(s[1] - segments[0][1]), "end_ms": int(s[2] - segments[0][1])} for s in segments],
                "reciter_name": reciter_db_obj.english_name,
                "surah_name": surah_db_obj.english_name,
                "verse_number": ayah,
                "brand_name": brand_name,
                "is_short": is_short,
                "layout": layout
            }
            
            renderer = WBWFastRenderer(scene_data, background_path=active_background)
            scenes.append({
                "start_sec": current_global_sec,
                "end_sec": current_global_sec + ayah_duration,
                "renderer": renderer
            })
            
            # Audio subclip
            ayah_audio = full_audio.subclip(segments[0][1] / 1000.0, segments[-1][2] / 1000.0)
            audio_clips.append(ayah_audio)
            
            current_global_sec += ayah_duration
            
            if delay_sec > 0:
                # Add delay scene (blank or last frame)
                # For now, just extend the last scene's duration but without word highlights
                scenes[-1]["end_sec"] += delay_sec
                audio_clips.append(make_silence(delay_sec))
                current_global_sec += delay_sec
        
        final_audio_path = os.path.join(temp_dir, "main_audio.m4a")
        final_audio = concatenate_audioclips(audio_clips)
        await run_in_threadpool(final_audio.write_audiofile, final_audio_path, fps=44100, codec="aac", logger=None)
        
        multi_renderer = FastWBWVideoRenderer(scenes, is_short=is_short)
        engine = FFmpegEngine(renderer=multi_renderer, output_path=main_path, fps=24)
        
        await engine.generate(
            duration_sec=current_global_sec, 
            audio_path=final_audio_path, 
            performance_monitor=monitor
        )
        
    else:
        # --- OLD MOVIEPY PATH ---
        main_clip, _, _, _ = await build_wbw_video_clip(
            surah_number, start_verse, end_verse, reciter_key, is_short, background_path, include_intro_outro=False
        )
        
        if not main_clip:
            return None
            
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

    # 3. Outro
    # ...


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
