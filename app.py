from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
load_dotenv()

# FACTORY DESIGN PATTERN
def create_app():
    app = Flask(__name__, template_folder='application/templates', static_folder='application/static', static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./project_optimus.db'
    app.secret_key = os.getenv("SECRET_KEY")
    csrf = CSRFProtect(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login' 

    from routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)
    
    return app