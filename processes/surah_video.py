from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation, get_full_translation_for_ayah
from db_ops.crud_wbw import get_wbw_timestamps, get_wbw_text_for_ayah, get_wbw_translation_for_ayah
from db_ops.crud_reciters import get_reciter_by_key
from db.database import async_session
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from factories.video import get_resolution, make_silence # Import both
from factories.single_clip import (
    generate_arabic_text_clip,
    generate_wbw_arabic_text_clip,
    generate_wbw_advanced_arabic_text_clip,
    generate_wbw_advanced_translation_text_clip,
    generate_wbw_interlinear_text_clip,
    generate_translation_text_clip, 
    generate_full_ayah_translation_clip,
    generate_reciter_name_clip,
    generate_surah_info_clip, 
    generate_brand_clip,
    generate_background
)
from processes.wbw_utils import segment_words_with_timestamps
from factories.composite_clip import generate_intro, generate_outro
from factories.video import get_resolution
from processes.video_configs import COMMON, VIDEO_ENCODING_THREADS
from processes.Classes import Reciter, Surah
from processes.description import generate_details
from config_manager import config_manager

from moviepy.editor import *
import tempfile
import json
import anyio


def create_ayah_clip(surah: Surah, ayah, reciter: Reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short: bool, background_image_path: str = None):
    try:
        screen_size = get_resolution(is_short)
        current_clips = []
        audio_duration = full_audio.duration * 1000  # Convert to milliseconds
        if gstart_ms < 0 or gstart_ms >= audio_duration:
            raise ValueError(f"Invalid start time {gstart_ms} for Surah {surah.number}, Ayah {ayah}")
        gend_ms = gend_ms if gend_ms <= audio_duration else audio_duration
        # Calculate the ayah duration in seconds
        duration = (gend_ms - gstart_ms) / 1000.0
        
        # Get the words for the ayah and build the full ayah text
        words_dict = surah_data.get(surah.number, {}).get(ayah, {})
        if not words_dict:
            raise ValueError(f"No data for surah {surah} ayah {ayah}")

        # Order words by their keys (word numbers)
        sorted_word_nums = sorted(words_dict.keys())
        full_ayah_text = " ".join(words_dict[w] for w in sorted_word_nums)
        
        background_clip = generate_background(background_image_path, duration, is_short)
        current_clips.append(background_clip)
        
        # Create a base clip with the full ayah text (non-highlighted)
        arabic_text_clip = generate_arabic_text_clip(full_ayah_text, is_short, duration)
        current_clips.append(arabic_text_clip)

        translation_text = translation_data[(surah.number, ayah)]
        translation_clip = generate_translation_text_clip(translation_text, is_short, duration)
        current_clips.append(translation_clip)
        
        if COMMON["enable_footer"]:
            # Reciter name overlay
            if COMMON["enable_reciter_info"]:
                reciter_name_clip = generate_reciter_name_clip(f"{reciter.bangla_name}", is_short=is_short, duration=duration)
                current_clips.append(reciter_name_clip)

            if COMMON["enable_surah_info"]:
                surah_name_clip = generate_surah_info_clip(surah.name_bangla, ayah, is_short=is_short, duration=duration)
                current_clips.append(surah_name_clip)

            # Verser number overlay
            if COMMON["enable_channel_info"]:
                brand_name_clip = generate_brand_clip("তাকওয়া বাংলা", is_short=is_short, duration=duration)
                current_clips.append(brand_name_clip)
        composite = CompositeVideoClip(current_clips, size=screen_size).set_duration(duration)
    except Exception as e:
        print(str(e), flush=True)
        print(f"[ERROR ] - Error creating composite video clip for ayah{ayah}: {e}", flush=True)
        raise e
    
    # Subclip the audio for the ayah (convert global ms to seconds)
    ayah_audio = full_audio.subclip(gstart_ms / 1000.0, gend_ms / 1000.0)
    composite = composite.set_audio(ayah_audio)
    print(f"[INFO] - Created composite video clip for Surah {surah.number}, Ayah {ayah}", flush=True)
    return composite


def create_wbw_ayah_clip(surah: Surah, ayah, reciter: Reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short: bool, segments: list, background_image_path: str = None):
    try:
        screen_size = get_resolution(is_short)
        current_clips = []
        
        # Duration from word segments
        duration = (segments[-1][2] - segments[0][1]) / 1000.0
        
        # Get the words for the ayah
        words_dict = surah_data.get(surah.number, {}).get(ayah, {})
        sorted_word_nums = sorted(words_dict.keys())
        words_list = [words_dict[w] for w in sorted_word_nums]
        
        background_clip = generate_background(background_image_path, duration, is_short)
        current_clips.append(background_clip)
        
        # WBW Arabic text
        arabic_text_clip = generate_wbw_arabic_text_clip(words_list, ayah, is_short, duration, segments)
        current_clips.append(arabic_text_clip)

        translation_text = translation_data[(surah.number, ayah)]
        translation_clip = generate_translation_text_clip(translation_text, is_short, duration)
        current_clips.append(translation_clip)
        
        if COMMON["enable_footer"]:
            if COMMON["enable_reciter_info"]:
                reciter_name_clip = generate_reciter_name_clip(f"{reciter.bangla_name}", is_short=is_short, duration=duration)
                current_clips.append(reciter_name_clip)
            if COMMON["enable_surah_info"]:
                surah_name_clip = generate_surah_info_clip(surah.name_bangla, ayah, is_short=is_short, duration=duration)
                current_clips.append(surah_name_clip)
            if COMMON["enable_channel_info"]:
                brand_name_clip = generate_brand_clip("তাকওয়া বাংলা", is_short=is_short, duration=duration)
                current_clips.append(brand_name_clip)
                
        composite = CompositeVideoClip(current_clips, size=screen_size).set_duration(duration)
        
        # Subclip audio using WBW segments
        ayah_audio = full_audio.subclip(segments[0][1] / 1000.0, segments[-1][2] / 1000.0)
        composite = composite.set_audio(ayah_audio)
        
        return composite
    except Exception as e:
        print(f"[ERROR] - Error creating WBW clip for ayah {ayah}: {e}")
        raise e


def create_wbw_advanced_ayah_clip(surah: Surah, ayah, reciter: Reciter, full_audio, is_short: bool, segments: list, background_image_path: str = None):
    """
    Creates an ayah clip using advanced multi-line segmentation.
    """
    try:
        screen_size = get_resolution(is_short)
        
        # 1. Fetch data from new WBW databases
        text_db = "databases/text/qpc-hafs-word-by-word.db"
        trans_db = "databases/translation/bangali-word-by-word-translation.sqlite"
        
        arabic_words = get_wbw_text_for_ayah(text_db, surah.number, ayah)
        bengali_words = get_wbw_translation_for_ayah(trans_db, surah.number, ayah)
        
        # 2. Get config for font size and character limit
        interlinear_enabled = config_manager.get("WBW_INTERLINEAR_ENABLED", "False") == "True"
        interlinear_trans_font_size = int(config_manager.get("WBW_TRANSLATION_FONT_SIZE", 20))
        
        full_trans_enabled = config_manager.get("WBW_FULL_TRANSLATION_ENABLED", "False") == "True"
        full_trans_source = config_manager.get("WBW_FULL_TRANSLATION_SOURCE", "rawai_al_bayan")
        full_ayah_translation = ""
        if full_trans_enabled:
            full_ayah_translation = get_full_translation_for_ayah(surah.number, ayah, full_trans_source)

        if is_short:
            font_size = int(config_manager.get("WBW_FONT_SIZE_SHORT", 40))
            char_limit = int(config_manager.get("WBW_CHAR_LIMIT_SHORT", 15))
        else:
            font_size = int(config_manager.get("WBW_FONT_SIZE_REGULAR", 60))
            char_limit = int(config_manager.get("WBW_CHAR_LIMIT_REGULAR", 30))
            
        # 3. Segment words into lines
        # In interlinear mode, we use a ratio to estimate width
        ratio = interlinear_trans_font_size / font_size if font_size > 0 else 0.5
        line_segments = segment_words_with_timestamps(
            arabic_words, bengali_words, segments, char_limit, 
            interlinear=interlinear_enabled, translation_ratio=ratio
        )
        
        ayah_clips = []
        for line in line_segments:
            line_duration = (line["end_ms"] - line["start_ms"]) / 1000.0
            current_line_clips = []
            
            # Background
            bg = generate_background(background_image_path, line_duration, is_short)
            current_line_clips.append(bg)
            
            if interlinear_enabled:
                # Interlinear rendering
                interlinear_clip = generate_wbw_interlinear_text_clip(
                    line["words"], line["translations"], is_short, line_duration,
                    font_size, interlinear_trans_font_size
                )
                current_line_clips.append(interlinear_clip)
            else:
                # Standard separate Arabic/Bengali lines
                # Arabic line
                arabic_clip = generate_wbw_advanced_arabic_text_clip(line["text"], is_short, line_duration, font_size)
                current_line_clips.append(arabic_clip)
                
                # Bengali line
                trans_clip = generate_wbw_advanced_translation_text_clip(line["translation_text"], is_short, line_duration, int(font_size * 0.8))
                current_line_clips.append(trans_clip)
            
            # Full Ayah Translation Overlay at bottom
            if full_trans_enabled and full_ayah_translation:
                full_trans_clip = generate_full_ayah_translation_clip(full_ayah_translation, is_short, line_duration)
                current_line_clips.append(full_trans_clip)

            # Footer
            if COMMON["enable_footer"]:
                if COMMON["enable_reciter_info"]:
                    current_line_clips.append(generate_reciter_name_clip(reciter.bangla_name, is_short, line_duration))
                if COMMON["enable_surah_info"]:
                    current_line_clips.append(generate_surah_info_clip(surah.name_bangla, ayah, is_short, line_duration))
                if COMMON["enable_channel_info"]:
                    current_line_clips.append(generate_brand_clip("তাকওয়া বাংলা", is_short, line_duration))
            
            line_composite = CompositeVideoClip(current_line_clips, size=screen_size).set_duration(line_duration)
            ayah_clips.append(line_composite)
            
        if not ayah_clips:
            print(f"[WARNING] - No clips generated for ayah {ayah}. Check WBW data.")
            return None

        # 4. Append delay if configured
        delay_sec = float(config_manager.get("WBW_DELAY_BETWEEN_AYAH", 0.5))
        if delay_sec > 0:
            last_clip = ayah_clips[-1]
            # Create a clip from the last frame of the last line
            last_frame_clip = last_clip.to_ImageClip(t=last_clip.duration - 0.01).set_duration(delay_sec)
            # Add silence
            last_frame_clip = last_frame_clip.set_audio(make_silence(delay_sec))
            ayah_clips.append(last_frame_clip)

        # 5. Concatenate line clips for this ayah
        final_ayah_clip = concatenate_videoclips(ayah_clips)
        
        # 6. Attach audio (the segments cover the recitation part)
        ayah_audio = full_audio.subclip(segments[0][1] / 1000.0, segments[-1][2] / 1000.0)
        
        if delay_sec > 0:
            final_audio = concatenate_audioclips([ayah_audio, make_silence(delay_sec)])
            final_ayah_clip = final_ayah_clip.set_audio(final_audio)
        else:
            final_ayah_clip = final_ayah_clip.set_audio(ayah_audio)
        
        return final_ayah_clip
        
    except Exception as e:
        print(f"[ERROR] - Error creating Advanced WBW clip for ayah {ayah}: {e}")
        raise e


def generate_surah(surah_number: int, reciter_tag: str, custom_title: str = None):
    reciter = Reciter(reciter_tag)
    surah = Surah(surah_number)
    surah_url = read_surah_data(surah.number, reciter.database_name)
    if not surah_url:
        raise ValueError(f"Could not find audio URL for Surah {surah.number} and Reciter '{reciter.database_name}'. The reciter's database may be missing this surah.")
    
    downloaded_surah_file = download_mp3_temp(surah_url)

    full_audio = AudioFileClip(downloaded_surah_file)
    
    surah_data = read_text_data(surah.number)
    translation_data = read_translation(surah.number)
    timestamp_data = read_timestamp_data(surah.number, reciter.database_name)
    
    if not timestamp_data:
        raise ValueError(f"No timestamp data found for Surah {surah.number} and Reciter '{reciter.database_name}'. Cannot create video.")

    # Fetch reciter from DB to check for WBW database
    async def fetch_reciter():
        async with async_session() as session:
            return await get_reciter_by_key(session, reciter_tag)
    
    db_reciter = anyio.from_thread.run(fetch_reciter)
    wbw_data = {}
    if db_reciter and db_reciter.wbw_database:
        print(f"[INFO] - WBW database found: {db_reciter.wbw_database}", flush=True)
        db_path = os.path.join("databases", "word-by-word", db_reciter.wbw_database)
        wbw_data = get_wbw_timestamps(db_path, surah_number, 1, 114) # Fetch all for this surah

    active_background = config_manager.get("ACTIVE_BACKGROUND")
    
    clips = []
    if COMMON["enable_intro"]:
        intro = generate_intro(surah=surah, reciter=reciter, background_image_url=active_background, is_short=False)
        print(f"[INFO] - Intro generated", flush=True)
        clips.append(intro)
    print(f"[INFO] - Going inside the ayah loop", flush=True)
    for tdata in timestamp_data:
        surah_number, ayah, gstart_ms, gend_ms, seg_str = tdata
        try:
            # Use Advanced WBW clip if data exists for this ayah
            if ayah in wbw_data:
                print(f"[INFO] - Creating Advanced WBW clip for Ayah {ayah}", flush=True)
                clip = create_wbw_advanced_ayah_clip(surah, ayah, reciter, full_audio, is_short=False, segments=wbw_data[ayah], background_image_path=active_background)
                if clip is None:
                    # Fallback to standard clip if WBW fails
                    print(f"[INFO] - Falling back to standard clip for Ayah {ayah}", flush=True)
                    clip = create_ayah_clip(surah, ayah, reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short=False, background_image_path=active_background)
            else:
                clip = create_ayah_clip(surah, ayah, reciter,gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short=False, background_image_path=active_background)
        except Exception as e:
            print(f"[ERROR ] - Error creating clip for Surah {surah_number}, Ayah {ayah}: {e}", flush=True)
            raise e
        clips.append(clip)

    if COMMON["enable_outro"]:
        outro = generate_outro(background_image_url=None, is_short=False)
        clips.append(outro)
    print(f"[INFO] - Going to concatenate the clips", flush=True)
    # Concatenate all ayah clips one after the other
    final_video = concatenate_videoclips(clips)
    print(f"[INFO] - Going to write the final video", flush=True)

    # Write the final video to a temporary file.
    #output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    output_path = f"exported_data/videos/quran_video_{surah_number}_{reciter.eng_name}.mp4"
    try:
        final_video.write_videofile(
            output_path, 
            codec='libx264', 
            fps=24, 
            audio_codec="aac",
            preset="ultrafast",
            threads=VIDEO_ENCODING_THREADS,
            write_logfile=True,
            logger="bar"
        )
    except Exception as e:
        print(str(e), flush=True)
    print(f"[INFO] - Final video written to {output_path}", flush=True)
    info_file_path = generate_details(surah, reciter, True, 1, 1, custom_title=custom_title)
    print(f"[INFO] - Info file written to {info_file_path}", flush=True)
    
    # Get total ayah count from surah_data or similar
    # For now, let's assume we can get it from timestamp_data length or just return the info we have
    total_ayahs = len(timestamp_data)

    return {
        "video": output_path, 
        "info": info_file_path, 
        "is_short": False, 
        "reciter": reciter.tag,
        "surah_number": surah_number,
        "start_ayah": 1,
        "end_ayah": total_ayahs
    }
    