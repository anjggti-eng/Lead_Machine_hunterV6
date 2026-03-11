import os

# Pega o caminho da pasta onde este arquivo config.py está
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "platinum_key_777"
    # Caminho absoluto para evitar erro de "unable to open database file"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'leads.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEOAPIFY_API_KEY = "004191afd7974679a48d5442fb1b1924"
    GOOGLE_MAPS_API_KEY = "004191afd7974679a48d5442fb1b1924"
