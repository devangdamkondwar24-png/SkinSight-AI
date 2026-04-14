import sqlite3
import json
import os
from contextlib import contextmanager

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "skinsight.db")

def init_db():
    print(f"[DB] Initializing SQLite Database at {DB_FILE}")
    with get_db() as conn:
        cursor = conn.cursor()
        
        # User Profile Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            name TEXT,
            gender TEXT,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Concerns Table (linked 1:1 to users for simplicity here)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS concerns (
            phone TEXT PRIMARY KEY,
            primary_concern TEXT,
            secondary_concerns TEXT, -- Stored as JSON string
            FOREIGN KEY (phone) REFERENCES users (phone)
        )
        ''')
        
        # Analysis Reports Table (1:N linking to users)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            result_json TEXT, -- Stored as JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phone) REFERENCES users (phone)
        )
        ''')
        
        conn.commit()
    print("[DB] Tables successfully created/verified.")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    # Enable fetching rows as dicts
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize upon import
init_db()
