import os
from dotenv import load_dotenv

# For future testing to load other .env files
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

# Because .env does not support booleans, only strings
def str_to_bool(text):
    return text.lower() == "true"


class Config:
    # flask_sqlalchemy, flask_wtf, flask_socketio
    SECRET_KEY = os.getenv('SECRET_KEY')

    # flask_sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    # flask_mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = str_to_bool(os.getenv('MAIL_USE_TLS'))
    MAIL_USE_SSL = str_to_bool(os.getenv('MAIL_USE_SSL'))
    MAIL_DEFAULT_SENDER = (os.getenv('MAIL_DEFAULT_SENDER_NAME'), os.getenv('MAIL_DEFAULT_SENDER_ADDRESS'))