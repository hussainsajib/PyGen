import numpy as np

from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger
from processes.Classes import Surah, Reciter
from processes.video_configs import *
from processes.description import generate_details
from factories.file import *

from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation
from net_ops.download_file import download_mp3_temp
from processes.surah_video import create_ayah_clip # Re-use the clip creation logic
from factories.composite_clip import generate_intro, generate_outro

def make_silence(duration, fps=44100):
    return AudioClip(make_frame=lambda t: np.zeros((1,)), duration=duration, fps=fps)

def generate_video(surah_number: int, start_verse: int, end_verse: int, reciter_key: str, is_short: bool):
    surah = Surah(surah_number)
    reciter = Reciter(reciter_key)
    
    # 1. Download full audio and get all data from DB
    surah_url = read_surah_data(surah.number, reciter.database_name)
    if not surah_url:
        raise ValueError(f"Could not find audio URL for Surah {surah.number} and Reciter '{reciter.database_name}'.")

    downloaded_surah_file = download_mp3_temp(surah_url)
    full_audio = AudioFileClip(downloaded_surah_file)
    
    surah_data = read_text_data(surah.number)
    translation_data = read_translation(surah.number)
    timestamp_data = read_timestamp_data(surah.number, reciter.database_name)

    if not timestamp_data:
        raise ValueError(f"No timestamp data found for Surah {surah.number} and Reciter '{reciter.database_name}'.")

    # 2. Filter timestamps for the desired verse range
    verse_range_timestamps = [t for t in timestamp_data if start_verse <= t[1] <= end_verse]
    if not verse_range_timestamps:
        raise ValueError(f"No timestamp data found for verses {start_verse}-{end_verse} in Surah {surah.number}.")

    clips = []
    
    # 3. Conditionally create Intro
    if not is_short and COMMON["enable_intro"]:
        intro = generate_intro(surah, reciter, None, is_short)
        clips.append(intro)
    
    # 4. Loop through the filtered timestamps and create a clip for each ayah
    for tdata in verse_range_timestamps:
        surah_num, ayah, gstart_ms, gend_ms, seg_str = tdata
        try:
            clip = create_ayah_clip(surah, ayah, reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio, is_short=is_short)
            clips.append(clip)
        except Exception as e:
            logger.error(f"Error creating clip for Surah {surah_num}, Ayah {ayah}: {e}")
            raise

    # 5. Check if clips list is empty before concatenation
    if not clips:
        logger.warning("No valid clips were generated for the given verse range.")
        return None

    if not is_short and COMMON["enable_outro"]:
        outro = generate_outro(None, is_short)
        clips.append(outro)

    final_video = concatenate_videoclips(clips)
    output_path = get_filename(surah_number, start_verse, end_verse, reciter.eng_name, is_short)
    
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    info_file_path = generate_details(surah, reciter, True, start_verse, end_verse)
    
    return {"video": output_path, "info": info_file_path, "is_short": is_short, "reciter": reciter.tag}

