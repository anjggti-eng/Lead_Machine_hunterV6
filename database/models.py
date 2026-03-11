from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(50))
    email = db.Column(db.String(100), default="N/A")
    endereco = db.Column(db.Text) # Mantendo nosso capturador de endereços
    cnpj = db.Column(db.String(20))  # campo extra para registrar CNPJ quando disponível
    cidade = db.Column(db.String(100))
    score = db.Column(db.Integer, default=50) # Novo campo para IA pontuar
    status = db.Column(db.String(50), default="novo") # Novo campo de status
    lat = db.Column(db.Float) # Latitude para o mapa
    lon = db.Column(db.Float) # Longitude para o mapa
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
