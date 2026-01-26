import sqlite3

DB_PATH = "databases/text/qpc-v2-15-lines.db"

def check_surah_name_lines():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT page_number, line_number, first_word_id, last_word_id, surah_number 
        FROM pages 
        WHERE line_type = 'surah_name' 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print("Surah Name Lines:", rows)
    conn.close()

if __name__ == "__main__":
    check_surah_name_lines()
