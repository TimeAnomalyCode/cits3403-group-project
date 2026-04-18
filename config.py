import os
from dotenv import load_dotenv

# For future testing to load other .env files
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# Because .env does not support booleans, only strings
def str_to_bool(text):
    if text is None:
        return False
    return text.lower() == "true"


class Config:
    # flask_sqlalchemy, flask_wtf, flask_socketio
<<<<<<< HEAD
    SECRET_KEY = os.getenv("SECRET_KEY")

    # flask_sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    # flask_mail
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = str_to_bool(os.getenv("MAIL_USE_TLS"))
    MAIL_USE_SSL = str_to_bool(os.getenv("MAIL_USE_SSL"))
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME"),
        os.getenv("MAIL_DEFAULT_SENDER_ADDRESS"),
    )
=======
    SECRET_KEY = os.getenv('SECRET_KEY', "dev-secret-key")

    # flask_sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask_mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = str_to_bool(os.getenv('MAIL_USE_TLS'))
    MAIL_USE_SSL = str_to_bool(os.getenv('MAIL_USE_SSL'))
>>>>>>> 2a4a27d (Implement tournament system: added create tournament page, lobby with player tracking, and initial bracket UI. Integrated Flask routes with session-based tournament state and frontend JS for dynamic updates.)
