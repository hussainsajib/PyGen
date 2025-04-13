import sqlite3
from collections import defaultdict

TRANSLATION_DB = "./databases/translation/rawai_al_bayan.sqlite"

def nested_dict():
    return defaultdict(nested_dict)

def read_text_data(surah_number: int):
    with sqlite3.connect("./databases/text/Uthmani.sqlite") as conn:
        cursor = conn.cursor()
        query = f"""SELECT * FROM words WHERE word_key LIKE '{surah_number}:%'"""
        cursor.execute(query)
        rows = cursor.fetchall()
        processed_data = defaultdict(nested_dict)
        for row in rows:
            surah_number, ayah_number, word_number = map(int, row[1].split(":"))
            processed_data[surah_number][ayah_number][word_number] = row[2]
        return processed_data
    
def read_translation(surah_number: int):
    with sqlite3.connect(TRANSLATION_DB) as conn:
        cursor = conn.cursor()
        query = f"""SELECT sura, ayah, text FROM translation WHERE sura = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchall()
        translation_dict = {(surah, ayah): translation for surah, ayah, translation in rows}
        return translation_dict