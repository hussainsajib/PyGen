import os
import requests
import json


ACCESS_KEY = os.getenv("ACCESS_KEY")
QURAN_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
TRANSLATION_URL = "https://api.quran.com/api/v4/verses/by_key/{surah}:{verse}?translations=161"
AUDIO_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}/ar.ibrahimakhbar"
IMAGE_API_URL = "https://api.unsplash.com/photos/random?query=universe&orientation=landscape&client_id=gvKXwU6tDDoZl6N3O1YWUIrT19yqZZW6CQLlSEGoxew"


class Verse:
    surah: int = 0
    verse: int = 0
    surah_name: str = None
    arabic: str = None
    translation: str = None
    reciter_name: str = ""
    reciter_key: str = "ar.ibrahimakhbar"
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
        self.get_reciter_name()
        self.arabic = self.fetch_verse_text()
        self.translation = self.fetch_verse_translation()
        self.link_to_audio = self.fetch_verse_audio()
        self.surah_name = f"Surah {self.quran_payload['data']['surah']['englishName']}"

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
    
    def get_reciter_name(self):
        with open("data/reciter_info.json", "r") as f:
            reciters = json.load(f)
            print(reciters)
            for k, v in reciters.items():
                if v["identifier"] == self.reciter_key:
                    self.reciter_name = k
