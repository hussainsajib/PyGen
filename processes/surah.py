import json
from processes.configs import *

class Surah:
    number: int = 0
    name_ar: str = None
    name_eng: str = None
    name_bangla: str = None
    name_translation_eng: str = None
    name_translation_bangla: str = None
    total_ayah: int = 0
    total_ruku: int = 0
    type_of_revelation: str = None

    def __init__(self, num: int) -> None:
        self.number = num
        self.get_quran_data()

    def get_quran_data(self):
        with open("data/surah_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)[str(self.number)]

            self.name_ar = data["arabic_name"]
            self.name_eng = data["english_name"]
            self.name_bangla = data["bangla_name"]
            self.name_translation_eng = data["english_meaning"]
            self.name_translation_bangla = data["bangla_meaning"]
            self.total_ayah = data["total_ayah"]
            self.total_ruku = data["total_ruku"]
            self.type_of_revelation = data["relevation_place"]
        