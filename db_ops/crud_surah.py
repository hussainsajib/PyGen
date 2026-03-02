import sqlite3
import json
import logging
import os

logger = logging.getLogger("uvicorn.error")

RECITATION_DATABASE_BASEURL = "./databases/reciter/{}.sqlite"

def read_surah_data(surah_number: int, reciter_db_name: str):
    if not reciter_db_name:
        raise ValueError("Reciter database name is not configured.")
        
    database = RECITATION_DATABASE_BASEURL.format(reciter_db_name)
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        query = f"""SELECT audio_url FROM surah_list WHERE surah_number = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchone()
        return rows[0] if rows else None

    
def read_timestamp_data(surah_number: int, reciter_db_name: str):
    database = RECITATION_DATABASE_BASEURL.format(reciter_db_name)
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        query = f"""SELECT surah_number, ayah_number, timestamp_from, timestamp_to, segments FROM segments WHERE surah_number = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows if rows else None

async def get_surah_by_number(surah_number: int):
    """
    Returns surah metadata from surah_data.json.
    Matches the expected interface in app.py (surah_obj.bangla_name).
    """
    try:
        json_path = os.path.join("data", "surah_data.json")
        if not os.path.exists(json_path):
            logger.error(f"surah_data.json not found at {json_path}")
            return None
            
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            surah_info = data.get(str(surah_number))
            if surah_info:
                # Create a simple class to mock the SQLAlchemy model behavior
                class SurahMock:
                    def __init__(self, info):
                        self.bangla_name = info.get("bangla_name")
                        self.english_name = info.get("english_name")
                        self.number = int(info.get("serial"))
                return SurahMock(surah_info)
    except Exception as e:
        logger.error(f"Error reading surah_data.json: {e}")
    return None
