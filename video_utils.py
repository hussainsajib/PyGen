import requests
from moviepy.editor import *
import os

QURAN_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
AUDIO_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}/ar.alafasy"
IMAGE_API_URL = "https://api.unsplash.com/photos/random?query=background&client_id=YOUR_UNSPLASH_API_KEY"

def fetch_verse_text(surah, verse):
    response = requests.get(QURAN_API_URL.format(surah=surah, verse=verse))
    if response.status_code == 200:
        return response.json()['data']['text']
    return None

def fetch_verse_audio(surah, verse):
    response = requests.get(AUDIO_API_URL.format(surah=surah, verse=verse))
    if response.status_code == 200:
        return response.json()['data']['audio']
    return None

def fetch_background_image():
    response = requests.get(IMAGE_API_URL)
    if response.status_code == 200:
        return response.json()['urls']['full']
    return None

def generate_video(surah, start_verse, end_verse):
    clips = []
    for verse in range(start_verse, end_verse + 1):
        verse_text = fetch_verse_text(surah, verse)
        verse_audio_url = fetch_verse_audio(surah, verse)
        background_image_url = fetch_background_image()
        
        # Skip if any component is missing
        if not (verse_text and verse_audio_url and background_image_url):
            print(f"Skipping verse {verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(verse_audio_url)
            image_clip = ImageClip(background_image_url).set_duration(audio_clip.duration)
            
            # Create the text overlay
            text_clip = TextClip(verse_text, fontsize=24, color='white')
            text_clip = text_clip.set_position('center').set_duration(audio_clip.duration)
            
            # Composite the video with text and audio
            video_clip = CompositeVideoClip([image_clip, text_clip])
            video_clip = video_clip.set_audio(audio_clip)
            
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
    final_video.write_videofile(output_path, codec='libx264', fps=24)
    
    return output_path
