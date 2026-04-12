import sqlalchemy as sa
from game2048 import app, db, mail, socketio
from game2048.forms import RegistrationForm, LoginForm, ChangeUsername, ChangePassword
from game2048.models import User
from flask import render_template, flash, redirect, url_for, request, make_response, send_from_directory
from flask_mail import Message
from flask_login import current_user, login_user, logout_user, login_required

# ----------------------------------------------------------------
# Our home is also the login page
# No @login_required
# ----------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():

    # we need to check if user has logged in already to render a logged in homepage
    if current_user.is_authenticated:
        return render_template('home_loggedIn.html', title='Home')
    
    leaderboard = [
        {'rank': 1, 'username': 'Jack', 'high_score': 1200, 'num_of_wins': 10},
        {'rank': 2, 'username': 'Sarah', 'high_score': 900, 'num_of_wins': 6},
        {'rank': 3, 'username': 'John', 'high_score': 300, 'num_of_wins': 2},
    ]
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('home'))
        
        login_user(user, remember=form.remember_me.data)
        return render_template('home_loggedIn.html', title='Home')

    return render_template('home.html', title='Home', leaderboard=leaderboard, form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            image_file=f'https://api.dicebear.com/9.x/croodles/svg?seed={form.username.data}&flip=true&backgroundColor=FFFFFF'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # One time display of status
        flash(f'You have created an account! Please Log In', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html', title='Register', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ----------------------------------------------------------------
# Anything below should have @login_required
# ----------------------------------------------------------------

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    num_of_wins = 2
    rank = 100
    match_history = [
        {'date': '2026-04-10', 'opponent': 'Sarah', 'result': 'Win', 'score': 2048},
        {'date': '2026-04-09', 'opponent': 'Jason', 'result': 'Loss', 'score': 1024},
        {'date': '2026-04-08', 'opponent': 'Alex', 'result': 'Win', 'score': 2048},
    ]
    return render_template('profile.html', title='Profile', user=user, num_of_wins=num_of_wins, rank=rank, match_history=match_history)

@app.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsername(current_user.username)

    if form.validate_on_submit():

        if not current_user.check_password(form.password.data):
            flash('Incorrect Password', 'danger')
            return redirect(url_for('change_username'))

        current_user.username = form.new_username.data
        db.session.commit()
        flash('Your username has been updated!', 'success')

        return redirect(url_for('profile', username=current_user.username))
        
    return render_template('change_username.html', title='Change Username', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Incorrect Password', 'danger')
            return redirect(url_for('change_password'))
    
        current_user.set_password(form.new_password.data)
        db.session.commit()

        logout_user()
        flash('Your Password has been updated! Please login', 'success')
        return redirect(url_for('home'))

    return render_template('change_password.html', title='Change Password', form=form)

# ----------------------------------------------------------------
# Anything Below is just helper functions or testing 
# (Should be removed or made official)
# ----------------------------------------------------------------

# Cache static files on client
# Source: https://stackoverflow.com/questions/77569410/flask-possible-to-cache-images
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
@app.route('/static/<path:filename>')
def static(filename):
    resp = make_response(send_from_directory('static/', filename))
    resp.headers['Cache-Control'] = 'max-age=604800'
    return resp

# Just to test login required
@app.route("/send")
def index():
    msg = Message(subject='2048 Battle!', sender='test@gmail.com', recipients=['nerd@gmail.com'])
    msg.body = request.args.get('message')
    mail.send(msg)
    return f"<p>Message sent!</p> {msg}"

# Helper to refresh/create and display db
# The reason One to One is not present: https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html#one-to-one
@app.route("/create")
def about():
    db.drop_all()
    db.create_all()

    data = []

    # V1
    # for key, obj in db.metadata.tables.items():
    #     data.append(f'<h1>{key}</h1>')
    #     for col in obj.columns:
    #         data.append(f'<p>{col.name} {col.type}</p>')
    #     data.append('<hr>')

    for mapper in db.Model.registry.mappers:
        cls = mapper.class_
        table = mapper.local_table

        data.append(f"<h1>{table.name}</h1>")

        # Columns
        for col in table.columns:
            data.append(f"<p><b>{col.name}</b> ({col.type})</p>")

        # Relationships
        data.append("<h3>Relationships</h3>")
        for rel in mapper.relationships:
            target = rel.mapper.class_.__name__
            direction = rel.direction.name  # MANYTOONE, ONETOMANY, MANYTOMANY

            data.append(
                f"<p>{rel.key} → {target} "
                f"({direction}) "
                f"back_populates={rel.back_populates}</p>"
            )

        data.append("<hr>")

    return ''.join(data)