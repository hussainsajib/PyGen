from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation
from net_ops.download_file import download_mp3_temp, cleanup_temp_file
from factories.single_clip import (
    generate_arabic_text_clip,
    generate_translation_text_clip, 
    generate_reciter_name_clip,
    generate_surah_info_clip, 
    generate_brand_clip,
    generate_background
)
from factories.composite_clip import generate_intro, generate_outro
from factories.video import get_resolution
from processes.video_configs import COMMON
from processes.Classes import Reciter, Surah
from processes.description import generate_details

from moviepy.editor import *
import tempfile
import json


def create_ayah_clip(surah: Surah, ayah, reciter: Reciter, gstart_ms, gend_ms, surah_data, translation_data, full_audio):
    screen_size = get_resolution(False)
    current_clips = []
    # Calculate the ayah duration in seconds
    duration = (gend_ms - gstart_ms) / 1000.0
    
    # Get the words for the ayah and build the full ayah text
    words_dict = surah_data.get(surah.number, {}).get(ayah, {})
    if not words_dict:
        raise ValueError(f"No data for surah {surah} ayah {ayah}")

    # Order words by their keys (word numbers)
    sorted_word_nums = sorted(words_dict.keys())
    full_ayah_text = " ".join(words_dict[w] for w in sorted_word_nums)
    
    background_clip = generate_background(None, duration, False)
    current_clips.append(background_clip)
    
    # Create a base clip with the full ayah text (non-highlighted)
    arabic_text_clip = generate_arabic_text_clip(full_ayah_text, False, duration)
    current_clips.append(arabic_text_clip)

    translation_text = translation_data[(surah.number, ayah)]
    translation_clip = generate_translation_text_clip(translation_text, False, duration)
    current_clips.append(translation_clip)
    
    if COMMON["enable_footer"]:
                # Reciter name overlay
                if COMMON["enable_reciter_info"]:
                    reciter_name_clip = generate_reciter_name_clip(reciter.bangla_name, is_short=False, duration=duration)
                    current_clips.append(reciter_name_clip)

                if COMMON["enable_surah_info"]:
                    surah_name_clip = generate_surah_info_clip(surah.name_bangla, ayah, is_short=False, duration=duration)
                    current_clips.append(surah_name_clip)

                # Verser number overlay
                if COMMON["enable_channel_info"]:
                    brand_name_clip = generate_brand_clip("তাকওয়া বাংলা", is_short=False, duration=duration)
                    current_clips.append(brand_name_clip)
    
    composite = CompositeVideoClip(current_clips, size=screen_size).set_duration(duration)
    
    # Subclip the audio for the ayah (convert global ms to seconds)
    ayah_audio = full_audio.subclip(gstart_ms / 1000.0, gend_ms / 1000.0)
    composite = composite.set_audio(ayah_audio)
    
    return composite


def generate_surah(surah_number: int, reciter_tag: str):
    reciter = Reciter(reciter_tag)
    surah = Surah(surah_number)
    surah_url = read_surah_data(surah.number, reciter.database_name)
    downloaded_surah_file = download_mp3_temp(surah_url)
    full_audio = AudioFileClip(downloaded_surah_file)
    
    surah_data = read_text_data(surah.number)
    translation_data = read_translation(surah.number)
    timestamp_data = read_timestamp_data(surah.number, reciter.database_name)
    clips = []
    if COMMON["enable_intro"]:
        intro = generate_intro(surah=surah, reciter=reciter, background_image_url=None, is_short=False)
        clips.append(intro)
    
    for tdata in timestamp_data:
        surah_number, ayah, gstart_ms, gend_ms, seg_str = tdata
        clip = create_ayah_clip(surah, ayah, reciter,gstart_ms, gend_ms, surah_data, translation_data, full_audio)
        clips.append(clip)

    if COMMON["enable_outro"]:
        outro = generate_outro(background_image_url=None, is_short=False)
        clips.append(outro)
        
    # Concatenate all ayah clips one after the other
    final_video = concatenate_videoclips(clips)

    # Write the final video to a temporary file.
    #output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    output_path = f"exported_data/videos/quran_video_{surah_number}_{reciter.eng_name}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    info_file_path = generate_details(surah, reciter, True, 1, 1)
    
    return {"video": output_path, "info": info_file_path, "is_short": False, "reciter": reciter.tag}
    