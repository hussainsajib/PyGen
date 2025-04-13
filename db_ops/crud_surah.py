import sqlite3

RECITATION_DATABASE = "./databases/reciter/Yasser-ad-Dussary.sqlite"

def read_surah_data(surah_number: int):
    with sqlite3.connect(RECITATION_DATABASE) as conn:
        cursor = conn.cursor()
        query = f"""SELECT audio_url FROM surah_list WHERE surah_number = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchone()
        return rows[0] if rows else None
    
def read_timestamp_data(surah_number: int):
    with sqlite3.connect(RECITATION_DATABASE) as conn:
        cursor = conn.cursor()
        query = f"""SELECT surah_number, ayah_number, timestamp_from, timestamp_to, segments FROM segments WHERE surah_number = {surah_number}"""
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows if rows else None
    
    