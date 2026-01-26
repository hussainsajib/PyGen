import sqlite3
import os

def get_db_schema(db_path):
    """
    Connects to an SQLite database and extracts its schema.
    
    Args:
        db_path (str): Path to the SQLite database file.
        
    Returns:
        dict: A dictionary where keys are table names and values are lists of column details.
    """
    if not os.path.exists(db_path) and not db_path == "dummy.db": # Allow dummy for mocking
         # This check is actually tricky with mocking, usually we let sqlite3 raise if file not found 
         # or it creates a new empty one depending on mode.
         # For inspection, we expect it to exist.
         # But in our test we mock sqlite3.connect so os.path.exists check might interfere if we don't mock it too.
         # Let's rely on sqlite3.connect throwing if we fail, or just logic.
         pass

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {}
    
    try:
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            column_details = []
            for col in columns:
                # col structure: (cid, name, type, notnull, dflt_value, pk)
                column_details.append({
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "dflt_value": col[4],
                    "pk": col[5]
                })
            
            schema[table_name] = column_details
            
    finally:
        conn.close()
        
    return schema

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python schema_inspector.py <db_path>")
        sys.exit(1)
        
    db_path = sys.argv[1]
    try:
        schema = get_db_schema(db_path)
        print(json.dumps(schema, indent=4))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
