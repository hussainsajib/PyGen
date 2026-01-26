import sqlite3

DB_PATH = "databases/text/word_by_word_qpc-v2.db"

def check_words_surah_1():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ayah, COUNT(*) 
        FROM words 
        WHERE surah = 1 
        GROUP BY ayah
    """)
    rows = cursor.fetchall()
    print("Words count per ayah in Surah 1:")
    for r in rows:
        print(f"Ayah {r[0]}: {r[1]}")
    conn.close()

if __name__ == "__main__":
    check_words_surah_1()
