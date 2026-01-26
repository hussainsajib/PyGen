import sqlite3
import os

DB_15_LINES = "databases/text/qpc-v2-15-lines.db"
DB_WBW = "databases/text/word_by_word_qpc-v2.db"

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
