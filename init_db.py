from app import app
from database.models import db, User

def initialize():
    # Cria o contexto do App para o SQLAlchemy saber qual banco usar
    with app.app_context():
        db.create_all()
        # garantia de que coluna 'cnpj' existe (SQLite não cria automaticamente em alter schema)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('lead')]
        if 'cnpj' not in cols:
            try:
                db.engine.execute('ALTER TABLE lead ADD COLUMN cnpj VARCHAR(20)')
                print('Coluna cnpj adicionada à tabela lead.')
            except Exception as exc:
                print('Falha ao adicionar coluna cnpj:', exc)

        # Admin Default
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="123"))
            db.session.commit()
            print("Sucesso! Banco criado e Admin 'admin/123' configurado.")
        else:
            print("O banco de dados já está pronto.")

if __name__ == "__main__":
    initialize()
