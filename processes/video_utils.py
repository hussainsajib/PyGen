import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 
from bangla import convert_english_digit_to_bangla_digit as e2b
from convert_numbers import english_to_arabic as e2a

from processes.logger import logger
from processes.Classes.reciter import Reciter
from processes.Classes.surah import Surah
from processes.Classes.verse import Verse
from processes.video_configs import *


def get_resolution(is_short: bool) -> tuple:
    return (SHORT["width"], SHORT["height"]) if is_short else (LONG["width"], LONG["height"])


def fetch_background_image():
    return COMMON["bg_image"]


def generate_image_background(background_image_url: str, duration: int, resolution: tuple):
    background_clip = ImageClip(background_image_url).set_opacity(BACKGROUND_OPACITY).set_duration(duration)
    return resize(background_clip, resolution)


def generate_solid_background(duration: int, resolution: tuple):
    return ColorClip(size=resolution, color=BACKGROUND_RGB).set_duration(duration)


def generate_background(background_image_url: str, duration: int, resolution: tuple):
    if background_image_url:
        return generate_image_background(background_image_url, duration, resolution)
    return generate_solid_background(duration, resolution)


def generate_intro(surah: Surah, reciter: Reciter, background_image_url, is_short: bool):
    intro_clips = []
    audio = AudioFileClip("recitation_data/basmalah.mp3")
    background = generate_background(background_image_url, audio.duration, get_resolution(is_short))
    intro_clips.append(background)

    if COMMON["enable_title"]:
        title = TextClip(txt=f"সুরাহ {surah.name_bangla}", font="kalpurush", fontsize=100, color=FONT_COLOR)\
            .set_position(("center", 0.4), relative=True)\
            .set_duration(audio.duration)
        intro_clips.append(title)

    if COMMON["enable_subtitle"]:
        sub_title = TextClip(txt=reciter.bangla_name, font="kalpurush", fontsize=50, color=FONT_COLOR)\
                .set_position(("center", 0.6), relative=True)\
                .set_duration(audio.duration)
        intro_clips.append(sub_title)
    
    return CompositeVideoClip(intro_clips).set_audio(audio)


def generate_outro(background_image_url, is_short):
    background = generate_background(background_image_url, duration=5, resolution=get_resolution(is_short))
    title = TextClip("তাকওয়া বাংলা", font="kalpurush", fontsize=70, color=FONT_COLOR)\
            .set_position(('center', 'center'))\
            .set_duration(5)
    return CompositeVideoClip([background, title])


def generate_video(surah_number, start_verse, end_verse, is_short: bool):
    # Prepare background

    background_image_url = fetch_background_image() if not COMMON["is_solid_bg"] else None
    logger.info("Background image downloaded")

    surah = Surah(surah_number)
    reciter = Reciter(tag=RECITER)
    clips = []
    
    if not is_short and COMMON["enable_intro"]:
        intro = generate_intro(surah, reciter, background_image_url, is_short)
        clips.append(intro)
    
    for verse in range(start_verse, end_verse + 1):
        current_clips = []
        v = Verse(surah=surah, verse=verse, reciter=reciter)
        
        # Skip if any component is missing
        if not (v.arabic and v.link_to_audio and v.translation and (COMMON["is_solid_bg"] or background_image_url)):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(v.link_to_audio)

            background_clip = generate_background(background_image_url, audio_clip.duration, get_resolution(is_short))
            current_clips.append(background_clip)

            # Create the text overlay
            # Unicode \u06DD is adding the ayah marking at the end
            arabic_sizes = COMMON["f_arabic_size"](is_short)
            arabic_text_clip = TextClip(f"{v.arabic[:-1]} \u06DD{e2a(v.verse)}", **arabic_sizes, **COMMON["arabic_textbox_config"])
            arabic_pos = COMMON["f_arabic_position"](is_short, arabic_text_clip.h)
            arabic_text_clip = arabic_text_clip.set_position(('center', arabic_pos))\
                                .set_duration(audio_clip.duration)
            current_clips.append(arabic_text_clip)

            # Create translation overlay
            translation_sizes = COMMON["f_translation_size"](is_short)
            translation_clip = TextClip(v.translation, **translation_sizes, **COMMON["translation_textbox_config"])
            translation_pos = COMMON["f_translation_position"](is_short)
            translation_clip = translation_clip.set_position(('center', translation_pos))\
                                .set_duration(audio_clip.duration)
            current_clips.append(translation_clip)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            if COMMON["enable_footer"]:
                # Reciter name overlay
                if COMMON["enable_reciter_info"]:
                    reciter_name_clip = TextClip(v.reciter.bangla_name, font="kalpurush", **FOOTER_CONFIG)
                    reciter_pos = COMMON["f_reciter_info_position"](is_short, reciter_name_clip.w)
                    reciter_name_clip = reciter_name_clip.set_position(reciter_pos, relative=True)\
                                    .set_duration(audio_clip.duration)
                    current_clips.append(reciter_name_clip)

                if COMMON["enable_surah_info"]:
                    surah_name_clip = TextClip(f'{v.surah.name_bangla} : {e2b(str(v.verse))}', font="kalpurush", **FOOTER_CONFIG)
                    surah_pos = COMMON["f_surah_info_position"](is_short, surah_name_clip.w)
                    surah_name_clip = surah_name_clip.set_position(surah_pos, relative=True)\
                                    .set_duration(audio_clip.duration)
                    current_clips.append(surah_name_clip)

                # Verser number overlay
                if COMMON["enable_channel_info"]:
                    taqwa_bangla_clip = TextClip("তাকওয়া বাংলা", font="kalpurush", **FOOTER_CONFIG)
                    channel_pos = COMMON["f_channel_info_position"](is_short, taqwa_bangla_clip.w)
                    taqwa_bangla_clip = taqwa_bangla_clip.set_position(channel_pos, relative=True)\
                                        .set_duration(audio_clip.duration)
                    current_clips.append(taqwa_bangla_clip)

            # Composite the video with text and audio
            video_clip = CompositeVideoClip(current_clips).set_audio(audio_clip)
            logger.info(f"Verse ${verse} CompositeVideoClip created")
            
            clips.append(video_clip)
            
        except Exception as e:
            print(str(e))
            raise
    
    # Check if clips list is empty before concatenation
    if not clips:
        print("No valid clips were generated.")
        return None


    if not is_short and COMMON["enable_outro"]:
        outro = generate_outro(background_image_url, is_short)
        clips.append(outro)

    final_video = concatenate_videoclips(clips)
    output_path = f"exported_data/videos/quran_video_{surah_number}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
