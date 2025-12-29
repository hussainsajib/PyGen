import sqlite3
import os
from collections import defaultdict
from config_manager import config_manager

TRANSLATION_DB = "./databases/translation/bengali/rawai_al_bayan.sqlite"

def nested_dict():
    return defaultdict(nested_dict)

def get_full_translation_for_ayah(surah_number: int, ayah_number: int, db_name: str = "rawai_al_bayan"):
    """Fetches the full translation text for a specific ayah."""
    language = config_manager.get("DEFAULT_LANGUAGE", "bengali")
    
    # Construct path based on language
    db_path = f"./databases/translation/{language}/{db_name}.sqlite"
    
    # Fallback/Checks
    if not os.path.exists(db_path):
         # Try legacy/direct path if provided
         if os.path.exists(db_name):
             db_path = db_name
         elif os.path.exists(f"databases/translation/{db_name}.sqlite"):
             # Fallback to root translation folder (legacy)
             db_path = f"databases/translation/{db_name}.sqlite"
         else:
             # Attempt to find it in other languages? Or just warn.
             print(f"Warning: Translation DB {db_path} not found. Trying default fallback.")
             # Fallback to hardcoded default (likely Bengali for now as it's the main one)
             db_path = f"./databases/translation/bengali/rawai_al_bayan.sqlite"

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
    language = config_manager.get("DEFAULT_LANGUAGE", "bengali")
    db_name = "rawai_al_bayan"
    db_path = f"./databases/translation/{language}/{db_name}.sqlite"
    
    if not os.path.exists(db_path):
        db_path = TRANSLATION_DB

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = f"""SELECT sura, ayah, text FROM translation WHERE sura = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchall()
        translation_dict = {(surah, ayah): translation for surah, ayah, translation in rows}
        return translation_dict