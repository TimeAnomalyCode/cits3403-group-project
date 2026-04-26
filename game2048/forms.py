from game2048 import db
from game2048.models import User
import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Regexp,
    Email,
    EqualTo,
    ValidationError,
)


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            Regexp(r"[a-zA-Z]+$", message="Only letters are acceptable"),
        ],
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    # For now, we don't check if the password has special characters, can be added later
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), Length(min=8, max=20), EqualTo("password")],
    )

    submit = SubmitField("Sign Up")

    # Custom username validator to make sure no 2 usernames are same
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")

    # Custom email validator to make sure no 2 emails are the same
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("Please use a different email address.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    remember_me = BooleanField("Remember Me")

    submit = SubmitField("Login")


class ChangeUsername(FlaskForm):
    new_username = StringField(
        "New Username",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            Regexp(r"[a-zA-Z]+$", message="Only letters are acceptable"),
        ],
    )

    password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    submit = SubmitField("Update Username")

    # Overloaded Constructor
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    # We get the original username and the new_username
    # If they're not the same, we check db if the username already exists
    # If username already exists, raise Validation Error
    def validate_new_username(self, new_username):
        if new_username.data != self.original_username:
            user = db.session.scalar(
                sa.Select(User).where(User.username == new_username.data)
            )

            if user is not None:
                raise ValidationError("Please use a different username")

        else:
            raise ValidationError("Old username cannot be the same as new username")


class ChangePassword(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), Length(min=8, max=20), EqualTo("new_password")],
    )

    submit = SubmitField("Update Password")

    def validate_new_password(self, new_password):
        if self.current_password.data == new_password.data:
            raise ValidationError("Old password cannot be the same as new password")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=20),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), Length(min=8, max=20), EqualTo("password")],
    )

    submit = SubmitField("Request Password Reset")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_password(self, password):
        if self.user.check_password(password.data):
            raise ValidationError("Old password cannot be the same as new password")
