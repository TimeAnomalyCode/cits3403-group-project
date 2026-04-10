from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import Config

# Required for caching (static_folder)
app = Flask(__name__, static_folder=None)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
socketio = SocketIO(app)

from game2048 import routes, models