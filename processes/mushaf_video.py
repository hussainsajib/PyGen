import os
import tempfile
import anyio
import numpy as np
import traceback
from fastapi.concurrency import run_in_threadpool
from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeVideoClip, ColorClip, TextClip, concatenate_audioclips
from db_ops.crud_surah import read_surah_data
from db_ops.crud_reciters import get_reciter_by_key
from db_ops.crud_mushaf import get_surah_page_range, get_mushaf_page_data, align_mushaf_lines_with_timestamps, get_juz_boundaries, align_mushaf_lines_with_juz_timestamps, group_mushaf_lines_into_scenes
from db_ops.crud_wbw import get_wbw_timestamps
from processes.wbw_utils import calculate_juz_offsets
from db_ops.crud_language import fetch_localized_metadata
from db.database import async_session
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from factories.single_clip import generate_background, generate_mushaf_page_clip, generate_reciter_name_clip, generate_surah_info_clip, generate_brand_clip
from factories.video import get_resolution, get_standard_basmallah_clip, make_silence
from processes.video_configs import VIDEO_ENCODING_THREADS, COMMON, FONT_COLOR
from processes.description import generate_details, generate_juz_details
from processes.Classes.surah import Surah
from processes.Classes.reciter import Reciter
from config_manager import config_manager
from sqlalchemy import select
from db.models.language import Language

async def generate_mushaf_video(surah_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, custom_title: str = None, lines_per_page: int = 15):
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
        total_audio_ms = total_duration * 1000
        
        # 3. Fetch Word Timestamps for Highlighting
        if reciter_db_obj.wbw_database:
            wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
            # Fetch timestamps for all ayahs in the surah
            wbw_timestamps = get_wbw_timestamps(wbw_db_path, surah_number, 1, surah_p.total_ayah)
        else:
            wbw_timestamps = {}

        # Handle Basmallah Injection (Audio and visual offset)
        injection_offset_ms = 0
        if surah_number not in [1, 9]:
            try:
                bsml_audio = get_standard_basmallah_clip()
                silence_sec = float(config_manager.get("MUSHAF_BASMALLAH_SILENCE_DURATION", "1.0"))
                silence_audio = make_silence(silence_sec)
                
                injection_offset_ms = (bsml_audio.duration + silence_audio.duration) * 1000
                full_audio = concatenate_audioclips([bsml_audio, silence_audio, full_audio])
                
                # Shift all word timestamps
                for ayah_num in wbw_timestamps:
                    for seg in wbw_timestamps[ayah_num]:
                        seg[1] += injection_offset_ms
                        seg[2] += injection_offset_ms
            except Exception as e:
                print(f"[WARNING] Basmallah injection failed: {e}")

        # --- Intro/Ending Timing ---
        # Shift all main timestamps by 5 seconds for the intro screen
        recitation_start_offset_ms = 5000
        for ayah_num in wbw_timestamps:
            for seg in wbw_timestamps[ayah_num]:
                seg[1] += recitation_start_offset_ms
                seg[2] += recitation_start_offset_ms
        
        # Prepend and append 5s silence to audio
        intro_silence = make_silence(5.0)
        ending_silence = make_silence(5.0)
        full_audio = concatenate_audioclips([intro_silence, full_audio, ending_silence])
        
        total_duration = full_audio.duration
        total_audio_ms = total_duration * 1000
        # ----------------------------

        # 4. Filter and Align Lines
        page_range = get_surah_page_range(surah_number)
        if not page_range or page_range[0] is None:
            full_audio.close()
            cleanup_temp_file(temp_audio)
            return None
            
        start_page, end_page = page_range
        
        all_aligned_lines = []
        for page_num in range(start_page, end_page + 1):
            page_data = get_mushaf_page_data(page_num)
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
            all_aligned_lines.extend(aligned_page)

        # 5. Generate Clips with Global Grouping (Handling Page Boundaries)
        scenes = group_mushaf_lines_into_scenes(all_aligned_lines, threshold=3, max_lines=lines_per_page, defer_if_no_ayah=True)
        
        page_clips = []
        resolution = get_resolution(is_short)
        width, height = resolution
        
        # --- Create Intro Clip ---
        from factories.mushaf_fast_render import MushafRenderer
        try:
            font_scale = float(config_manager.get("MUSHAF_FONT_SCALE", "0.8"))
        except:
            font_scale = 0.8
            
        reciter_display_name = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
        surah_display_name = surah_p.bangla_name if current_language == "bengali" else surah_p.english_name

        intro_renderer = MushafRenderer(
            page_number=start_page, is_short=is_short, lines=[], 
            font_scale=font_scale, background_input=background_path,
            reciter_name=reciter_display_name, surah_name=surah_display_name, 
            brand_name=brand_name, total_duration_ms=total_audio_ms,
            surah_number=surah_number, render_mode="intro"
        )
        intro_frame = intro_renderer.get_frame_at(0)
        intro_clip = ImageClip(intro_frame).set_duration(5.0).set_audio(intro_silence)
        page_clips.append(intro_clip)
        # -------------------------

        for s_idx, chunk in enumerate(scenes):
            try:
                # Use the page number from the first Ayah line to ensure correct font loading
                first_ayah = next((l for l in chunk if l.get("line_type") == "ayah"), None)
                page_num = first_ayah.get("page_number") if first_ayah else chunk[0].get("page_number")
                
                valid_starts = [l["start_ms"] for l in chunk if l["start_ms"] is not None]
                valid_ends = [l["end_ms"] for l in chunk if l["end_ms"] is not None]
                
                if not valid_starts or not valid_ends:
                    # Fallback for empty/unaligned chunks
                    if s_idx == 0:
                        chunk_start_ms = recitation_start_offset_ms
                        chunk_end_ms = recitation_start_offset_ms + 5000
                    else:
                        # Use end of previous chunk if possible, or skip
                        continue
                else:
                    chunk_start_ms = min(valid_starts, default=0)
                    chunk_end_ms = max(valid_ends, default=chunk_start_ms + 5000)
                
                # Adjust timestamps relative to chunk start
                chunk_for_rendering = []
                for line in chunk:
                    line_copy = line.copy()
                    if line_copy["start_ms"] is not None:
                        line_copy["start_ms"] -= chunk_start_ms
                    if line_copy["end_ms"] is not None:
                        line_copy["end_ms"] -= chunk_start_ms
                    
                    # Headers and basmallah should last end of scene
                    if line_copy.get("line_type") in ["surah_name", "basmallah"]:
                        line_copy["start_ms"] = 0
                        line_copy["end_ms"] = (chunk_end_ms - chunk_start_ms)
                        
                    chunk_for_rendering.append(line_copy)

                # Inject Surah Header ONLY on the very first recitation scene
                if s_idx == 0:
                    scene_duration_ms = chunk_end_ms - chunk_start_ms
                    has_header = any(l.get("line_type") == "surah_name" for l in chunk_for_rendering)
                    if not has_header:
                        header_line = {
                            "page_number": page_num,
                            "line_number": 0,
                            "line_type": "surah_name",
                            "is_centered": True,
                            "surah_number": surah_number,
                            "words": [],
                            "start_ms": 0,
                            "end_ms": scene_duration_ms
                        }
                        chunk_for_rendering.insert(0, header_line)

                    if surah_number not in [1, 9]:
                        has_basmallah = any(l.get("line_type") == "basmallah" for l in chunk_for_rendering)
                        if not has_basmallah:
                             insert_idx = 1 if (chunk_for_rendering[0].get("line_type") == "surah_name") else 0
                             bsml_line = {
                                "page_number": page_num,
                                "line_number": 0,
                                "line_type": "basmallah",
                                "is_centered": True,
                                "surah_number": surah_number,
                                "words": [],
                                "start_ms": 0,
                                "end_ms": scene_duration_ms
                             }
                             chunk_for_rendering.insert(insert_idx, bsml_line)

                # Generate Clip
                mushaf_clip = generate_mushaf_page_clip(chunk_for_rendering, page_num, is_short, (chunk_end_ms - chunk_start_ms)/1000.0, background_input=background_path)
                
                # Add Overlays
                # (Re-calculating display names for consistency if needed, already done above)
                
                overlays = []
                if config_manager.get("ENABLE_FOOTER", "True") == "True":
                    # Determine vertical position for footer items
                    text_y = height - 75
                    
                    if config_manager.get("ENABLE_RECITER_INFO", "True") == "True":
                        c = generate_reciter_name_clip(reciter_display_name, is_short, (chunk_end_ms - chunk_start_ms)/1000.0)
                        from processes.video_configs import get_reciter_info_position
                        pos_x_ratio = get_reciter_info_position(is_short, c.w)[0]
                        overlays.append(c.set_position((int(width * pos_x_ratio), text_y)))
                        
                    if config_manager.get("ENABLE_SURAH_INFO", "True") == "True":
                        c = generate_surah_info_clip(surah_display_name, 0, is_short, (chunk_end_ms - chunk_start_ms)/1000.0, language=current_language)
                        overlays.append(c.set_position(('center', text_y)))
                        
                    if config_manager.get("ENABLE_CHANNEL_INFO", "True") == "True":
                        c = generate_brand_clip(brand_name, is_short, (chunk_end_ms - chunk_start_ms)/1000.0)
                        from processes.video_configs import get_channel_info_position
                        pos_x_ratio = get_channel_info_position(is_short, c.w)[0]
                        overlays.append(c.set_position((int(width * pos_x_ratio) - c.w, text_y)))

                # Progress Bar
                start_ratio = chunk_start_ms / total_audio_ms
                end_ratio = chunk_end_ms / total_audio_ms
                progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration((chunk_end_ms - chunk_start_ms)/1000.0).set_position(('center', height-5))
                overlays.append(progress_bar_bg)
                progress_bar_fg = ColorClip(size=(width, 5), color=(0, 200, 0))
                
                def get_progress_width(t, sr=start_ratio, er=end_ratio, dur_ms=(chunk_end_ms-chunk_start_ms)):
                    dur_sec = dur_ms / 1000.0
                    if dur_sec <= 0: return 1
                    p = sr + (er - sr) * (t / dur_sec)
                    w = int(width * max(0.0, min(1.0, p)))
                    return max(1, w)

                progress_bar_fg = progress_bar_fg.resize(newsize=lambda t: (get_progress_width(t), 5))
                progress_bar_fg = progress_bar_fg.set_opacity(0.8).set_duration((chunk_end_ms - chunk_start_ms)/1000.0).set_position(('left', height-5))
                overlays.append(progress_bar_fg)

                # Compose Chunk
                all_chunk_clips = [mushaf_clip] + overlays
                valid_chunk_clips = [c for c in all_chunk_clips if c is not None]
                
                final_chunk_clip = CompositeVideoClip(valid_chunk_clips, size=resolution).set_duration((chunk_end_ms - chunk_start_ms)/1000.0)
                
                audio_start = max(0, chunk_start_ms / 1000.0)
                audio_end = min(total_duration - 0.001, chunk_end_ms / 1000.0)
                if audio_end > audio_start:
                    final_chunk_clip = final_chunk_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                
                page_clips.append(final_chunk_clip)
            except Exception as e:
                print(f"[ERROR] Scene {s_idx} failed: {e}", flush=True)
                traceback.print_exc()
                continue

        # --- Create Ending Clip ---
        ending_renderer = MushafRenderer(
            page_number=end_page, is_short=is_short, lines=[], 
            font_scale=font_scale, background_input=background_path,
            reciter_name=reciter_display_name, surah_name=surah_display_name, 
            brand_name=brand_name, total_duration_ms=total_audio_ms,
            surah_number=surah_number, render_mode="ending"
        )
        ending_frame = ending_renderer.get_frame_at(total_duration - 0.1) # Near end
        ending_clip = ImageClip(ending_frame).set_duration(5.0).set_audio(ending_silence)
        page_clips.append(ending_clip)
        # -------------------------

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
        
        print(f"\n[SUCCESS] Mushaf video exported to: {video_path}", flush=True)
        
        # 7. Generate Details
        await run_in_threadpool(
            generate_details, 
            surah_p, 
            reciter_p, 
            False, 
            1, 
            surah_p.total_ayah, 
            is_short, 
            custom_title,
            current_language
        )
        
        full_audio.close()
        cleanup_temp_file(temp_audio)
        
        return video_path

async def prepare_juz_data_package(juz_number: int, reciter_db_obj, boundaries: dict):
    """
    Downloads and prepares all necessary data for a Juz recitation video.
    """
    surahs_in_juz = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
    temp_files = []
    surah_clips = []
    all_wbw_timestamps = {}
    final_audio_clips = []
    
    # 1. Collect Audio and Timestamps for each Surah
    offsets = {}
    current_offset_ms = 0
    
    for s_num in surahs_in_juz:
        # Handle Basmallah Injection for each Surah
        # Skip for Surah 1 and Surah 9
        if s_num not in [1, 9]:
            try:
                bsml_audio = get_standard_basmallah_clip()
                final_audio_clips.append(bsml_audio)
                current_offset_ms += bsml_audio.duration * 1000
                
                silence_sec = float(config_manager.get("MUSHAF_BASMALLAH_SILENCE_DURATION", "1.0"))
                silence_audio = make_silence(silence_sec)
                final_audio_clips.append(silence_audio)
                current_offset_ms += silence_audio.duration * 1000
            except Exception as e:
                print(f"[WARNING] Basmallah injection failed for Surah {s_num} in Juz: {e}")

        audio_url = read_surah_data(s_num, reciter_db_obj.database)
        if not audio_url: continue
        
        t_mp3 = download_mp3_temp(audio_url)
        if not t_mp3: continue
        temp_files.append(t_mp3)
        
        clip = AudioFileClip(t_mp3)
        surah_clips.append(clip)
        
        # WBW Timestamps
        wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
        v_mapping = boundaries["verse_mapping"][str(s_num)]
        v_range = v_mapping.split("-")
        s_ayah, e_ayah = int(v_range[0]), int(v_range[1])
        
        s_timestamps = get_wbw_timestamps(wbw_db_path, s_num, s_ayah, e_ayah)
        
        if s_timestamps:
            first_ayah_in_juz = min(s_timestamps.keys())
            ayah_1_start = s_timestamps[first_ayah_in_juz][0][1] # Start of first word
            
            for a_num in s_timestamps:
                key = f"{s_num}:{a_num}"
                normalized = []
                for seg in s_timestamps[a_num]:
                    normalized.append([
                        seg[0],
                        (seg[1] - ayah_1_start) + current_offset_ms,
                        (seg[2] - ayah_1_start) + current_offset_ms
                    ])
                all_wbw_timestamps[key] = normalized
        
        offsets[s_num] = current_offset_ms
        
        # Recitation segment duration
        if s_timestamps:
            last_ayah_in_juz = max(s_timestamps.keys())
            first_ayah_in_juz = min(s_timestamps.keys())
            part_duration_ms = s_timestamps[last_ayah_in_juz][-1][2] - s_timestamps[first_ayah_in_juz][0][1]
            
            # Prepare recitation subclip
            start_t = s_timestamps[min(s_timestamps.keys())][0][1] / 1000.0
            end_t = min(clip.duration - 0.001, s_timestamps[max(s_timestamps.keys())][-1][2] / 1000.0)
            final_audio_clips.append(clip.subclip(start_t, end_t))
            
            current_offset_ms += part_duration_ms
        else:
            final_audio_clips.append(clip)
            current_offset_ms += clip.duration * 1000
            
    # 2. Assemble Audio
    full_audio = concatenate_audioclips(final_audio_clips)
    
    # 3. Identify sorted pages
    start_page = boundaries["start_page"]
    end_page = boundaries["end_page"]
    sorted_pages = list(range(start_page, end_page + 1))
    
    return full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, None # initial_bsml no longer separate

async def generate_juz_video(juz_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, lines_per_page: int = 15):
    """
    Generates a continuous Mushaf video for an entire Juz.
    """
    boundaries = get_juz_boundaries(juz_number)
    if not boundaries: return None
    
    surahs_in_juz = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
    surah_set = set(surahs_in_juz)
    
    async with async_session() as session:
        # 1. Localized Metadata
        reciter_db_obj, lang_obj, _ = await fetch_localized_metadata(session, surahs_in_juz[0], reciter_key, config_manager)
        if not reciter_db_obj: return None
        
        reciter_p = Reciter(reciter_key)
        current_language = lang_obj.name if lang_obj else "bengali"
        brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
        
        # 2. Data Package
        prep_res = await prepare_juz_data_package(juz_number, reciter_db_obj, boundaries)
        full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, _ = prep_res
        
        # --- Intro/Ending Timing ---
        recitation_start_offset_ms = 5000
        # Shift all word timestamps in all_wbw_timestamps
        for key in all_wbw_timestamps:
            for seg in all_wbw_timestamps[key]:
                seg[1] += recitation_start_offset_ms
                seg[2] += recitation_start_offset_ms
        
        # Shift Surah offsets as well for accurate metadata
        for s_num in offsets:
            offsets[s_num] += recitation_start_offset_ms
        
        # Prepend and append 5s silence to audio
        intro_silence = make_silence(5.0)
        ending_silence = make_silence(5.0)
        full_audio = concatenate_audioclips([intro_silence, full_audio, ending_silence])
        
        total_duration = full_audio.duration
        total_audio_ms = total_duration * 1000
        # ----------------------------

        # 3. Filter and Align Lines across entire Juz
        all_aligned_lines = []
        for page_num in sorted_pages:
            page_data = get_mushaf_page_data(page_num)
            filtered_page = []
            for line in page_data:
                l_type = line.get("line_type", "ayah")
                line_surah = line.get("surah_number")
                
                if line_surah in surah_set:
                    if l_type == "ayah":
                        filtered_words = []
                        for w in line["words"]:
                            s_id = str(w["surah"])
                            if s_id in boundaries["verse_mapping"]:
                                v_range = boundaries["verse_mapping"][s_id].split("-")
                                if int(v_range[0]) <= w["ayah"] <= int(v_range[1]):
                                    filtered_words.append(w)
                        
                        if filtered_words:
                            line_copy = line.copy()
                            line_copy["words"] = filtered_words
                            filtered_page.append(line_copy)
                    else:
                        filtered_page.append(line.copy())
            
            if filtered_page:
                aligned_page = align_mushaf_lines_with_juz_timestamps(filtered_page, all_wbw_timestamps)
                
                for i, line in enumerate(aligned_page):
                    if line["line_type"] in ["surah_name", "basmallah"] and line.get("start_ms") is None:
                        for j in range(i + 1, len(aligned_page)):
                            if aligned_page[j].get("start_ms") is not None:
                                line["start_ms"] = aligned_page[j]["start_ms"]
                                line["end_ms"] = aligned_page[j]["end_ms"]
                                break
                        
                        if line.get("start_ms") is None:
                            for j in range(i - 1, -1, -1):
                                if aligned_page[j].get("start_ms") is not None:
                                    line["start_ms"] = aligned_page[j]["start_ms"]
                                    line["end_ms"] = aligned_page[j]["end_ms"]
                                    break
                
                all_aligned_lines.extend(aligned_page)

        # 4. Group into Scenes (Handling Page Boundaries)
        scenes = group_mushaf_lines_into_scenes(all_aligned_lines, threshold=3, max_lines=lines_per_page, defer_if_no_ayah=False)
        
        page_clips = []
        resolution = get_resolution(is_short)
        width, height = resolution
        
        # --- Create Intro Clip ---
        from factories.mushaf_fast_render import MushafRenderer
        try:
            font_scale = float(config_manager.get("MUSHAF_FONT_SCALE", "0.8"))
        except:
            font_scale = 0.8
            
        reciter_display_name = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
        if current_language == "bengali":
            from factories.single_clip import e2b
            juz_display_name = f"পারা {e2b(str(juz_number))}"
        else:
            juz_display_name = f"Juz {juz_number}"

        intro_renderer = MushafRenderer(
            page_number=sorted_pages[0], is_short=is_short, lines=[], 
            font_scale=font_scale, background_input=background_path,
            reciter_name=reciter_display_name, surah_name=juz_display_name, 
            brand_name=brand_name, total_duration_ms=total_audio_ms,
            surah_number=surahs_in_juz[0], render_mode="intro"
        )
        intro_frame = intro_renderer.get_frame_at(0)
        intro_clip = ImageClip(intro_frame).set_duration(5.0).set_audio(intro_silence)
        page_clips.append(intro_clip)
        # -------------------------

        global_chunk_idx = 0
        last_processed_ms = float(recitation_start_offset_ms) # Track end of last chunk
        
        for s_idx, chunk in enumerate(scenes):
            try:
                page_num = chunk[0].get("page_number")
                
                # Timing boundaries for chunk
                valid_starts = [l["start_ms"] for l in chunk if l["start_ms"] is not None]
                valid_ends = [l["end_ms"] for l in chunk if l["end_ms"] is not None]
                
                if not valid_starts or not valid_ends:
                    if global_chunk_idx == 0:
                        chunk_start_ms = recitation_start_offset_ms
                        chunk_end_ms = recitation_start_offset_ms + 5000
                    else:
                        continue
                else:
                    if global_chunk_idx == 0:
                        chunk_start_ms = recitation_start_offset_ms
                    else:
                        chunk_start_ms = last_processed_ms
                    
                    chunk_end_ms = max(valid_ends)
                
                last_processed_ms = chunk_end_ms
                
                chunk_duration_sec = (float(chunk_end_ms) - float(chunk_start_ms)) / 1000.0
                if chunk_duration_sec <= 0: continue
                
                chunk_for_rendering = []
                for line in chunk:
                    line_copy = line.copy()
                    if line_copy["start_ms"] is not None:
                        line_copy["start_ms"] -= chunk_start_ms
                    if line_copy["end_ms"] is not None:
                        line_copy["end_ms"] -= chunk_start_ms
                    
                    if line_copy.get("line_type") in ["surah_name", "basmallah"]:
                        line_copy["start_ms"] = 0
                        line_copy["end_ms"] = (chunk_end_ms - chunk_start_ms)
                        
                    chunk_for_rendering.append(line_copy)

                # Generate Clip
                mushaf_clip = await run_in_threadpool(
                    generate_mushaf_page_clip, 
                    chunk_for_rendering, page_num, is_short, chunk_duration_sec, background_input=background_path
                )

                overlays = []
                if config_manager.get("ENABLE_FOOTER", "True") == "True":
                    text_y = height - 75
                    
                    if config_manager.get("ENABLE_RECITER_INFO", "True") == "True":
                        c = await run_in_threadpool(generate_reciter_name_clip, reciter_display_name, is_short, chunk_duration_sec)
                        from processes.video_configs import get_reciter_info_position
                        pos_x_ratio = get_reciter_info_position(is_short, c.w)[0]
                        overlays.append(c.set_position((int(width * pos_x_ratio), text_y)))
                        
                    if config_manager.get("ENABLE_SURAH_INFO", "True") == "True":
                        c = await run_in_threadpool(generate_surah_info_clip, juz_display_name, 0, is_short, chunk_duration_sec, language=current_language)
                        overlays.append(c.set_position(('center', text_y)))
                        
                    if config_manager.get("ENABLE_CHANNEL_INFO", "True") == "True":
                        c = await run_in_threadpool(generate_brand_clip, brand_name, is_short, chunk_duration_sec)
                        from processes.video_configs import get_channel_info_position
                        pos_x_ratio = get_channel_info_position(is_short, c.w)[0]
                        overlays.append(c.set_position((int(width * pos_x_ratio) - c.w, text_y)))
                
                # Progress Bar
                start_ratio = float(chunk_start_ms) / float(total_audio_ms)
                end_ratio = float(chunk_end_ms) / float(total_audio_ms)
                progress_bar_bg = await run_in_threadpool(
                    lambda: ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(chunk_duration_sec).set_position(('center', height-5))
                )
                overlays.append(progress_bar_bg)

                def get_progress_width(t, sr=start_ratio, er=end_ratio, dur=chunk_duration_sec):
                    if dur <= 0: return 1
                    p = sr + (er - sr) * (t / dur)
                    w = int(width * max(0.0, min(1.0, p)))
                    return max(1, w)

                progress_bar_fg = await run_in_threadpool(
                    lambda: ColorClip(size=(width, 5), color=(0, 200, 0)).resize(newsize=lambda t: (get_progress_width(t), 5)).set_opacity(0.8).set_duration(chunk_duration_sec).set_position(('left', height-5))
                )
                overlays.append(progress_bar_fg)

                final_chunk_clip = await run_in_threadpool(
                    lambda: CompositeVideoClip([mushaf_clip] + overlays, size=resolution).set_duration(chunk_duration_sec)
                )

                try:
                    audio_start = max(0.0, float(chunk_start_ms) / 1000.0)
                    audio_end = min(float(total_duration) - 0.001, float(chunk_end_ms) / 1000.0)
                    if float(audio_end) > float(audio_start):
                        final_chunk_clip = await run_in_threadpool(
                            lambda: final_chunk_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                        )
                except:
                    pass

                page_clips.append(final_chunk_clip)
                global_chunk_idx += 1
            except Exception as e:
                print(f"[ERROR] Juz {juz_number} Scene {s_idx} failed: {e}")
                traceback.print_exc()
                continue

        # --- Create Ending Clip ---
        ending_renderer = MushafRenderer(
            page_number=sorted_pages[-1], is_short=is_short, lines=[], 
            font_scale=font_scale, background_input=background_path,
            reciter_name=reciter_display_name, surah_name=juz_display_name, 
            brand_name=brand_name, total_duration_ms=total_audio_ms,
            surah_number=surahs_in_juz[-1], render_mode="ending"
        )
        ending_frame = ending_renderer.get_frame_at(total_duration - 0.1)
        ending_clip = ImageClip(ending_frame).set_duration(5.0).set_audio(ending_silence)
        page_clips.append(ending_clip)
        # -------------------------

        # 5. Final Assembly
        if not page_clips:
            full_audio.close()
            for c in surah_clips: c.close()
            for tf in temp_files: cleanup_temp_file(tf)
            return None

        final_video = await run_in_threadpool(concatenate_videoclips, page_clips, method="compose")
        filename = f"mushaf_juz_{juz_number}_{reciter_key.replace('.', '_')}.mp4"
        export_dir = "exported_data/shorts" if is_short else "exported_data/videos"
        os.makedirs(export_dir, exist_ok=True)
        video_path = os.path.join(export_dir, filename)

        await run_in_threadpool(
            final_video.write_videofile,
            video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=VIDEO_ENCODING_THREADS,
            preset="ultrafast",
            logger="bar"
        )
        
        print(f"\n[SUCCESS] Juz Mushaf video exported to: {video_path}", flush=True)
        
        # 6. Generate Details
        await run_in_threadpool(generate_juz_details, juz_number, reciter_p, offsets, is_short, current_language)
        
        full_audio.close()
        for c in surah_clips: c.close()
        for tf in temp_files: cleanup_temp_file(tf)
        
        return video_path
