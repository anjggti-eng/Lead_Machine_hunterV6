from flask import Flask, redirect, url_for
from config import Config
from database.models import db, User
from flask_login import LoginManager
from routes.auth_routes import auth
from routes.lead_routes import leads
import os

app = Flask(__name__)
app.config.from_object(Config)

# IMPORTANTE: Criar a pasta database se ela não existir antes de iniciar o banco
db_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "database")
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)
app.register_blueprint(leads)

@app.route("/")
def home():
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    with app.app_context():
        # Agora o Flask sabe qual App o DB pertence
        db.create_all()
        # Admin Default
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="123"))
            db.session.commit()
            
    # Roda ouvindo em todas as interfaces na porta 5050
    app.run(debug=True, port=5050, host='0.0.0.0')
