from flask import render_template, flash, redirect, url_for, request, make_response, send_from_directory
from flask_mail import Message
from game2048 import app, db, mail, socketio
from game2048.forms import RegistrationForm, LoginForm

# Our home is also the login page
@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
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

# Cache static files on client for 1 month
# Source: https://stackoverflow.com/questions/77569410/flask-possible-to-cache-images
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
@app.route('/static/<path:filename>')
def static(filename):
    resp = make_response(send_from_directory('static/', filename))
    resp.headers['Cache-Control'] = 'max-age=604800'
    return resp