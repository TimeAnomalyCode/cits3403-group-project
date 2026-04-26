from threading import Thread
from flask import render_template
from flask_mail import Message
from game2048 import app, mail


# This makes sending emails a background thread
# This allows the page to respond immediately without waiting for user
def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# Use send_email() to send emails
def send_email(
    subject: str,
    recipients: list[str],
    text_body: str,
    html_body: str,
    sender: str = app.config["MAIL_DEFAULT_SENDER"],
):

    msg = Message(
        subject, sender=sender, recipients=recipients, body=text_body, html=html_body
    )
    Thread(target=_send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()

    send_email(
        "[2048 Battle] Reset your Password",
        [user.email],
        render_template("email/reset_password.txt", user=user, token=token),
        render_template("email/reset_password.html", user=user, token=token),
    )
