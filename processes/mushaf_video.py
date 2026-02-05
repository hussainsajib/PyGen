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
from processes.description import generate_details
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

async def generate_juz_video(juz_number: int, reciter_key: str, is_short: bool = False, background_path: str = None, custom_title: str = None, lines_per_page: int = 15):
    """
    Orchestrates the generation of a Mushaf-style Juz recitation video.
    """
    async with async_session() as session:
        # 1. Fetch Juz Boundaries
        boundaries = get_juz_boundaries(juz_number)
        if not boundaries:
            return None
            
        start_surah = boundaries["start_surah"]
        end_surah = boundaries["end_surah"]
        surahs_in_juz = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
        
        # 2. Fetch Reciter and Language Metadata
        # We'll use the first surah to fetch generic reciter/language metadata
        reciter_db_obj, lang_obj, _ = await fetch_localized_metadata(session, start_surah, reciter_key, config_manager)
        if not reciter_db_obj:
            return None
            
        current_language = lang_obj.name if lang_obj else "bengali"
        brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"
        reciter_p = Reciter(reciter_key)
        
        # 3. Audio Processing: Download and Concatenate with Offsets
        surah_clips = []
        surah_durations = {}
        
        # We need a Basmallah clip for concatenation
        # For now, let's assume we can fetch it or use a placeholder if not available.
        # Ideally, we should have a local 'static/audio/basmallah.mp3'
        bsml_path = "static/audio/basmallah.mp3"
        bsml_duration = 0.0
        bsml_audio = None
        if os.path.exists(bsml_path):
            bsml_audio = AudioFileClip(bsml_path)
            bsml_duration = bsml_audio.duration
            
        # Download and measure each Surah audio
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
                    # Cleanup and fail if any audio missing
                    for tf in temp_files: cleanup_temp_file(tf)
                    return None
            else:
                for tf in temp_files: cleanup_temp_file(tf)
                return None
                
        # Calculate Juz-level offsets
        offsets = calculate_juz_offsets(surahs_in_juz, surah_durations, bsml_duration)
        
        # Concatenate final audio stream
        final_audio_clips = []
        for i, s_num in enumerate(surahs_in_juz):
            if i > 0:
                if s_num == 9:
                    # 5s Silence for Surah 9
                    from moviepy.audio.AudioClip import AudioArrayClip
                    import numpy as np
                    silence = AudioArrayClip(np.zeros((44100 * 5, 2)), fps=44100)
                    final_audio_clips.append(silence)
                elif s_num != 1 and bsml_audio:
                    final_audio_clips.append(bsml_audio)
            
            # Find the surah clip (matched by index)
            final_audio_clips.append(surah_clips[i])
            
        full_audio = concatenate_audioclips(final_audio_clips)
        total_duration = full_audio.duration
        
        # 4. Fetch and Offset WBW Timestamps for all Surahs
        all_wbw_timestamps = {}
        wbw_db_path = os.path.join("databases", "word-by-word", reciter_db_obj.wbw_database)
        
        for s_num in surahs_in_juz:
            surah_p = Surah(s_num)
            # Determine range within Juz for this Surah
            v_range = boundaries["verse_mapping"][str(s_num)].split("-")
            v_start, v_end = int(v_range[0]), int(v_range[1])
            
            s_wbw = get_wbw_timestamps(wbw_db_path, s_num, v_start, v_end)
            
            # Offset timestamps
            s_offset_ms = offsets[s_num] * 1000
            offset_wbw = {}
            for ayah_num, segments in s_wbw.items():
                offset_segments = []
                for seg in segments:
                    # seg is [word_num, start_ms, end_ms]
                    offset_segments.append([seg[0], seg[1] + s_offset_ms, seg[2] + s_offset_ms])
                offset_wbw[ayah_num] = offset_segments
            
            # Merge into master map (Ayah numbers are unique per Surah, but we need composite keys for Juz)
            # We'll use "surah:ayah" as key
            for ayah_num, segs in s_wbw.items():
                all_wbw_timestamps[f"{s_num}:{ayah_num}"] = offset_wbw[ayah_num]

        # 5. Collect and Aligned Mushaf Lines across all Surahs
        # Find page range for the entire Juz
        all_pages = set()
        for s_num in surahs_in_juz:
            pr = get_surah_page_range(s_num)
            if pr and pr[0]:
                for p in range(pr[0], pr[1] + 1):
                    all_pages.add(p)
        
        sorted_pages = sorted(list(all_pages))
        resolution = get_resolution(is_short)
        width, height = resolution
        page_clips = []
        total_audio_ms = total_duration * 1000
        
        # We need a set of surahs part of this Juz to filter page data
        surah_set = set(surahs_in_juz)
        
        # Cache for page data to avoid redundant DB hits
        lines_by_page = {}
        for page_num in sorted_pages:
            page_data = get_mushaf_page_data(page_num)
            filtered_page = []
            for line in page_data:
                # Keep line if it belongs to a surah in our Juz
                if line["surah_number"] in surah_set:
                    # Further filter words to ensure they are within Juz boundaries for boundary surahs
                    # (Though Mushaf pages usually align well with Juz, we be safe)
                    filtered_words = []
                    for w in line["words"]:
                        s_id = str(w["surah"])
                        if s_id in boundaries["verse_mapping"]:
                            v_range = boundaries["verse_mapping"][s_id].split("-")
                            if int(v_range[0]) <= w["ayah"] <= int(v_range[1]):
                                filtered_words.append(w)
                    
                    if filtered_words or line["line_type"] in ["surah_name", "basmallah"]:
                        line_copy = line.copy()
                        line_copy["words"] = filtered_words
                        filtered_page.append(line_copy)
            
            if filtered_page:
                aligned_page = align_mushaf_lines_with_juz_timestamps(filtered_page, all_wbw_timestamps)
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
                    
                    # Buffer boundaries
                    if global_chunk_idx == 0:
                        chunk_start_ms = 0
                    if p_idx == len(sorted_pages) - 1 and c_idx == len(page_chunks) - 1:
                        chunk_end_ms = total_audio_ms
                        
                    chunk_duration_sec = (chunk_end_ms - chunk_start_ms) / 1000.0
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
                    start_ratio = chunk_start_ms / total_audio_ms
                    end_ratio = chunk_end_ms / total_audio_ms
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
                    
                    audio_start = max(0, chunk_start_ms / 1000.0)
                    audio_end = min(total_duration, chunk_end_ms / 1000.0)
                    if audio_end > audio_start:
                        final_chunk_clip = final_chunk_clip.set_audio(full_audio.subclip(audio_start, audio_end))
                    
                    page_clips.append(final_chunk_clip)
                    global_chunk_idx += 1
                except Exception as e:
                    print(f"[ERROR] Juz {juz_number} Page {page_num} Chunk {c_idx} failed: {e}")
                    continue

        # 7. Final Assembly
        if not page_clips:
            full_audio.close()
            for tf in temp_files: cleanup_temp_file(tf)
            return None
            
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
        
        full_audio.close()
        for c in page_clips: c.close()
        for tf in temp_files: cleanup_temp_file(tf)
        
        return {
            "video": video_path,
            "juz_number": juz_number,
            "reciter": reciter_key,
            "is_short": is_short
        }
