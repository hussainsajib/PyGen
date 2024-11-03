import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.all import crop

from logger import logger


ACCESS_KEY = os.getenv("ACCESS_KEY")
QURAN_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
AUDIO_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}/ar.alafasy"
IMAGE_API_URL = "https://api.unsplash.com/photos/random?query=universe&orientation=landscape&client_id=gvKXwU6tDDoZl6N3O1YWUIrT19yqZZW6CQLlSEGoxew"

def fetch_verse_text(surah, verse):
    response = requests.get(QURAN_API_URL.format(surah=surah, verse=verse))
    if response.status_code != 200:
        raise Exception("Response from QURAN API for the text was not successful")
    return response.json()['data']['text']

def fetch_verse_audio(surah, verse):
    response = requests.get(AUDIO_API_URL.format(surah=surah, verse=verse))
    if response.status_code != 200:
        raise Exception("Response from QURAN API for the audio was not successful")
    return response.json()['data']['audio']

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
        verse_text = fetch_verse_text(surah, verse)
        if verse == 1 and surah != 1:
            print(verse_text[2:15])
            verse_text = verse_text.replace("بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ", '')
        logger.info(f"Verse {verse} text downloaded")

        verse_audio_url = fetch_verse_audio(surah, verse)
        logger.info(f"Verse {verse} audio downloaded")
        
        # Skip if any component is missing
        if not (verse_text and verse_audio_url and background_image_url):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(verse_audio_url)
            image_clip = ImageClip(background_image_url).set_duration(audio_clip.duration)
            logger.info(f"Verse ${verse} ImageClip created")

            x1, y1, width, height = 100, 50, 1280, 720
            #image_clip = crop(image_clip, x1=x1, y1=y1, width=width, height=height)

            # Create the text overlay
            text_clip = TextClip(verse_text, fontsize=40, color='white')
            text_clip = text_clip.set_position('center').set_duration(audio_clip.duration)
            logger.info(f"Verse ${verse} TextClip created")

            # Composite the video with text and audio
            video_clip = CompositeVideoClip([image_clip, text_clip])
            video_clip = video_clip.set_audio(audio_clip)
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
    final_video = concatenate_videoclips(clips, method="compose")
    output_path = f"quran_video_{surah}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
