from game2048 import app, mail
from flask import request
from flask_mail import Message

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