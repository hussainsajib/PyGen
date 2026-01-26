import sqlite3

DB_PATH = "databases/word-by-word/mishari-rashid-al-afasy.sqlite"

def check_timestamps_surah_1():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Assume table name is 'word_timestamps' or similar. Let's list tables first.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        # Usually table is 'word_segments' or 'files'
        if ('segments',) in tables:
            # cursor.execute("PRAGMA table_info(segments)")
            # columns = cursor.fetchall()
            # print("Columns in segments table:", columns)
            
            cursor.execute("SELECT ayah_number, segments FROM segments WHERE surah_number = 1 ORDER BY ayah_number LIMIT 10")
            rows = cursor.fetchall()
            print("Segments for Surah 1:")
            for r in rows:
                print(f"Ayah {r[0]}: {r[1]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_timestamps_surah_1()
