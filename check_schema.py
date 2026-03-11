"""
Shows existing lead data and current schema.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "database.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(lead)")
cols = cur.fetchall()
print("=== Current lead schema ===")
for c in cols:
    print(f"  {c[1]} ({c[2]})")

cur.execute("SELECT COUNT(*) FROM lead")
count = cur.fetchone()[0]
print(f"\n=== Row count: {count} ===")

if count > 0:
    cur.execute("SELECT * FROM lead LIMIT 5")
    rows = cur.fetchall()
    print("Sample rows:")
    col_names = [c[1] for c in cols]
    for row in rows:
        print(dict(zip(col_names, row)))

conn.close()
