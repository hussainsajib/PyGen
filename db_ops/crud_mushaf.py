import sqlite3
import os

DB_15_LINES = "databases/text/qpc-v2-15-lines.db"
DB_WBW = "databases/text/word_by_word_qpc-v2.db"

def get_surah_page_range(surah_number: int):
    """
    Returns the start and end page for a given surah.
    """
    conn = sqlite3.connect(DB_15_LINES)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MIN(page_number), MAX(page_number)
            FROM pages
            WHERE surah_number = ?
        """, (surah_number,))
        return cursor.fetchone()
    finally:
        conn.close()

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

