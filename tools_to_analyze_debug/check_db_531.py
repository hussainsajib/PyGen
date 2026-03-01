import sqlite3
import os

DB_15_LINES = "databases/text/qpc-v2-15-lines.db"

def check_db():
    conn = sqlite3.connect(DB_15_LINES)
    cursor = conn.cursor()
    cursor.execute("SELECT line_number, line_type, surah_number FROM pages WHERE page_number = 531")
    rows = cursor.fetchall()
    for r in rows:
        print(f"Line {r[0]}: Type={r[1]}, Surah={r[2]}")
    conn.close()

if __name__ == "__main__":
    check_db()
