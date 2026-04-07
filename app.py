from flask import Flask, request
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER']= os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Because .env does not support booleans, only strings
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == "true"
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == "true"

mail = Mail(app)

@app.route("/")
@app.route("/home")
def home():
    return "Home Page"

@app.route("/about")
def about():
    return "About Page"

@app.route("/send")
def index():
    msg = Message(subject='2048 Battle!', sender='test@gmail.com', recipients=['nerd@gmail.com'])
    msg.body = request.args.get('message')
    mail.send(msg)
    return f"<p>Message sent!</p> {msg}"

# Use Ctrl + Shift + R to hard refresh browser
if __name__ == "__main__":
    app.run(debug=True)
