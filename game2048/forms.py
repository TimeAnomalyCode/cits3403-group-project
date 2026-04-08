from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[
                               DataRequired(), 
                               Length(min=2, max=20),
                               Regexp(r'[a-zA-Z]+$', message='Only letters are acceptable')
                            ])
    
    email = StringField('Email', 
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    
    # For now, we don't check if the password has special characters, can be added later
    password = PasswordField('Password', 
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=20),
                             ])
    
    confirm_password = PasswordField('Confirm Password', 
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=20),
                                 EqualTo('password')
                             ])
    
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):    
    email = StringField('Email', 
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    
    password = PasswordField('Password', 
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=20),
                             ])
    
    submit = SubmitField('Login')
