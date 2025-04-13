import sqlite3
from fastapi import Depends

MISHARY_DB = "./databases/reciter/Mishari.sqlite"

def get_db():
    conn = sqlite3.connect(MISHARY_DB)
    try:
        yield conn
    finally:
        conn.close()