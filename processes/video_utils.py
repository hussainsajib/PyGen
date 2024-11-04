import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger
from processes.reciter import Reciter
from processes.surah import Surah
from processes.verse import Verse, IMAGE_API_URL
from processes.video_configs import *

TARGET_RESOLUTION = (1920, 1080)


def fetch_background_image():
    response = requests.get(IMAGE_API_URL)
    if response.status_code != 200:
        raise Exception("Response from Unsplash API for the background image was not successful")
    return response.json()['urls']['regular']

def generate_background(background_image_url: str, duration: int, resolution: tuple):
    background_clip = ImageClip(background_image_url).set_duration(duration)
    return resize(background_clip, resolution)

def generate_intro(surah: Surah, reciter: Reciter, background_image_url):
    background = generate_background(background_image_url, INTRO_DURATION, TARGET_RESOLUTION)
    title = TextClip(txt=surah.name_bangla, font="kalpurush", fontsize=100, color="white")\
            .set_position(("center", 0.4), relative=True)\
            .set_duration(INTRO_DURATION)
    sub_title = TextClip(txt=reciter.bangla_name, font="kalpurush", fontsize=50, color='white')\
                .set_position(("center", 0.6), relative=True)\
                .set_duration(INTRO_DURATION)
    return CompositeVideoClip([background, title, sub_title])


def generate_video(surah_number, start_verse, end_verse):
    # Prepare background
    background_image_url = fetch_background_image()
    logger.info("Background image downloaded")

    surah = Surah(surah_number)
    reciter = Reciter(tag=RECITER)
    intro = generate_intro(surah, reciter, background_image_url)
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

            background_clip = generate_background(background_image_url, audio_clip.duration, TARGET_RESOLUTION)
            current_clips.append(background_clip)

            # Create the text overlay
            arabic_text_clip = TextClip(v.arabic, **ARABIC_TEXT_BOX_CONFIG)\
                                .set_position(lambda t: ARABIC_TEXT_CLIP_POS)\
                                .set_duration(audio_clip.duration)
            current_clips.append(arabic_text_clip)

            # Create translation overlay
            translation_clip = TextClip(v.translation, **TRANSLATON_TEXT_BOX_CONFIG)\
                                .set_position(lambda t: TRANS_TEXT_CLIP_POS)\
                                .set_duration(audio_clip.duration)
            current_clips.append(translation_clip)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            surah_name_clip = TextClip(f'{v.surah.name_bangla} : {str(v.verse)}', font="kalpurush", **FOOTER_CONFIG)\
                                .set_position(lambda t:(0.45, 0.95), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(surah_name_clip)

            # Reciter name overlay
            reciter_name_clip = TextClip(v.reciter.bangla_name, font="kalpurush", **FOOTER_CONFIG)\
                                .set_position((0.05, 0.95), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(reciter_name_clip)

            # Verser number overlay
            taqwa_bangla_clip = TextClip("Taqwa Bangla", **FOOTER_CONFIG)\
                                .set_position((0.85, 0.95), relative=True)\
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
    final_video = concatenate_videoclips(clips)
    output_path = f"quran_video_{surah_number}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
