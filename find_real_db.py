import sqlite3
import os

BASE = r'C:\Users\User\.gemini\antigravity\scratch\lead_machine'

candidates = [
    os.path.join(BASE, 'database', 'leads.db'),
    os.path.join(BASE, 'instance', 'database.db'),
    os.path.join(BASE, 'instance', 'leads.db'),
    os.path.join(BASE, 'leads.db'),
]

for path in candidates:
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        try:
            cur.execute("PRAGMA table_info(lead)")
            cols = [r[1] for r in cur.fetchall()]
            cur.execute("SELECT COUNT(*) FROM lead")
            count = cur.fetchone()[0]
            print(f"FOUND: {path}")
            print(f"  Rows : {count}")
            print(f"  Cols : {cols}")
        except Exception as e:
            print(f"FOUND (error reading): {path} -> {e}")
        conn.close()
    else:
        print(f"NOT FOUND: {path}")
