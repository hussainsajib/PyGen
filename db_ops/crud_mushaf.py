import sqlite3
import os
import json

DB_15_LINES = "databases/text/qpc-v2-15-lines.db"
DB_WBW = "databases/text/word_by_word_qpc-v2.db"
DB_JUZ = "databases/text/quran-metadata-juz.sqlite"

def get_juz_boundaries(juz_number: int):
    """
    Retrieves the start and end surah/ayah for a given juz.
    """
    if not os.path.exists(DB_JUZ):
        return None
        
    conn = sqlite3.connect(DB_JUZ)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT first_verse_key, last_verse_key, verse_mapping FROM juz WHERE juz_number = ?", (juz_number,))
        row = cursor.fetchone()
        if not row:
            return None
            
        first_key, last_key, mapping_str = row
        start_surah, start_ayah = map(int, first_key.split(":"))
        end_surah, end_ayah = map(int, last_key.split(":"))
        
        return {
            "start_surah": start_surah,
            "start_ayah": start_ayah,
            "end_surah": end_surah,
            "end_ayah": end_ayah,
            "verse_mapping": json.loads(mapping_str)
        }
    finally:
        conn.close()

def get_surah_page_range(surah_number: int):
    """
    Returns the start and end page for a given surah by resolving word ID boundaries.
    """
    conn_wbw = sqlite3.connect(DB_WBW)
    try:
        cursor_wbw = conn_wbw.cursor()
        cursor_wbw.execute("SELECT MIN(id), MAX(id) FROM words WHERE surah = ?", (surah_number,))
        start_word_id, end_word_id = cursor_wbw.fetchone()
    finally:
        conn_wbw.close()
        
    if start_word_id is None:
        return (None, None)

    conn_15line = sqlite3.connect(DB_15_LINES)
    try:
        cursor_15line = conn_15line.cursor()
        # Find pages where the word range overlaps with the Surah's word range
        cursor_15line.execute("""
            SELECT MIN(page_number), MAX(page_number)
            FROM pages
            WHERE first_word_id != '' AND last_word_id != ''
              AND NOT (last_word_id < ? OR first_word_id > ?)
        """, (start_word_id, end_word_id))
        return cursor_15line.fetchone()
    finally:
        conn_15line.close()

def get_mushaf_page_data(page_number: int):
    """
    Retrieves the structured page data for the 15-line Mushaf layout.
    """
    conn_15line = sqlite3.connect(DB_15_LINES)
    conn_wbw = sqlite3.connect(DB_WBW)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch lines for the page
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        for line in lines:
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # Global Suppression: Surah 1 (Basmallah is Ayah 1) and Surah 9 (No Basmallah)
            if l_type == 'basmallah' and surah_num in [1, 9]:
                continue

            words = []
            if start_id != '' and end_id != '':
                # 2. Fetch words for this line
                cursor_wbw.execute("""
                    SELECT id, location, surah, ayah, word, text
                    FROM words
                    WHERE id BETWEEN ? AND ?
                    ORDER BY id
                """, (start_id, end_id))
                
                words_raw = cursor_wbw.fetchall()
                for w in words_raw:
                    words.append({
                        "id": w[0],
                        "location": w[1],
                        "surah": w[2],
                        "ayah": w[3],
                        "word": w[4],
                        "text": w[5]
                    })
            
            lines_data.append({
                "page_number": page_num,
                "line_number": line_num,
                "line_type": l_type,
                "is_centered": bool(centered),
                "surah_number": surah_num,
                "words": words
            })
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return lines_data

def get_mushaf_page_data_structured(page_number: int):
    """
    Retrieves the structured page data for the 15-line Mushaf layout, 
    with concatenated words for ayah lines.
    """
    conn_15line = sqlite3.connect(DB_15_LINES)
    conn_wbw = sqlite3.connect(DB_WBW)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        for line in lines:
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # Global Suppression: Surah 1 (Basmallah is Ayah 1) and Surah 9 (No Basmallah)
            if l_type == 'basmallah' and surah_num in [1, 9]:
                continue

            concatenated_text = ""
            if l_type == 'ayah' and start_id is not None and end_id is not None:
                cursor_wbw.execute("""
                    SELECT text
                    FROM words
                    WHERE id BETWEEN ? AND ?
                    ORDER BY id
                """, (start_id, end_id))
                
                words_raw = cursor_wbw.fetchall()
                concatenated_text = " ".join([w[0] for w in words_raw])
            
            lines_data.append({
                "page_number": page_num,
                "line_number": line_num,
                "line_type": l_type,
                "is_centered": bool(centered),
                "surah_number": surah_num,
                "text": concatenated_text
            })
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return lines_data

def align_mushaf_lines_with_timestamps(page_data: list, wbw_timestamps: dict):
    """
    Calculates start and end timestamps for each Mushaf line based on word-level timing.
    Uses min start and max end of all timestamped words in the line to handle missing segments.
    """
    for line in page_data:
        words = line.get("words", [])
        if not words:
            line["start_ms"] = None
            line["end_ms"] = None
            continue
            
        valid_starts = []
        valid_ends = []
        
        for w in words:
            segments = wbw_timestamps.get(w["ayah"], [])
            for seg in segments:
                if seg[0] == w["word"]:
                    valid_starts.append(seg[1])
                    valid_ends.append(seg[2])
                    break
        
        if valid_starts:
            line["start_ms"] = min(valid_starts)
        else:
            line["start_ms"] = None
            
        if valid_ends:
            line["end_ms"] = max(valid_ends)
        else:
            line["end_ms"] = None
        
    return page_data

