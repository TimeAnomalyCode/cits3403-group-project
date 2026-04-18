import sqlalchemy as sa
<<<<<<< HEAD
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    make_response,
    send_from_directory,
)
=======
import random
from game2048 import app, db, mail, socketio
from game2048.forms import RegistrationForm, LoginForm
from game2048.models import User
from flask import render_template, flash, redirect, jsonify, url_for, request, make_response, send_from_directory, session
from flask_mail import Message
>>>>>>> 2a4a27d (Implement tournament system: added create tournament page, lobby with player tracking, and initial bracket UI. Integrated Flask routes with session-based tournament state and frontend JS for dynamic updates.)
from flask_login import current_user, login_user, logout_user, login_required
from game2048 import app, db, socketio
from game2048.forms import (
    RegistrationForm,
    LoginForm,
    ChangeUsername,
    ChangePassword,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from game2048.models import User
from game2048.email import send_password_reset_email

# ----------------------------------------------------------------
# Our home is also the login page
# No @login_required
# ----------------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():

    # we need to check if user has logged in already to render a logged in homepage
    if current_user.is_authenticated:
        return render_template("home_loggedIn.html", title="Home")

    leaderboard = [
        {"rank": 1, "username": "Jack", "high_score": 1200, "num_of_wins": 10},
        {"rank": 2, "username": "Sarah", "high_score": 900, "num_of_wins": 6},
        {"rank": 3, "username": "John", "high_score": 300, "num_of_wins": 2},
    ]
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("home"))

        login_user(user, remember=form.remember_me.data)
        return render_template("home_loggedIn.html", title="Home")

    return render_template(
        "home.html", title="Home", leaderboard=leaderboard, form=form
    )


<<<<<<< HEAD
@app.route("/register", methods=["GET", "POST"])
=======
@app.route('/profile')
@login_required
def profile():
    return render_template('profile_page.html', user= current_user)


@app.route("/game")
@login_required
def game():
    return render_template("2048_mutil_player_game_board.html")

@app.route("/tournament-bracket")
#@login_required
def tournament_bracket():
    return render_template("tournament_bracket.html")


@app.route("/tournament-lobby")
#@login_required
def tournament_lobby():
    return render_template("PrivateTournamentLobby.html")

@app.route("/register", methods=['GET', 'POST'])
>>>>>>> 2a4a27d (Implement tournament system: added create tournament page, lobby with player tracking, and initial bracket UI. Integrated Flask routes with session-based tournament state and frontend JS for dynamic updates.)
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            image_file=f"https://api.dicebear.com/9.x/croodles/svg?seed={form.username.data}&flip=true&backgroundColor=FFFFFF",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # One time display of status
        flash("You have created an account! Please Log In", "success")
        return redirect(url_for("home"))

    return render_template("register.html", title="Register", form=form)


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user:
            send_password_reset_email(user)

        # We flash the message regardless if the user exists or not so that hackers can't probe if user exists or not
        flash("Check your email for the instructions to reset your password", "success")
        return redirect(url_for("home"))

    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for("home"))

    form = ResetPasswordForm(user)

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset", "success")
        return redirect(url_for("home"))

    return render_template(
        "reset_password.html", title="Reset Password Form", form=form
    )


# ----------------------------------------------------------------
# Anything below should have @login_required
# ----------------------------------------------------------------


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    num_of_wins = 2
    rank = 100
    match_history = [
        {"date": "2026-04-10", "opponent": "Sarah", "result": "Win", "score": 2048},
        {"date": "2026-04-09", "opponent": "Jason", "result": "Loss", "score": 1024},
        {"date": "2026-04-08", "opponent": "Alex", "result": "Win", "score": 2048},
    ]
    return render_template(
        "profile.html",
        title="Profile",
        user=user,
        num_of_wins=num_of_wins,
        rank=rank,
        match_history=match_history,
    )


@app.route("/change_username", methods=["GET", "POST"])
@login_required
def change_username():
    form = ChangeUsername(current_user.username)

    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Incorrect Password", "danger")
            return redirect(url_for("change_username"))

        current_user.username = form.new_username.data
        db.session.commit()
        flash("Your username has been updated!", "success")

        return redirect(url_for("profile", username=current_user.username))

    return render_template("change_username.html", title="Change Username", form=form)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePassword()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Incorrect Password", "danger")
            return redirect(url_for("change_password"))

        current_user.set_password(form.new_password.data)
        db.session.commit()

        logout_user()
        flash("Your Password has been updated! Please login", "success")
        return redirect(url_for("home"))

    return render_template("change_password.html", title="Change Password", form=form)


# ----------------------------------------------------------------
# Anything Below is just helper functions or testing
# (Should be removed or made official)
# ----------------------------------------------------------------


# Cache static files on client
# Source: https://stackoverflow.com/questions/77569410/flask-possible-to-cache-images
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
<<<<<<< HEAD
@app.route("/static/<path:filename>")
def static(filename):
    resp = make_response(send_from_directory("static/", filename))
    resp.headers["Cache-Control"] = "max-age=604800"
    return resp
=======


#@app.route('/static/<path:filename>')
#def static(filename):
#    resp = make_response(send_from_directory('static/', filename))
#    resp.headers['Cache-Control'] = 'max-age=604800'
#    return resp
>>>>>>> 2a4a27d (Implement tournament system: added create tournament page, lobby with player tracking, and initial bracket UI. Integrated Flask routes with session-based tournament state and frontend JS for dynamic updates.)


# Just to test login required
# @app.route("/send")
# def index():
#     msg = Message(
#         subject="2048 Battle!", sender="test@gmail.com", recipients=["nerd@gmail.com"]
#     )
#     msg.body = request.args.get("message")
#     mail.send(msg)
#     return f"<p>Message sent!</p> {msg}"


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

<<<<<<< HEAD
    return "".join(data)
=======
    return ''.join(data)

tournaments = {}

@app.route("/create-tournament")
def create_tournament_page():
    return render_template("CreateTournament.html")


@app.route("/api/create-tournament", methods=["POST"])
#@login_required
def api_create_tournament():
    data = request.json

    name = data.get("name")
    players = data.get("players")
    privacy = data.get("privacy")

    if not name or not players or not privacy:
        return jsonify({"error": "Missing tournament details"}), 400

    try:
        players = int(players)
    except ValueError:
        return jsonify({"error": "Invalid player count"}), 400

    if players not in [4, 8, 16]:
        return jsonify({"error": "Player count must be 4, 8, or 16"}), 400

    join_code = str(random.randint(10000, 99999))
    while join_code in tournaments:
        join_code = str(random.randint(10000, 99999))

    tournaments[join_code] = {
        "name": name,
        "max": players,
        "privacy": privacy,
        "players": [current_user.username]
    }

    session["tournament_code"] = join_code

    return jsonify({
        "success": True,
        "joinCode": join_code,
        "name": name
    })

@app.route("/api/join-tournament", methods=["POST"])
#@login_required
def api_join_tournament():
    data = request.json
    code = data.get("joinCode")

    if code not in tournaments:
        return jsonify({"error": "Invalid code"}), 400

    t = tournaments[code]
    user = current_user.username

    if user not in t["players"] and len(t["players"]) < t["max"]:
        t["players"].append(user)

    session["tournament_code"] = code

    return jsonify({"success": True})

@app.route("/api/lobby-state")
@login_required
def lobby_state():
    code = session.get("tournament_code")

    if not code or code not in tournaments:
        return {"error": "No tournament"}

    t = tournaments[code]

    return {
        "name": t["name"],
        "players": t["players"],
        "code": code,
        "max": t["max"]
    }
>>>>>>> 2a4a27d (Implement tournament system: added create tournament page, lobby with player tracking, and initial bracket UI. Integrated Flask routes with session-based tournament state and frontend JS for dynamic updates.)
