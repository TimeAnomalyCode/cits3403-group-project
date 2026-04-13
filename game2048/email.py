from flask import render_template
from flask_mail import Message
from game2048 import app, mail

def send_email(subject: str, recipients: list[str], text_body: str, html_body: str, sender: str = app.config['MAIL_DEFAULT_SENDER']):
    msg = Message(subject, sender=sender, recipients=recipients, body=text_body, html=html_body)
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()

    send_email('[2048 Battle] Reset your Password',
               [user.email],
               render_template('email/reset_password.txt', user=user, token=token),
               render_template('email/reset_password.html', user=user, token=token)
    )