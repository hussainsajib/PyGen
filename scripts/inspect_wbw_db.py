import sqlite3

db_path = "databases/word-by-word/mishari-rashid-al-afasy.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")

for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    print(f"Schema for {table_name}: {cursor.fetchall()}")

    # Sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    print(f"Sample data for {table_name}: {cursor.fetchall()}")

conn.close()
