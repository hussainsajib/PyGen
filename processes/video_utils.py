import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger
from processes.verse import Verse, IMAGE_API_URL
from processes.video_configs import (
    ARABIC_TEXT_CLIP_POS, ARABIC_TEXT_BOX_CONFIG, TRANS_TEXT_CLIP_POS, TRANSLATON_TEXT_BOX_CONFIG, FOOTER_CONFIG)



def fetch_background_image():
    response = requests.get(IMAGE_API_URL)
    if response.status_code != 200:
        raise Exception("Response from Unsplash API for the background image was not successful")
    return response.json()['urls']['regular']

def generate_video(surah, start_verse, end_verse):
    clips = []
    
    # Prepare background
    background_image_url = fetch_background_image()
    logger.info("Background image downloaded")

    target_resolution = (1920, 1080)

    for verse in range(start_verse, end_verse + 1):
        current_clips = []
        v = Verse(surah=surah, verse=verse)
        
        # Skip if any component is missing
        if not (v.arabic and v.link_to_audio and v.translation and background_image_url):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(v.link_to_audio)

            background_clip = ImageClip(background_image_url).set_duration(audio_clip.duration)
            background_clip = resize(background_clip, target_resolution)
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
            surah_name_clip = TextClip(f'{v.surah_name} : {str(v.verse)}', **FOOTER_CONFIG)\
                                .set_position(lambda t:(0.45, 0.95), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(surah_name_clip)

            # Reciter name overlay
            reciter_name_clip = TextClip(v.reciter_name, **FOOTER_CONFIG)\
                                .set_position((0.05, 0.95), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(reciter_name_clip)

            # Verser number overlay
            verse_number_clip = TextClip("Taqwa Bangla", **FOOTER_CONFIG)\
                                .set_position((0.85, 0.95), relative=True)\
                                .set_duration(audio_clip.duration)
            current_clips.append(verse_number_clip)

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
    print(clips)
    final_video = concatenate_videoclips(clips)
    output_path = f"quran_video_{surah}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
