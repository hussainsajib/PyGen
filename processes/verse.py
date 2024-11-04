import os
import requests
import json
from processes.reciter import Reciter
from processes.surah import Surah
from processes.configs import *


ACCESS_KEY = os.getenv("ACCESS_KEY")


class Verse:
    surah: Surah = None
    verse: int = 0
    surah_name: str = None
    arabic: str = None
    translation: str = None
    reciter: Reciter = ""
    link_to_audio: str = None

    quran_payload: str = None
    translation_payload: str = None
    audio_payload: str = None

    def __init__(self, surah: Surah, verse: int, reciter: Reciter) -> None:
        self.surah = surah
        self.verse = verse
        self.reciter = reciter
        self.get_quran_data()
        self.get_audio_data()
        self.get_translation_data()
        self.arabic = self.fetch_verse_text()
        self.translation = self.fetch_verse_translation()
        self.link_to_audio = self.fetch_verse_audio()
        self.surah_name = f"Surah {self.quran_payload['data']['surah']['englishName']}"

    def get_quran_data(self):
        print(f"surah {self.surah.number}, ayah: {self.verse}")
        response = requests.get(QURAN_API_URL.format(surah=self.surah.number, verse=self.verse))
        
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the text was not successful")
        self.quran_payload = response.json()

    def get_translation_data(self):
        response = requests.get(TRANSLATION_URL.format(surah=self.surah.number, verse=self.verse))
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the translation was not successful")
        self.translation_payload = response.json()

    def get_audio_data(self):
        response = requests.get(AUDIO_API_URL.format(surah=self.surah.number, verse=self.verse, reciter=self.reciter.tag))
        if response.status_code != 200:
            raise Exception("Response from QURAN API for the audio was not successful")
        self.audio_payload = response.json()

    def fetch_verse_text(self):
        verse_text = self.quran_payload['data']['text']
        if self.verse == 1 and self.surah.number != "1":
            verse_text = verse_text.replace("بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ", '')
        return verse_text 

    def fetch_verse_translation(self):
        return self.translation_payload['verse']['translations'][0]['text']

    def fetch_verse_audio(self):
        return self.audio_payload['data']['audio']
    
