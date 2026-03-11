"""Migration script to add cnpj column to lead table if it doesn't exist.
Compatible with SQLAlchemy 2.x.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "leads.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(lead)")
    columns = {row[1] for row in cur.fetchall()}

    if 'cnpj' not in columns:
        print("Adicionando coluna 'cnpj' à tabela 'lead'...")
        try:
            cur.execute("ALTER TABLE lead ADD COLUMN cnpj VARCHAR(20)")
            conn.commit()
            print("✓ Coluna 'cnpj' adicionada com sucesso!")
        except Exception as e:
            print(f"✗ Erro ao adicionar coluna: {e}")
            conn.close()
            return 1
    else:
        print("✓ Coluna 'cnpj' já existe na tabela 'lead'.")

    conn.close()
    return 0

if __name__ == "__main__":
    exit_code = migrate()
    exit(exit_code)
