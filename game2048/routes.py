from flask import render_template, flash, redirect, url_for, request
from flask_mail import Message
from game2048 import app, db, mail, socketio
from game2048.forms import RegistrationForm, LoginForm

# Our home is also the login page
@app.route("/")
@app.route("/home")
def home():
    # we need to check if user has logged in already to render a logged in homepage
    form = LoginForm()
    return render_template('home.html', title='Home', form=form)

@app.route("/about")
def about():
    return "About Page"

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # One time display of status
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/send")
def index():
    msg = Message(subject='2048 Battle!', sender='test@gmail.com', recipients=['nerd@gmail.com'])
    msg.body = request.args.get('message')
    mail.send(msg)
    return f"<p>Message sent!</p> {msg}"