import sqlite3

def inspect_db(db_path):
    print(f"Inspecting {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        print(f"Schema for {table_name}: {cursor.fetchall()}")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        print(f"Sample data for {table_name}: {cursor.fetchall()}")
    conn.close()
    print("-" * 20)

inspect_db("databases/text/qpc-hafs-word-by-word.db")
    print("\n--- Bengali WBW Translation DB ---")
    inspect_db("databases/translation/bengali/bangali-word-by-word-translation.sqlite")
