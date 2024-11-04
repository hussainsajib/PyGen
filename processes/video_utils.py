import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger
from processes.verse import Verse, IMAGE_API_URL
from processes.video_configs import (
    MAIN_TEXT_BOXES_SIZE, ARABIC_TEXT_CLIP_POS, TRANS_TEXT_CLIP_POS, FOOTER_FONT_SIZE, FOOTER_FONT_COLOR)



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
            arabic_text_clip = TextClip(v.arabic, fontsize=50, color='white', method='caption', size=MAIN_TEXT_BOXES_SIZE)\
                                .set_position(lambda t: ARABIC_TEXT_CLIP_POS)\
                                .set_duration(audio_clip.duration)
            current_clips.append(arabic_text_clip)

            # Create translation overlay
            translation_clip = TextClip(v.translation, fontsize=30, color='white', font='Kalpurush', method='caption', size=MAIN_TEXT_BOXES_SIZE)\
                                .set_position(lambda t: TRANS_TEXT_CLIP_POS)\
                                .set_duration(audio_clip.duration)
            current_clips.append(translation_clip)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            surah_name_clip = TextClip(f'{v.surah_name}:{str(v.verse)}', fontsize=FOOTER_FONT_SIZE, color=FOOTER_FONT_COLOR)\
                                .set_position(('center', 'bottom'))\
                                .set_duration(audio_clip.duration)\
                                .margin(bottom=10)
            current_clips.append(surah_name_clip)

            # Reciter name overlay
            reciter_name_clip = TextClip(v.reciter_name, fontsize=FOOTER_FONT_SIZE, color=FOOTER_FONT_COLOR)\
                                .set_position(('left', 'bottom'))\
                                .set_duration(audio_clip.duration)\
                                .margin(bottom=10, left=10)
            current_clips.append(reciter_name_clip)

            # Verser number overlay
            verse_number_clip = TextClip("Taqwa Bangla", fontsize=FOOTER_FONT_SIZE, color=FOOTER_FONT_COLOR)\
                                .set_position(('right', 'bottom'))\
                                .set_duration(audio_clip.duration)\
                                .margin(bottom=10, right=10)
            current_clips.append(verse_number_clip)

            # Composite the video with text and audio
            video_clip = CompositeVideoClip(current_clips).set_audio(audio_clip)
            logger.info(f"Verse ${verse} CompositeVideoClip created")
            
            clips.append(video_clip)
            
        except Exception as e:
            print(f"Error processing verse {verse}: {e}")
            continue
    
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
