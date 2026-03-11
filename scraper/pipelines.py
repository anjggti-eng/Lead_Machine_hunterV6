import sqlite3
import os

class LeadPipeline:
    def open_spider(self, spider):
        # Caminho para o banco de dados do Flask
        db_path = os.path.join(os.getcwd(), 'database', 'leads.db')
        self.conn = sqlite3.connect(db_path)
        self.curr = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.curr.execute("""
            INSERT INTO lead (empresa, telefone, endereco, cidade, score, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            item['empresa'],
            item['telefone'],
            item.get('endereco', 'N/A'),
            item.get('cidade', spider.location if hasattr(spider, 'location') else 'N/A'),
            85, # Score fixo inicial
            'novo'
        ))
        self.conn.commit()
        return item
