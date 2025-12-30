import json

class Surah:
    number: int = None
    english_name: str = None
    bangla_name: str = None
    arabic_name: str = None
    english_meaning: str = None
    bangla_meaning: str = None
    total_ayah: int = None

    def __init__(self, number: int):
        self.number = number
        with open("data/surah_data.json", "r", encoding="utf-8") as f:
            data = json.load(f).get(str(number))
            if data:
                self.english_name = data.get("english_name")
                self.bangla_name = data.get("bangla_name")
                self.arabic_name = data.get("arabic_name")
                self.english_meaning = data.get("english_meaning")
                self.bangla_meaning = data.get("bangla_meaning")
                self.total_ayah = int(data.get("total_ayah", 0))

    def __repr__(self):
        return f"<Surah Class: {self.number} - {self.english_name}>"