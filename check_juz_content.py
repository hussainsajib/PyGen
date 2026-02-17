import sqlite3
import os
import json

def check_content():
    db_path = 'databases/text/quran-metadata-juz.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM juz WHERE juz_number = 30")
    row = cursor.fetchone()
    if row:
        print("Juz 30 row found.")
        print(f"Columns: {row}")
        # Assuming verse_mapping is the last column
        try:
            mapping = json.loads(row[4])
            print("Successfully parsed verse_mapping JSON.")
        except:
            print("Failed to parse verse_mapping as JSON.")
    else:
        print("Juz 30 not found!")
    conn.close()

if __name__ == "__main__":
    check_content()
