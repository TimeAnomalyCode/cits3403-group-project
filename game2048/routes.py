import sqlalchemy as sa
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    make_response,
    send_from_directory,
)
from flask_login import current_user, login_user, logout_user, login_required
from flask_migrate import upgrade
from game2048 import app, db
from game2048.forms import (
    RegistrationForm,
    LoginForm,
    ChangeUsername,
    ChangePassword,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    JoinMatch,
)
from game2048.models import User, Match
from game2048.email import send_password_reset_email
from game2048.board import match_state

# ----------------------------------------------------------------
# Our home is also the login page
# No @login_required
# ----------------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():

    join_form = JoinMatch()
    # we need to check if user has logged in already to render a logged in homepage
    if current_user.is_authenticated:
        if join_form.validate_on_submit():
            match_id = join_form.match_id.data

            if match_state.get_match_by_id(match_id) is None:
                flash("That match doesn't exist", "danger")
                return redirect(url_for("home"))

            return redirect(url_for("match", match_id=match_id))

        return render_template("home_loggedIn.html", title="Home", form=join_form)

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
        return render_template("home_loggedIn.html", title="Home", form=join_form)

    return render_template(
        "home.html", title="Home", leaderboard=leaderboard, form=form
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            profile_pic=f"https://api.dicebear.com/9.x/croodles/svg?seed={form.username.data}&flip=true&backgroundColor=FFFFFF",
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


@app.route("/match")
@login_required
def create_match():
    match_id, match = match_state.create_match(current_user.username)
    return redirect(url_for("match", match_id=match_id))


@app.route("/match/<match_id>")
@login_required
def match(match_id):
    username = current_user.username
    match = match_state.get_match_by_id(match_id)
    if match is None:
        return redirect(url_for("home"))

    if match["opponent"] is None and username != match["host"]:
        match_state.join_match(match_id, username)

    data = {"username": username, "match_id": match_id, "match": match}
    return render_template("board.html", data=data)


# ----------------------------------------------------------------
# Anything Below is just helper functions or testing
# (Should be removed or made official)
# ----------------------------------------------------------------


# Cache static files on client
# Source: https://stackoverflow.com/questions/77569410/flask-possible-to-cache-images
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
@app.route("/static/<path:filename>")
def static(filename):
    resp = make_response(send_from_directory("static/", filename))
    resp.headers["Cache-Control"] = "max-age=604800"
    return resp


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
    # db.drop_all()
    # db.create_all()
    upgrade()
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

    return "".join(data)


# ====================== Tournament Functions ======================
# Once user clicks "Create Tournament", we will create a tournament,
# then redirect to the tournament page where the bracket will be generated
# based on the tournament code.

# These functions are used to initialize tournament and generate bracket
# @app.route("/create_tournament")
# @app.route("/tournament")
# @login_required
# def create_tournament():
#   tournament_code = create_Tournament(current_user.id)
# bracket = get_simple_bracket(tournament_code)
#
# return redirect(url_for('tournament', tournament_code=tournament_code))

# These function will generate tournament_bracket site
# @app.route("/tournament/<tournament_code>", methods=['GET', 'POST'])
# @login_required
# def tournament(tournament_code):
# find tournament by code
#   tournament = db.session.scalar(
#      sa.select(Tournament).where(Tournament.tournament_code == tournament_code)
# )
# if not tournament:
#   return render_template('404.html'), 404

# Count how many players have joined this tournament
#    players_count = db.session.scalars(
#       sa.select(MatchPlayer)
#      .join(Match)
#     .where(Match.tournament_id == tournament.id)
# ).all()


#    bracket = get_simple_bracket(tournament_code)
#
#   return render_template(
#       'tournament_bracket.html',
#      bracket=bracket,
#     tournament_code=tournament_code,
#    match_count=len(tournament.matches),
#   players_count=len(players_count)
#  )

# This function will add more matches to the tournament when the host clicks "Add More Matches" button
# @app.route("/moreMatches/<tournament_code>", methods=['POST'])
# @login_required
# def more_matches(tournament_code):
# find tournament by code
#   tournament = db.session.scalar(
#      sa.select(Tournament).where(Tournament.tournament_code == tournament_code)
# )
# if not tournament:
#        return render_template('404.html'), 404

#   add_more_matches(tournament)

#  return jsonify(
#     status="ok",
#    #added=match_count,
#   total_matches=len(tournament.matches)
# )


# ====================== Match Functions ======================
# @app.route("/match", methods=["GET", "POST"])
# @login_required
# def match():

#     match_id = "123ABC"

#     return render_template("match.html", match_id=match_id)
