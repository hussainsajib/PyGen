import os
import json
import anyio
from typing import Dict, Optional
from factories.mushaf_fast_render import MushafRenderer
from factories.mushaf_ffmpeg_engine import FFmpegEngine
from factories.mushaf_opencv_engine import OpenCVEngine
from factories.mushaf_pyav_engine import PyAVEngine
from processes.performance import PerformanceMonitor
from processes.mushaf_video import prepare_juz_data_package
from db_ops.crud_mushaf import get_surah_page_range, get_mushaf_page_data, align_mushaf_lines_with_timestamps, get_juz_boundaries, align_mushaf_lines_with_juz_timestamps, group_mushaf_lines_into_scenes
from db_ops.crud_reciters import get_reciter_by_key
from db_ops.crud_surah import read_surah_data
from db_ops.crud_language import fetch_localized_metadata
from db.database import async_session
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from processes.Classes.surah import Surah
from processes.Classes.reciter import Reciter
from factories.video import get_resolution, get_standard_basmallah_clip, make_silence
from moviepy.editor import AudioFileClip, concatenate_audioclips
from config_manager import config_manager
from processes.description import generate_details, generate_juz_details

async def generate_mushaf_fast(surah_number: int, reciter_key: str, engine_type: str, is_short: bool = False, background_path: str = None, custom_title: str = None, is_juz: bool = False, lines_per_page: int = 15, start_page: int = None, end_page: int = None):
    """
    Orchestrates high-speed Mushaf video generation using the specified backend engine.
    """
    monitor = PerformanceMonitor(f"MushafFast_{engine_type}")
    monitor.start()
    
    async with async_session() as session:
        # 1. Fetch Basic Data & Meta
        if not is_juz:
            reciter_db_obj, lang_obj, surah_db_obj = await fetch_localized_metadata(session, surah_number, reciter_key, config_manager)
            if not surah_db_obj or not reciter_db_obj:
                return None
            surah_p = Surah(surah_number)
            reciter_p = Reciter(reciter_key)
            current_language = lang_obj.name if lang_obj else "bengali"
            brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
            
            # Download Audio
            audio_url = read_surah_data(surah_number, reciter_db_obj.database)
            temp_audio = download_mp3_temp(audio_url)
            full_audio = AudioFileClip(temp_audio)
            total_duration = full_audio.duration
            
            # Timestamps
            from db_ops.crud_wbw import get_wbw_timestamps
            wbw_timestamps = {}
            if reciter_db_obj.wbw_database:
                wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
                wbw_timestamps = get_wbw_timestamps(wbw_db_path, surah_number, 1, surah_p.total_ayah)
            
            # Basmallah Injection
            injection_offset_ms = 0
            if surah_number not in [1, 9]:
                try:
                    bsml_audio = get_standard_basmallah_clip()
                    silence_sec = float(config_manager.get("MUSHAF_BASMALLAH_SILENCE_DURATION", "1.0"))
                    silence_audio = make_silence(silence_sec)
                    injection_offset_ms = (bsml_audio.duration + silence_audio.duration) * 1000
                    full_audio = concatenate_audioclips([bsml_audio, silence_audio, full_audio])
                    total_duration = full_audio.duration
                    for key in wbw_timestamps:
                        for seg in wbw_timestamps[key]:
                            seg[1] += injection_offset_ms
                            seg[2] += injection_offset_ms
                except:
                    pass
            
            # Paging
            s_page, e_page = get_surah_page_range(surah_number)
            sorted_pages = list(range(s_page, e_page + 1))
            
            # Aligned Data (Flat for fast render)
            all_aligned_lines = []
            for p_num in sorted_pages:
                p_data = get_mushaf_page_data(p_num)
                # Filter for this surah
                filtered = [l for l in p_data if l["surah_number"] == surah_number or (l["words"] and any(w["surah"] == surah_number for w in l["words"]))]
                aligned = align_mushaf_lines_with_timestamps(filtered, wbw_timestamps)
                all_aligned_lines.extend(aligned)
            
            # Group into Scenes (Handling Page Boundaries)
            scenes = group_mushaf_lines_into_scenes(all_aligned_lines, threshold=3, max_lines=lines_per_page, defer_if_no_ayah=True)
            
            # Shift main recitation timestamps by 5 seconds for intro
            for chunk in scenes:
                for line in chunk:
                    if line.get("start_ms") is not None:
                        line["start_ms"] += 5000
                    if line.get("end_ms") is not None:
                        line["end_ms"] += 5000

            all_page_data = []
            # Prepend Intro
            all_page_data.append((0, [], "intro"))
            
            for chunk in scenes:
                # Use first Ayah's page number if available to ensure correct font loading
                first_ayah = next((l for l in chunk if l.get("line_type") == "ayah"), None)
                p_num = first_ayah.get("page_number") if first_ayah else chunk[0].get("page_number")
                all_page_data.append((p_num, chunk, "main"))
            
            # Append Ending
            all_page_data.append((0, [], "ending"))
                
            reciter_display = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
            surah_display = surah_p.bangla_name if current_language == "bengali" else surah_p.english_name
            
        else:
            # Juz Implementation
            juz_number = surah_number
            boundaries = get_juz_boundaries(juz_number)
            surahs_in_juz = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
            reciter_db_obj, lang_obj, _ = await fetch_localized_metadata(session, surahs_in_juz[0], reciter_key, config_manager)
            current_language = lang_obj.name if lang_obj else "bengali"
            brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
            reciter_p = Reciter(reciter_key)
            
            prep_res = await prepare_juz_data_package(juz_number, reciter_db_obj, boundaries)
            full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, _ = prep_res
            
            # Shift timestamps in all_wbw_timestamps for intro
            for key in all_wbw_timestamps:
                for seg in all_wbw_timestamps[key]:
                    seg[1] += 5000
                    seg[2] += 5000

            # Override sorted_pages if start/end provided
            if start_page is not None and end_page is not None:
                sorted_pages = [p for p in sorted_pages if start_page <= p <= end_page]

            all_aligned_lines = []
            for p_num in sorted_pages:
                p_data = get_mushaf_page_data(p_num)
                aligned = align_mushaf_lines_with_juz_timestamps(p_data, all_wbw_timestamps)
                all_aligned_lines.extend(aligned)
                
            # Group into Scenes (Handling Page Boundaries)
            scenes = group_mushaf_lines_into_scenes(all_aligned_lines, threshold=3, max_lines=lines_per_page, defer_if_no_ayah=False)
            
            all_page_data = []
            # Prepend Intro
            all_page_data.append((0, [], "intro"))
            
            for chunk in scenes:
                p_num = chunk[0].get("page_number")
                all_page_data.append((p_num, chunk, "main"))
            
            # Append Ending
            all_page_data.append((0, [], "ending"))
                
            reciter_display = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
            if current_language == "bengali":
                from factories.single_clip import e2b
                surah_display = f"পারা {e2b(str(juz_number))}"
            else:
                surah_display = f"Juz {juz_number}"

        # 2. Sequence Rendering Phase
        # Prepend and append 5s silence to audio
        intro_silence = make_silence(5.0)
        ending_silence = make_silence(5.0)
        full_audio = concatenate_audioclips([intro_silence, full_audio, ending_silence])
        total_duration = full_audio.duration
        
        output_filename = f"fast_{engine_type}_{'juz' if is_juz else 'surah'}_{surah_number}_{reciter_key.replace('.', '_')}.mp4"
        export_dir = "exported_data/videos"
        os.makedirs(export_dir, exist_ok=True)
        final_output_path = os.path.join(export_dir, output_filename)
        
        # We need a unified audio file for the engine
        audio_export_path = final_output_path + ".audio.mp3"
        full_audio.write_audiofile(audio_export_path, logger=None)
        full_audio.close()
        
        # Initialize Engine
        # We'll wrap the multiple renderers into a SequenceRenderer
        class SequenceRenderer:
            def __init__(self, page_data_list, is_short, font_scale, r_name, s_name, b_name, total_ms, background):
                self.page_data_list = page_data_list # List of (p_num, lines, mode)
                self.renderers = {} # Key: (p_num, mode)
                self.resolution = get_resolution(is_short)
                self.is_short = is_short
                self.font_scale = font_scale
                self.r_name = r_name
                self.s_name = s_name
                self.b_name = b_name
                self.total_ms = total_ms
                self.background = background
                
            def get_frame_at(self, timestamp_sec):
                ts_ms = timestamp_sec * 1000
                
                # Determine which page/mode this timestamp belongs to
                target_data = self.page_data_list[0] # Default to intro
                
                if timestamp_sec < 5.0:
                    target_data = self.page_data_list[0]
                elif timestamp_sec > (self.total_ms / 1000.0) - 5.0:
                    target_data = self.page_data_list[-1]
                else:
                    # Main content
                    for item in self.page_data_list:
                        p_num, lines, mode = item
                        if mode == "main":
                            # Find the first scene that contains this timestamp
                            # Standard alignment ensures lines have absolute global timestamps
                            valid_starts = [l["start_ms"] for l in lines if l.get("start_ms") is not None]
                            if valid_starts:
                                # We use a generous window for main content scenes
                                # This is slightly fuzzy to handle gaps
                                if valid_starts[0] <= ts_ms:
                                    target_data = item
                                    # Don't break yet, keep looking for the LATEST matching scene
                                    # since scenes are sorted chronologically
                    
                p_num, lines, mode = target_data
                cache_key = (p_num, mode)
                
                if cache_key not in self.renderers:
                    # Determine surah number for this page
                    s_num = None
                    if lines:
                        s_num = lines[0].get("surah_number")
                        
                    self.renderers[cache_key] = MushafRenderer(
                        p_num, self.is_short, lines, self.font_scale, self.background,
                        self.r_name, self.s_name, self.b_name, self.total_ms,
                        surah_number=s_num, render_mode=mode
                    )
                return self.renderers[cache_key].get_frame_at(timestamp_sec)

        try:
            font_scale = float(config_manager.get("MUSHAF_FONT_SCALE", "0.8"))
        except:
            font_scale = 0.8
            
        seq_renderer = SequenceRenderer(
            all_page_data, is_short, font_scale, reciter_display, surah_display, brand_name, 
            total_duration * 1000, background_path
        )
        
        if engine_type == "ffmpeg":
            engine = FFmpegEngine(seq_renderer, final_output_path)
        elif engine_type == "opencv":
            engine = OpenCVEngine(seq_renderer, final_output_path)
        elif engine_type == "pyav":
            engine = PyAVEngine(seq_renderer, final_output_path)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
            
        await engine.generate(total_duration, audio_export_path, performance_monitor=monitor)
        
        print(f"\n[SUCCESS] High-speed Mushaf video exported to: {final_output_path}", flush=True)
        
        monitor.stop()
        report = monitor.get_report()
        
        # Cleanup
        if os.path.exists(audio_export_path):
            os.remove(audio_export_path)
        if not is_juz:
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
        else:
            for tf in temp_files: cleanup_temp_file(tf)
            details_path = generate_juz_details(
                juz_number,
                reciter_p,
                offsets,
                is_short,
                language=current_language,
                custom_title=custom_title
            )
            
        return {
            "video": final_output_path,
            "info": details_path,
            "performance": report,
            "surah_number": surah_number if not is_juz else 0,
            "juz_number": surah_number if is_juz else 0,
            "reciter": reciter_key,
            "is_short": is_short
        }
