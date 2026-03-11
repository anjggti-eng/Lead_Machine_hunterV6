from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    whatsapp = db.Column(db.String(50))
    address = db.Column(db.Text) # NOVO CAMPO: Endereço completo
    city = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
