from flask_mail import Message

from flask_app import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template
    )
    mail.send(msg)
