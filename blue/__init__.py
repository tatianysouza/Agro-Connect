from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect


# Inicializar o aplicativo Flask
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
bcrypt = Bcrypt()


# Inicializar as extensões
login_manager = LoginManager(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
# Configurar a página de login
login_manager.login_view = 'login'

from .controllers import default