import sqlite3
import json
import os

def get_wbw_timestamps(db_path: str, surah_number: int, start_ayah: int, end_ayah: int):
    """
    Fetches word-level timestamps for a specific surah and ayah range from a WBW SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database file.
        surah_number (int): Surah number.
        start_ayah (int): Starting ayah number.
        end_ayah (int): Ending ayah number.
        
    Returns:
        dict: A dictionary where keys are ayah numbers and values are lists of word segments [word_num, start_ms, end_ms].
    """
    if not os.path.exists(db_path):
        print(f"WBW Database file not found: {db_path}")
        return {}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT ayah_number, segments 
            FROM segments 
            WHERE surah_number = ? AND ayah_number BETWEEN ? AND ?
        """
        cursor.execute(query, (surah_number, start_ayah, end_ayah))
        rows = cursor.fetchall()
        
        wbw_data = {}
        for row in rows:
            ayah_num, segments_json = row
            try:
                segments = json.loads(segments_json)
                # Filter out segments that don't have start/end times (e.g. [[1]])
                valid_segments = [s for s in segments if len(s) == 3]
                wbw_data[ayah_num] = valid_segments
            except json.JSONDecodeError:
                print(f"Error decoding segments JSON for Surah {surah_number}, Ayah {ayah_num}")
                
        return wbw_data
    except Exception as e:
        print(f"Error querying WBW database: {e}")
        return {}
    finally:
        conn.close()
