import sqlite3
import os
from collections import defaultdict

TRANSLATION_DB = "./databases/translation/rawai_al_bayan.sqlite"

def nested_dict():
    return defaultdict(nested_dict)

def get_full_translation_for_ayah(surah_number: int, ayah_number: int, db_name: str = "rawai_al_bayan"):
    """Fetches the full translation text for a specific ayah."""
    db_path = f"./databases/translation/{db_name}.sqlite"
    # Fallback to default path if only name is provided without extension or if path constructed is wrong
    if not os.path.exists(db_path):
         # Try direct path if db_name looks like a path or just use default
         if os.path.exists(db_name):
             db_path = db_name
         elif os.path.exists(f"databases/translation/{db_name}.sqlite"):
             db_path = f"databases/translation/{db_name}.sqlite"
         else:
             print(f"Warning: Translation DB {db_path} not found. Fallback to default.")
             db_path = TRANSLATION_DB

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT text FROM translation WHERE sura = ? AND ayah = ?"
            cursor.execute(query, (surah_number, ayah_number))
            result = cursor.fetchone()
            return result[0] if result else ""
    except Exception as e:
        print(f"Error fetching full translation: {e}")
        return ""

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