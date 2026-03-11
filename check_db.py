import sqlite3
import os

db_path = 'database/leads.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(lead)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {columns}")
    
    # Check if lat exists, if not, add it
    if 'lat' not in columns:
        print("Adding lat column...")
        cursor.execute("ALTER TABLE lead ADD COLUMN lat FLOAT")
    if 'lon' not in columns:
        print("Adding lon column...")
        cursor.execute("ALTER TABLE lead ADD COLUMN lon FLOAT")
    
    conn.commit()
    conn.close()
else:
    print("Database not found.")
