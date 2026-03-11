import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
if not os.path.exists(db_path):
    # Tenta no root se não estiver na pasta instance
    db_path = 'database.db'

print(f"Tentando corrigir o banco em: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Adiciona a coluna address na tabela lead
    cursor.execute("ALTER TABLE lead ADD COLUMN address TEXT")
    
    conn.commit()
    conn.close()
    print("Sucesso! Coluna 'address' adicionada com sucesso.")
except sqlite3.OperationalError:
    print("Aviso: A coluna 'address' já parece existir ou a tabela não foi encontrada.")
except Exception as e:
    print(f"Erro ao corrigir: {e}")
