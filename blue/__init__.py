from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models.tables import db, bcrypt
from blue.config import Config


# Inicializar o aplicativo Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar as extensões
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)

# Configurar a página de login
login_manager.login_view = 'login'

from .controllers import default