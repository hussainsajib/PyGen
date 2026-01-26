import sqlite3
import os

def get_page_content(page_number, db_15line_path, db_wbw_path):
    """
    Groups words from WBW DB based on line definitions in 15-Line DB for a given page.
    """
    conn_15line = sqlite3.connect(db_15line_path)
    conn_wbw = sqlite3.connect(db_wbw_path)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch all lines for the given page
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        for line in lines:
            # line structure: (page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number)
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # 2. Fetch words for this line range
            cursor_wbw.execute("""
                SELECT id, location, surah, ayah, word, text
                FROM words
                WHERE id BETWEEN ? AND ?
                ORDER BY id
            """, (start_id, end_id))
            
            words_raw = cursor_wbw.fetchall()
            
            words = []
            for w in words_raw:
                # w structure: (id, location, surah, ayah, word, text)
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

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python mushaf_mapper.py <page_number>")
        sys.exit(1)
        
    page_num = int(sys.argv[1])
    db_15 = "databases/text/qpc-v2-15-lines.db"
    db_wbw = "databases/text/word_by_word_qpc-v2.db"
    
    try:
        content = get_page_content(page_num, db_15, db_wbw)
        # For CLI output, just show a summary
        for line in content:
            text = " ".join([w['text'] for w in line['words']])
            print(f"Page {line['page_number']} Line {line['line_number']} [{line['line_type']}]: {text}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
