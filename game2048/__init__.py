from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
socketio = SocketIO()
login_manager = LoginManager()

login_manager.login_view = "home"
login_manager.login_message_category = "info"


# making a function for better application creation for both production and testing environment
def create_app(config_class=Config):
    app = Flask(__name__, static_folder=None)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    socketio.server.instrument(auth=False)

    from game2048.routes import main
    from game2048.errors import error

    app.register_blueprint(main)
    app.register_blueprint(error)

    return app
