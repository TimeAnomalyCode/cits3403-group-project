from flask import render_template, flash, redirect, url_for, request, make_response, send_from_directory
from flask_mail import Message
from game2048 import app, db, mail, socketio
from game2048.forms import RegistrationForm, LoginForm
from game2048.models import User

# Our home is also the login page
@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    # we need to check if user has logged in already to render a logged in homepage
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@game.com' and form.password.data =='123456789':
            flash('You have logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful', 'danger')
    return render_template('home.html', title='Home', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_password = generate_password_hash(form.password.data)
        # user = User(
        #     username=form.username.data,
        #     email=form.email.data,
        #     password=hashed_password,
        # )
        # db.session.add(user)
        # db.session.commit()

        # One time display of status
        flash(f'You have created an account! Please Log In', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html', title='Register', form=form)

@app.route("/send")
def index():
    msg = Message(subject='2048 Battle!', sender='test@gmail.com', recipients=['nerd@gmail.com'])
    msg.body = request.args.get('message')
    mail.send(msg)
    return f"<p>Message sent!</p> {msg}"

# Cache static files on client
# Source: https://stackoverflow.com/questions/77569410/flask-possible-to-cache-images
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
@app.route('/static/<path:filename>')
def static(filename):
    resp = make_response(send_from_directory('static/', filename))
    resp.headers['Cache-Control'] = 'max-age=604800'
    return resp

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