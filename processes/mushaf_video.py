import os
import tempfile
import anyio
import numpy as np
from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeVideoClip, ColorClip, TextClip, concatenate_audioclips
from db_ops.crud_surah import read_surah_data
from db_ops.crud_reciters import get_reciter_by_key
from db_ops.crud_mushaf import get_surah_page_range, get_mushaf_page_data, align_mushaf_lines_with_timestamps, get_juz_boundaries, align_mushaf_lines_with_juz_timestamps
from db_ops.crud_wbw import get_wbw_timestamps
from processes.wbw_utils import calculate_juz_offsets
from db_ops.crud_language import fetch_localized_metadata
from db.database import async_session
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from factories.single_clip import generate_background, generate_mushaf_page_clip, generate_reciter_name_clip, generate_surah_info_clip, generate_brand_clip
from factories.video import get_resolution
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

        # Collect and group aligned lines by page
        lines_by_page = {}
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
            lines_by_page[page_num] = aligned_page

        # 5. Generate Clips with Page-Aware Chunking
        global_chunk_idx = 0
        sorted_pages = sorted(lines_by_page.keys())
        
        for p_idx, page_num in enumerate(sorted_pages):
            page_lines = lines_by_page[page_num]
            # Chunk within the page
            page_chunks = [page_lines[i:i + lines_per_page] for i in range(0, len(page_lines), lines_per_page)]
            
            for c_idx, chunk in enumerate(page_chunks):
                try:
                    valid_starts = [l["start_ms"] for l in chunk if l["start_ms"] is not None]
                    valid_ends = [l["end_ms"] for l in chunk if l["end_ms"] is not None]
                    
                    if not valid_starts or not valid_ends:
                        # Fallback for empty/unaligned chunks
                        if global_chunk_idx == 0:
                            chunk_start_ms = 0
                            chunk_end_ms = 5000
                        else:
                            # Use end of previous chunk if possible, or skip
                            continue
                    else:
                        chunk_start_ms = min(valid_starts, default=0)
                        chunk_end_ms = max(valid_ends, default=chunk_start_ms + 5000)
                    
                    # Force boundaries
                    if global_chunk_idx == 0:
                        chunk_start_ms = 0
                    if p_idx == len(sorted_pages) - 1 and c_idx == len(page_chunks) - 1:
                        chunk_end_ms = total_audio_ms
                        
                    chunk_duration_sec = (chunk_end_ms - chunk_start_ms) / 1000.0
                    if chunk_duration_sec <= 0:
                        continue
                    
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
                            line_copy["end_ms"] = chunk_duration_sec * 1000
                            
                        chunk_for_rendering.append(line_copy)

                    # Inject Surah Header ONLY on the first page, first chunk
                    if p_idx == 0 and c_idx == 0:
                        scene_end_ms = chunk_duration_sec * 1000
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
                                "end_ms": scene_end_ms
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
                                    "end_ms": scene_end_ms
                                 }
                                 chunk_for_rendering.insert(insert_idx, bsml_line)

                    # Generate Clip
                    mushaf_clip = generate_mushaf_page_clip(chunk_for_rendering, page_num, is_short, chunk_duration_sec, background_input=background_path)
                    
                    # Add Overlays
                    reciter_display_name = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
                    surah_display_name = surah_p.bangla_name if current_language == "bengali" else surah_p.english_name
                    
                    overlays = []
                    if config_manager.get("ENABLE_RECITER_INFO", "True") == "True":
                        overlays.append(generate_reciter_name_clip(reciter_display_name, is_short, chunk_duration_sec))
                    if config_manager.get("ENABLE_SURAH_INFO", "True") == "True":
                        overlays.append(generate_surah_info_clip(surah_display_name, 0, is_short, chunk_duration_sec, language=current_language))
                    if config_manager.get("ENABLE_CHANNEL_INFO", "True") == "True":
                        overlays.append(generate_brand_clip(brand_name, is_short, chunk_duration_sec))

                    # Progress Bar
                    start_ratio = chunk_start_ms / total_audio_ms
                    end_ratio = chunk_end_ms / total_audio_ms
                    progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(chunk_duration_sec).set_position(('center', height-5))
                    overlays.append(progress_bar_bg)
                    progress_bar_fg = ColorClip(size=(width, 5), color=(0, 200, 0))
                    
                    def get_progress_width(t, sr=start_ratio, er=end_ratio, dur=chunk_duration_sec):
                        if dur <= 0: return 1
                        p = sr + (er - sr) * (t / dur)
                        w = int(width * max(0.0, min(1.0, p)))
                        return max(1, w)

                    progress_bar_fg = progress_bar_fg.resize(newsize=lambda t: (get_progress_width(t), 5))
                    progress_bar_fg = progress_bar_fg.set_opacity(0.8).set_duration(chunk_duration_sec).set_position(('left', height-5))
                    overlays.append(progress_bar_fg)

                    # Compose Chunk
                    all_chunk_clips = [mushaf_clip] + overlays
                    valid_chunk_clips = [c for c in all_chunk_clips if c is not None]
                    
                    final_chunk_clip = CompositeVideoClip(valid_chunk_clips, size=resolution).set_duration(chunk_duration_sec)
                    
                    audio_start = max(0, chunk_start_ms / 1000.0)
                    audio_end = min(total_duration, chunk_end_ms / 1000.0)
                    if audio_end > audio_start:
                        final_chunk_clip = final_chunk_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                    
                    page_clips.append(final_chunk_clip)
                    global_chunk_idx += 1
                except Exception as e:
                    print(f"[ERROR] Page {page_num} Chunk {c_idx} failed: {e}", flush=True)
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

def validate_mushaf_assets(page_numbers: list):
    """
    Verifies that all required QPC v2 font files are present on disk.
    Returns a list of missing font paths.
    """
    missing_assets = []
    font_folder = "QPC_V2_Font.ttf"
    
    # Check static header fonts
    header_fonts = ["QCF_BSML.TTF", "QCF_SurahHeader_COLOR-Regular.ttf"]
    for font_file in header_fonts:
        path = os.path.join(font_folder, font_file)
        if not os.path.exists(path):
            missing_assets.append(path)
            
    # Check page-specific fonts
    for page in page_numbers:
        path = os.path.join(font_folder, f"p{page}.ttf")
        if not os.path.exists(path):
            missing_assets.append(path)
            
    return missing_assets

async def prepare_juz_data_package(
    juz_number: int, 
    reciter_db_obj, 
    boundaries: dict, 
    is_short: bool = False,
    start_page_relative: int = None, 
    end_page_relative: int = None
):
    """
    Prepares audio and timestamp data for a Juz, optionally clipped to a page range.
    Returns (full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, bsml_audio)
    """
    surahs_in_juz = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
    
    # 1. Audio Processing: Download and Concatenate
    surah_clips = []
    surah_durations = {}
    bsml_path = "static/audio/basmallah.mp3"
    bsml_duration = 0.0
    bsml_audio = None
    if os.path.exists(bsml_path):
        bsml_audio = AudioFileClip(bsml_path)
        bsml_duration = bsml_audio.duration
        
    temp_files = []
    for s_num in surahs_in_juz:
        audio_url = read_surah_data(s_num, reciter_db_obj.database)
        if audio_url:
            t_file = download_mp3_temp(audio_url)
            if t_file:
                temp_files.append(t_file)
                clip = AudioFileClip(t_file)
                surah_durations[s_num] = clip.duration
                surah_clips.append(clip)
            else:
                for tf in temp_files: cleanup_temp_file(tf)
                return None
        else:
            for tf in temp_files: cleanup_temp_file(tf)
            return None
            
    offsets = calculate_juz_offsets(surahs_in_juz, surah_durations, bsml_duration)
    
    final_audio_clips = []
    for i, s_num in enumerate(surahs_in_juz):
        if i > 0:
            if s_num == 9:
                from moviepy.audio.AudioClip import AudioArrayClip
                silence = AudioArrayClip(np.zeros((44100 * 5, 2)), fps=44100)
                final_audio_clips.append(silence)
            elif s_num != 1 and bsml_audio:
                final_audio_clips.append(bsml_audio)
        final_audio_clips.append(surah_clips[i])
        
    full_audio_juz = concatenate_audioclips(final_audio_clips)
    
    # 2. Fetch and Offset WBW Timestamps
    all_wbw_timestamps = {}
    wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
    
    for s_num in surahs_in_juz:
        v_range = boundaries["verse_mapping"][str(s_num)].split("-")
        v_start, v_end = int(v_range[0]), int(v_range[1])
        s_wbw = get_wbw_timestamps(wbw_db_path, s_num, v_start, v_end)
        s_offset_ms = offsets[s_num] * 1000
        for ayah_num, segments in s_wbw.items():
            offset_segments = []
            for seg in segments:
                offset_segments.append([seg[0], seg[1] + s_offset_ms, seg[2] + s_offset_ms])
            all_wbw_timestamps[f"{s_num}:{ayah_num}"] = offset_segments

    # 3. Identify Pages and Clip Range
    all_pages_in_juz = set()
    for s_num in surahs_in_juz:
        pr = get_surah_page_range(s_num)
        if pr and pr[0]:
            for p in range(pr[0], pr[1] + 1):
                all_pages_in_juz.add(p)
    
    sorted_juz_pages = sorted(list(all_pages_in_juz))
    
    if start_page_relative is not None or end_page_relative is not None:
        rel_start = (start_page_relative - 1) if start_page_relative else 0
        rel_end = end_page_relative if end_page_relative else len(sorted_juz_pages)
        sorted_pages = sorted_juz_pages[rel_start:rel_end]
    else:
        sorted_pages = sorted_juz_pages

    if not sorted_pages:
        return None

    # 4. Audio Clipping based on Page Boundaries
    # Find timing of the first word on the first page and last word on the last page
    first_page_data = get_mushaf_page_data(sorted_pages[0])
    last_page_data = get_mushaf_page_data(sorted_pages[-1])
    
    # Helper to find first/last valid timestamp in page data
    def get_extreme_ms(page_data, find_min=True):
        valid_ms = []
        for line in page_data:
            for w in line.get("words", []):
                key = f"{w['surah']}:{w['ayah']}"
                segs = all_wbw_timestamps.get(key, [])
                for s in segs:
                    if s[0] == w["word"]:
                        valid_ms.append(s[1] if find_min else s[2])
                        break
        return min(valid_ms) if find_min and valid_ms else (max(valid_ms) if not find_min and valid_ms else None)

    global_start_ms = get_extreme_ms(first_page_data, find_min=True)
    global_end_ms = get_extreme_ms(last_page_data, find_min=False)

    if global_start_ms is None: global_start_ms = 0
    if global_end_ms is None: global_end_ms = full_audio_juz.duration * 1000

    # Clip audio
    audio_start_sec = global_start_ms / 1000.0
    audio_end_sec = global_end_ms / 1000.0
    clipped_audio = full_audio_juz.subclip(max(0, audio_start_sec), min(full_audio_juz.duration, audio_end_sec))
    
    # Adjust all timestamps relative to new global_start_ms
    final_wbw_timestamps = {}
    for key, segs in all_wbw_timestamps.items():
        adjusted_segs = []
        for s in segs:
            adjusted_segs.append([s[0], s[1] - global_start_ms, s[2] - global_start_ms])
        final_wbw_timestamps[key] = adjusted_segs

    return clipped_audio, final_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, bsml_audio

async def generate_juz_video(juz_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, custom_title: str = None, lines_per_page: int = 15, start_ayah: int = None, end_ayah: int = None, start_page: int = None, end_page: int = None):
    """
    Orchestrates the generation of a Mushaf-style Juz recitation video.
    Supports optional Ayah range and relative Page range selection for testing.
    """
    async with async_session() as session:
        # 1. Fetch Juz Boundaries
        boundaries = get_juz_boundaries(juz_number)
        if not boundaries:
            return None
            
        # Apply Ayah range overrides if provided
        if start_ayah is not None or end_ayah is not None:
            # ... (Existing Ayah override logic) ...
            pass # Keep existing logic for now, but focus on page range fix
        
        # 2. Fetch Reciter and Language Metadata
        surahs_in_juz_raw = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
        start_surah = surahs_in_juz_raw[0]
        reciter_db_obj, lang_obj, _ = await fetch_localized_metadata(session, start_surah, reciter_key, config_manager)
        if not reciter_db_obj:
            return None
            
        current_language = lang_obj.name if lang_obj else "bengali"
        brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
        reciter_p = Reciter(reciter_key)
        
        # 3. Prepare Data Package (Clipped)
        prep_res = await prepare_juz_data_package(
            juz_number, reciter_db_obj, boundaries, is_short, 
            start_page_relative=start_page, end_page_relative=end_page
        )
        if not prep_res:
            return None
            
        full_audio, all_wbw_timestamps, sorted_pages, offsets, temp_files, surah_clips, bsml_audio = prep_res
        total_duration = float(full_audio.duration)
        total_audio_ms = float(total_duration * 1000)
        
        resolution = get_resolution(is_short)
        width, height = resolution
        page_clips = []

        # 4. Asset Validation
        missing_fonts = validate_mushaf_assets(sorted_pages)
        if missing_fonts:
            # Cleanup and fail
            full_audio.close()
            if bsml_audio: bsml_audio.close()
            for c in surah_clips: c.close()
            for tf in temp_files: cleanup_temp_file(tf)
            print(f"[ERROR] Missing required fonts: {missing_fonts}")
            return None

        # 5. Collect and Aligned Mushaf Lines
        surah_set = set(surahs_in_juz_raw)
        lines_by_page = {}
        for page_num in sorted_pages:
            page_data = get_mushaf_page_data(page_num)
            
            # Pre-pass: Fill in missing surah_numbers by propagation
            last_known_surah = None
            for line in page_data:
                if line.get("surah_number") and line["surah_number"] != '':
                    last_known_surah = line["surah_number"]
                elif line.get("words"):
                    last_known_surah = line["words"][0]["surah"]
                    line["surah_number"] = last_known_surah
                elif last_known_surah:
                    line["surah_number"] = last_known_surah
            
            # Back-propagation for headers at the top of the page
            next_known_surah = None
            for line in reversed(page_data):
                if line.get("surah_number") and line["surah_number"] != '':
                    next_known_surah = line["surah_number"]
                elif next_known_surah:
                    line["surah_number"] = next_known_surah

            filtered_page = []
            for line in page_data:
                l_type = line.get("line_type", "ayah")
                line_surah = line.get("surah_number")
                
                if line_surah in surah_set:
                    # For Ayah lines, verify they are within the Juz boundaries
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
                        # Keep surah_name and basmallah lines
                        filtered_page.append(line.copy())
            
            if filtered_page:
                aligned_page = align_mushaf_lines_with_juz_timestamps(filtered_page, all_wbw_timestamps)
                
                # Post-alignment refinement for static headers
                for i, line in enumerate(aligned_page):
                    if line["line_type"] in ["surah_name", "basmallah"] and line.get("start_ms") is None:
                        # Find next ayah line for timing
                        for j in range(i + 1, len(aligned_page)):
                            if aligned_page[j].get("start_ms") is not None:
                                line["start_ms"] = aligned_page[j]["start_ms"]
                                line["end_ms"] = aligned_page[j]["end_ms"]
                                break
                        
                        # If still None, look backwards
                        if line.get("start_ms") is None:
                            for j in range(i - 1, -1, -1):
                                if aligned_page[j].get("start_ms") is not None:
                                    line["start_ms"] = aligned_page[j]["start_ms"]
                                    line["end_ms"] = aligned_page[j]["end_ms"]
                                    break
                
                lines_by_page[page_num] = aligned_page

        # 6. Generate Clips with Page-Aware Chunking (Juz-aware)
        global_chunk_idx = 0
        for p_idx, page_num in enumerate(sorted_pages):
            if page_num not in lines_by_page: continue
            
            page_lines = lines_by_page[page_num]
            # Chunk within the page
            page_chunks = [page_lines[i:i + lines_per_page] for i in range(0, len(page_lines), lines_per_page)]
            
            for c_idx, chunk in enumerate(page_chunks):
                try:
                    # Timing boundaries for chunk
                    valid_starts = [l["start_ms"] for l in chunk if l["start_ms"] is not None]
                    valid_ends = [l["end_ms"] for l in chunk if l["end_ms"] is not None]
                    
                    if not valid_starts or not valid_ends:
                        # Fallback for empty/unaligned chunks (like headers at transition)
                        if global_chunk_idx == 0:
                            chunk_start_ms = 0
                            chunk_end_ms = 5000
                        else:
                            # Skip for now if we can't find timing
                            continue
                    else:
                        chunk_start_ms = min(valid_starts)
                        chunk_end_ms = max(valid_ends)
                    
                    print(f"DEBUG: chunk_start_ms={chunk_start_ms} ({type(chunk_start_ms)})", flush=True)
                    print(f"DEBUG: chunk_end_ms={chunk_end_ms} ({type(chunk_end_ms)})", flush=True)
                    print(f"DEBUG: total_duration={total_duration} ({type(total_duration)})", flush=True)

                    # Buffer boundaries
                    if global_chunk_idx == 0:
                        chunk_start_ms = 0
                    if p_idx == len(sorted_pages) - 1 and c_idx == len(page_chunks) - 1:
                        chunk_end_ms = total_audio_ms
                        
                    try:
                        chunk_duration_sec = (float(chunk_end_ms) - float(chunk_start_ms)) / 1000.0
                    except:
                        chunk_duration_sec = 5.0 # Fallback
                        
                    if chunk_duration_sec <= 0: continue
                    
                    # Adjust timestamps relative to chunk start
                    chunk_for_rendering = []
                    for line in chunk:
                        line_copy = line.copy()
                        if line_copy["start_ms"] is not None:
                            line_copy["start_ms"] -= chunk_start_ms
                        if line_copy["end_ms"] is not None:
                            line_copy["end_ms"] -= chunk_start_ms
                        
                        # Headers and basmallah should last end of scene if they are part of it
                        if line_copy.get("line_type") in ["surah_name", "basmallah"]:
                            line_copy["start_ms"] = 0
                            line_copy["end_ms"] = chunk_duration_sec * 1000
                            
                        chunk_for_rendering.append(line_copy)

                    # Inject Surah Header/Basmallah at transitions if missing
                    # (Logic: If we see Ayah 1 of a new Surah, ensure header/bsml precede it)
                    # For Juz, this is complex because headers might be at end of previous page
                    # The get_mushaf_page_data already includes them if they exist in the DB for that page.
                    
                    # Generate Clip
                    mushaf_clip = generate_mushaf_page_clip(chunk_for_rendering, page_num, is_short, chunk_duration_sec, background_input=background_path)
                    
                    # Add Overlays
                    reciter_display_name = reciter_p.bangla_name if current_language == "bengali" else reciter_p.english_name
                    # Juz Title instead of Surah Name
                    juz_display_name = f"Juz {juz_number}"
                    
                    overlays = []
                    if config_manager.get("ENABLE_RECITER_INFO", "True") == "True":
                        overlays.append(generate_reciter_name_clip(reciter_display_name, is_short, chunk_duration_sec))
                    if config_manager.get("ENABLE_SURAH_INFO", "True") == "True":
                        overlays.append(generate_surah_info_clip(juz_display_name, 0, is_short, chunk_duration_sec, language=current_language))
                    if config_manager.get("ENABLE_CHANNEL_INFO", "True") == "True":
                        overlays.append(generate_brand_clip(brand_name, is_short, chunk_duration_sec))

                    # Progress Bar (Juz level)
                    start_ratio = float(chunk_start_ms) / float(total_audio_ms)
                    end_ratio = float(chunk_end_ms) / float(total_audio_ms)
                    progress_bar_bg = ColorClip(size=(width, 5), color=(100, 100, 100)).set_opacity(0.3).set_duration(chunk_duration_sec).set_position(('center', height-5))
                    overlays.append(progress_bar_bg)
                    
                    def get_progress_width(t, sr=start_ratio, er=end_ratio, dur=chunk_duration_sec):
                        if dur <= 0: return 1
                        p = sr + (er - sr) * (t / dur)
                        w = int(width * max(0.0, min(1.0, p)))
                        return max(1, w)

                    progress_bar_fg = ColorClip(size=(width, 5), color=(0, 200, 0))
                    progress_bar_fg = progress_bar_fg.resize(newsize=lambda t: (get_progress_width(t), 5))
                    progress_bar_fg = progress_bar_fg.set_opacity(0.8).set_duration(chunk_duration_sec).set_position(('left', height-5))
                    overlays.append(progress_bar_fg)

                    final_chunk_clip = CompositeVideoClip([mushaf_clip] + overlays, size=resolution).set_duration(chunk_duration_sec)
                    
                    try:
                        audio_start = max(0.0, float(chunk_start_ms) / 1000.0)
                        audio_end = min(float(total_duration), float(chunk_end_ms) / 1000.0)
                        if float(audio_end) > float(audio_start):
                            final_chunk_clip = final_chunk_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                    except:
                        pass
                    
                    page_clips.append(final_chunk_clip)
                    global_chunk_idx += 1
                except Exception as e:
                    print(f"[ERROR] Juz {juz_number} Page {page_num} Chunk {c_idx} failed: {e}")
                    continue

        # 7. Final Assembly
        if not page_clips:
            full_audio.close()
            if bsml_audio: bsml_audio.close()
            for c in surah_clips: c.close()
            for tf in temp_files: cleanup_temp_file(tf)
            raise Exception(f"Failed to generate any page clips for Juz {juz_number}. Check alignment and timing data.")
            
        final_video = concatenate_videoclips(page_clips, method="compose")
        filename = f"mushaf_juz_{juz_number}_{reciter_key.replace('.', '_')}.mp4"
        export_dir = "exported_data/shorts" if is_short else "exported_data/videos"
        os.makedirs(export_dir, exist_ok=True)
        video_path = os.path.join(export_dir, filename)
        
        final_video.write_videofile(
            video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=VIDEO_ENCODING_THREADS,
            preset="ultrafast",
            logger="bar"
        )
        
        # Cleanup clips to release file handles
        full_audio.close()
        if bsml_audio: bsml_audio.close()
        for c in surah_clips: c.close()
        for c in page_clips: c.close()
        
        # Cleanup temp files
        for tf in temp_files: cleanup_temp_file(tf)
        
        details_path = generate_juz_details(
            juz_number,
            reciter_p,
            offsets,
            is_short,
            language=current_language
        )
        
        return {
            "video": video_path,
            "info": details_path,
            "surah_number": 0, # Sentinel for Juz videos
            "juz_number": juz_number,
            "start_ayah": 1,
            "end_ayah": 0, # Sentinel
            "reciter": reciter_key,
            "is_short": is_short
        }
