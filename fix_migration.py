"""
Migrates database/leads.db to match the current Lead SQLAlchemy model.

Old column names -> New column names:
  name      -> empresa
  whatsapp  -> telefone
  city      -> cidade
  timestamp -> created_at
  address   -> endereco

New columns added (with defaults):
  cnpj   -> NULL
  score  -> 50
  status -> 'novo'
  lat    -> NULL
  lon    -> NULL
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "leads.db")

print(f"Target DB: {DB_PATH}")
if not os.path.exists(DB_PATH):
    print("ERROR: File not found!")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Show current state
cur.execute("PRAGMA table_info(lead)")
rows = cur.fetchall()
existing_cols = {row[1] for row in rows}
print(f"\nExisting columns: {existing_cols}")

cur.execute("SELECT COUNT(*) FROM lead")
count = cur.fetchone()[0]
print(f"Rows to migrate: {count}")

# Map old -> new
empresa_src  = 'name'      if 'name'      in existing_cols else ('empresa'    if 'empresa'    in existing_cols else None)
telefone_src = 'whatsapp'  if 'whatsapp'  in existing_cols else ('telefone'   if 'telefone'   in existing_cols else 'NULL')
cidade_src   = 'city'      if 'city'      in existing_cols else ('cidade'     if 'cidade'     in existing_cols else 'NULL')
created_src  = 'timestamp' if 'timestamp' in existing_cols else ('created_at' if 'created_at' in existing_cols else 'NULL')
endereco_src = 'address'   if 'address'   in existing_cols else ('endereco'   if 'endereco'   in existing_cols else 'NULL')
cnpj_src     = 'cnpj'      if 'cnpj'      in existing_cols else 'NULL'
score_src    = 'score'     if 'score'     in existing_cols else '50'
status_src   = 'status'    if 'status'    in existing_cols else "'novo'"
lat_src      = 'lat'       if 'lat'       in existing_cols else 'NULL'
lon_src      = 'lon'       if 'lon'       in existing_cols else 'NULL'
email_src    = 'email'     if 'email'     in existing_cols else "'N/A'"

if empresa_src is None:
    print("ERROR: Cannot find 'name' or 'empresa' column - cannot migrate!")
    conn.close()
    exit(1)

print(f"\nColumn mapping:")
print(f"  empresa  <- {empresa_src}")
print(f"  telefone <- {telefone_src}")
print(f"  cidade   <- {cidade_src}")
print(f"  created  <- {created_src}")
print(f"  endereco <- {endereco_src}")

# Create new table
print("\nCreating 'lead_new' with correct schema...")
cur.execute("DROP TABLE IF EXISTS lead_new")
cur.execute("""
    CREATE TABLE lead_new (
        id         INTEGER PRIMARY KEY,
        empresa    VARCHAR(200) NOT NULL,
        telefone   VARCHAR(50),
        email      VARCHAR(100) DEFAULT 'N/A',
        endereco   TEXT,
        cnpj       VARCHAR(20),
        cidade     VARCHAR(100),
        score      INTEGER DEFAULT 50,
        status     VARCHAR(50) DEFAULT 'novo',
        lat        REAL,
        lon        REAL,
        created_at DATETIME
    )
""")

# Migrate data
sql = f"""
    INSERT INTO lead_new
        (id, empresa, telefone, email, endereco, cnpj, cidade, score, status, lat, lon, created_at)
    SELECT
        id,
        {empresa_src},
        {telefone_src},
        {email_src},
        {endereco_src},
        {cnpj_src},
        {cidade_src},
        {score_src},
        {status_src},
        {lat_src},
        {lon_src},
        {created_src}
    FROM lead
"""
print(f"\nMigrating data...")
cur.execute(sql)
migrated = cur.rowcount
print(f"Migrated {migrated} rows.")

# Swap
print("Swapping tables...")
cur.execute("DROP TABLE lead")
cur.execute("ALTER TABLE lead_new RENAME TO lead")
conn.commit()

# Verify
cur.execute("PRAGMA table_info(lead)")
final_cols = [r[1] for r in cur.fetchall()]
cur.execute("SELECT COUNT(*) FROM lead")
final_count = cur.fetchone()[0]

print(f"\n=== DONE ===")
print(f"Final columns: {final_cols}")
print(f"Final row count: {final_count}")
conn.close()
print("\nRestart Flask - the error should be gone!")
