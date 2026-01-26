import sqlite3

DB_PATH = "databases/text/qpc-v2-15-lines.db"

def check_line_types():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT line_type FROM pages")
    types = cursor.fetchall()
    print("Line Types:", types)
    conn.close()

if __name__ == "__main__":
    check_line_types()
