import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 
from bangla import convert_english_digit_to_bangla_digit as e2b
from convert_numbers import english_to_arabic as e2a

from processes.logger import logger
from processes.reciter import Reciter
from processes.surah import Surah
from processes.verse import Verse, IMAGE_API_URL
from processes.video_configs import *

TARGET_RESOLUTION = (TARGET_WIDTH, TARGET_HEIGHT)


def fetch_background_image():
    response = requests.get(IMAGE_API_URL)
    if response.status_code != 200:
        raise Exception("Response from Unsplash API for the background image was not successful")
    return response.json()['urls']['regular']

def generate_background(background_image_url: str, duration: int, resolution: tuple):
    background_clip = ImageClip(BACKGROUND).set_opacity(BACKGROUND_OPACITY).set_duration(duration)
    return resize(background_clip, resolution)

def generate_solid_background(duration: int, resolution: tuple):
    return ColorClip(size=resolution, color=BACKGROUND_RGB).set_duration(duration)

def generate_intro(surah: Surah, reciter: Reciter, background_image_url):
    audio = AudioFileClip("recitation_data/basmalah.mp3")
    background = generate_solid_background(audio.duration, TARGET_RESOLUTION)
    title = TextClip(txt=f"সুরাহ {surah.name_bangla}", font="kalpurush", fontsize=100, color=FONT_COLOR)\
            .set_position(("center", 0.4), relative=True)\
            .set_duration(audio.duration)
    sub_title = TextClip(txt=reciter.bangla_name, font="kalpurush", fontsize=50, color=FONT_COLOR)\
                .set_position(("center", 0.6), relative=True)\
                .set_duration(audio.duration)
    return CompositeVideoClip([background, title, sub_title]).set_audio(audio)

def generate_outro(background_image_url):
    background = generate_solid_background(duration=5, resolution=TARGET_RESOLUTION)
    title = TextClip("তাকওয়া বাংলা", font="kalpurush", fontsize=70, color=FONT_COLOR)\
            .set_position(('center', 'center'))\
            .set_duration(5)
    return CompositeVideoClip([background, title])


def generate_video(surah_number, start_verse, end_verse):
    # Prepare background
    background_image_url = fetch_background_image()
    logger.info("Background image downloaded")

    surah = Surah(surah_number)
    reciter = Reciter(tag=RECITER)
    intro = generate_intro(surah, reciter, background_image_url)
    outro = generate_outro(background_image_url)
    clips = [intro]

    for verse in range(start_verse, end_verse + 1):
        current_clips = []
        v = Verse(surah=surah, verse=verse, reciter=reciter)
        
        # Skip if any component is missing
        if not (v.arabic and v.link_to_audio and v.translation and background_image_url):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(v.link_to_audio)

            background_clip = generate_solid_background(audio_clip.duration, TARGET_RESOLUTION)
            current_clips.append(background_clip)

            # Create the text overlay
            arabic_text_clip = TextClip(f"{v.arabic[:-1]} \u06DD{e2a(v.verse)}", **ARABIC_TEXT_BOX_CONFIG)
            arabic_text_clip = arabic_text_clip.set_position(('center', (TARGET_HEIGHT // 2) - (arabic_text_clip.h + 25)))\
                                .set_duration(audio_clip.duration)
            current_clips.append(arabic_text_clip)

            # Create translation overlay
            translation_clip = TextClip(v.translation, **TRANSLATON_TEXT_BOX_CONFIG)
            translation_clip = translation_clip.set_position(('center', (TARGET_HEIGHT // 2) + 25))\
                                .set_duration(audio_clip.duration)
            current_clips.append(translation_clip)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            surah_name_clip = TextClip(f'{v.surah.name_bangla} : {e2b(str(v.verse))}', font="kalpurush", **FOOTER_CONFIG)\
                                .set_position(lambda t:(0.45, 0.92), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(surah_name_clip)

            # Reciter name overlay
            reciter_name_clip = TextClip(v.reciter.bangla_name, font="kalpurush", **FOOTER_CONFIG)\
                                .set_position((0.05, 0.92), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(reciter_name_clip)

            # Verser number overlay
            taqwa_bangla_clip = TextClip("তাকওয়া বাংলা", font="kalpurush", **FOOTER_CONFIG)\
                                .set_position((0.85, 0.92), relative=True)\
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

    # Concatenate all clips
    clips.append(outro)
    final_video = concatenate_videoclips(clips)
    output_path = f"quran_video_{surah_number}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
