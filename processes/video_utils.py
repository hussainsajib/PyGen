import os
import requests

from fastapi import HTTPException
from moviepy.editor import *
from moviepy.video.fx.resize import resize 

from processes.logger import logger


ACCESS_KEY = os.getenv("ACCESS_KEY")
QURAN_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
TRANSLATION_URL = "https://api.quran.com/api/v4/verses/by_key/{surah}:{verse}?translations=161"
AUDIO_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}/ar.ibrahimakhbar"
IMAGE_API_URL = "https://api.unsplash.com/photos/random?query=universe&orientation=landscape&client_id=gvKXwU6tDDoZl6N3O1YWUIrT19yqZZW6CQLlSEGoxew"
TEXTBOX_SIZE = (1500, 400)

class Verse:
    surah: int = 0
    verse: int = 0
    surah_name: str = None
    arabic: str = None
    translation: str = None
    reciter_name: str = "Misary Rashid al-Afasy"
    link_to_audio: str = None

    quran_payload: str = None
    translation_payload: str = None
    audio_payload: str = None

    def __init__(self, surah: int, verse: int) -> None:
        self.surah = surah
        self.verse = verse
        self.get_quran_data()
        self.get_audio_data()
        self.get_translation_data()
        self.arabic = self.fetch_verse_text()
        self.translation = self.fetch_verse_translation()
        self.link_to_audio = self.fetch_verse_audio()
        self.surah_name = "Surah " +self.quran_payload['data']['surah']['englishName']

    def get_quran_data(self):
        response = requests.get(QURAN_API_URL.format(surah=self.surah, verse=self.verse))
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the text was not successful")
        self.quran_payload = response.json()

    def get_translation_data(self):
        response = requests.get(TRANSLATION_URL.format(surah=self.surah, verse=self.verse))
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the translation was not successful")
        self.translation_payload = response.json()

    def get_audio_data(self):
        response = requests.get(AUDIO_API_URL.format(surah=self.surah, verse=self.verse))
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the audio was not successful")
        self.audio_payload = response.json()

    def fetch_verse_text(self):
        verse_text = self.quran_payload['data']['text']
        if self.verse == 1 and self.surah != 1:
            verse_text = verse_text.replace("بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ", '')
        return verse_text 

    def fetch_verse_translation(self):
        return self.translation_payload['verse']['translations'][0]['text']

    def fetch_verse_audio(self):
        return self.audio_payload['data']['audio']



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
        v = Verse(surah=surah, verse=verse)
        
        # Skip if any component is missing
        if not (v.arabic and v.link_to_audio and v.translation and background_image_url):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(v.link_to_audio)
            image_clip = ImageClip(background_image_url).set_duration(audio_clip.duration)
            image_clip = resize(image_clip, target_resolution)
            logger.info(f"Verse ${verse} ImageClip created")

            x1, y1, width, height = 100, 50, 1280, 720
            #image_clip = crop(image_clip, x1=x1, y1=y1, width=width, height=height)

            # Create the text overlay
            text_clip = TextClip(v.arabic, fontsize=50, color='white', method='caption', size=TEXTBOX_SIZE)
            text_clip = text_clip.set_position(lambda t: ('center', 200)).set_duration(audio_clip.duration)

            # Create translation overlay
            translation_clip = TextClip(v.translation, fontsize=30, color='white', font='Kalpurush', method='caption', size=TEXTBOX_SIZE)
            translation_clip = translation_clip.set_position(lambda t: ('center', 500)).set_duration(audio_clip.duration)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            surah_name_clip = TextClip(f'{v.surah_name}:{str(v.verse)}', fontsize=30, color='white')
            surah_name_clip = surah_name_clip.set_position(('center', 'bottom')).set_duration(audio_clip.duration).margin(bottom=10)

            # Reciter name overlay
            reciter_name_clip = TextClip(v.reciter_name, fontsize=30, color='white')
            reciter_name_clip = reciter_name_clip.set_position(('left', 'bottom')).set_duration(audio_clip.duration).margin(bottom=10, left=10)

            # Verser number overlay
            verse_number_clip = TextClip("Taqwa Bangla", fontsize=30, color='white')
            verse_number_clip = verse_number_clip.set_position(('right', 'bottom')).set_duration(audio_clip.duration).margin(bottom=10, right=10)

            # Composite the video with text and audio
            video_clip = CompositeVideoClip([image_clip, text_clip, translation_clip, surah_name_clip, reciter_name_clip, verse_number_clip])
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
    print(clips)
    final_video = concatenate_videoclips(clips)
    output_path = f"quran_video_{surah}_{start_verse}_{end_verse}.mp4"
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    return output_path
