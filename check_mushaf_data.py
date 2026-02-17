import sqlite3
import os

def check_db(db_path):
    print(f"\n--- Checking DB: {db_path} ---")
    if not os.path.exists(db_path):
        print(f"File not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    for table_tuple in tables:
        table_name = table_tuple[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Columns in {table_name}: {[c[1] for c in columns]}")
    
    conn.close()

if __name__ == "__main__":
    check_db('databases/text/word_by_word_qpc-v2.db')
