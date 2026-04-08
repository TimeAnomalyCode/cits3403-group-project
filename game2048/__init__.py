from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Because .env does not support booleans, only strings
def str_to_bool(text):
    return text.lower() == "true"

# flask_sqlalchemy, flask_wtf, flask_socketio
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# flask_sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

# flask_mail
app.config['MAIL_SERVER']= os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = str_to_bool(os.getenv('MAIL_USE_TLS'))
app.config['MAIL_USE_SSL'] = str_to_bool(os.getenv('MAIL_USE_SSL'))

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)

from game2048 import routes