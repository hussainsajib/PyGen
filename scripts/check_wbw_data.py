import sqlite3
import os

def check_db(db_path, surah, ayah, table, surah_col, ayah_col):
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {surah_col} = ? AND {ayah_col} = ?", (surah, ayah))
    count = cursor.fetchone()[0]
    print(f"Count in {db_path} for {surah}:{ayah}: {count}")
    conn.close()

check_db("databases/text/qpc-hafs-word-by-word.db", 1, 1, "words", "surah", "ayah")
check_db("databases/translation/bengali/bangali-word-by-word-translation.sqlite", 1, 1, "word_translation", "surah_number", "ayah_number")
