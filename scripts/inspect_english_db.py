import sqlite3
import sys

def inspect_english_db():
    db_path = "databases/translation/english/word-by-word-translation.sqlite"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(word_translation)")
        print("Schema:", cursor.fetchall())
        
        # Fetch rows with non-ascii characters (python check)
        cursor.execute("SELECT * FROM word_translation")
        print("\nChecking for non-ASCII characters...")
        count = 0
        for row in cursor:
            # Assuming text is the last column based on previous output
            text_val = row[-1] 
            if any(ord(c) > 127 for c in text_val):
                print(f"Found non-ASCII: {row}")
                print(f"Repr: {repr(text_val)}")
                count += 1
                if count >= 5: break
        
        if count == 0:
            print("No non-ASCII characters found in the first scan (might be clean ASCII DB).")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    inspect_english_db()
