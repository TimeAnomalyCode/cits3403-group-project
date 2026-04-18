from flask import Flask
import os
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import Config

# Required for caching (static_folder)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
print("TEMPLATE FOLDER =", app.template_folder)
print("TEMPLATE EXISTS =", os.path.exists(app.template_folder))
print("TEMPLATE FILES =", os.listdir(app.template_folder) if os.path.exists(app.template_folder) else "missing")
app.config.from_object(Config)

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
mail = Mail(app)
socketio = SocketIO(app)

login_manager.login_view = "home"
login_manager.login_message_category = "info"

from game2048 import routes, models, errors  # noqa
