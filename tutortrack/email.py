from flask import current_app
from flask_mail import Message
from threading import Thread
from tutortrack import mail
import os


def sendAsyncEmail(app, msg):
    """
    Send an email asynchronously.

    Args:
        app: The Flask application object.
        msg: The email Message object.
    """
    with app.app_context():
        mail.send(msg)


def sendEmail(to, subject, template):
    """
    Send an email.

    Args:
        to (str): The recipient email address.
        subject (str): The subject.
        template (str): The HTML email content.
    """
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config["MAIL_USERNAME"]
    )
    app = current_app._get_current_object()
    thread = Thread(target=sendAsyncEmail, args=[app, msg])
    thread.start()


def sendAttachmentEmail(to, subject, template, attachment):
    """
    Send an email containing an attachment.

    Args:
        to (str): The recipient email address.
        subject (str): The subject.
        template (str): The HTML email content.
        attachment (str): The filename of the attachment.
    """
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config["MAIL_USERNAME"]
    )
    app = current_app._get_current_object()
    with app.open_resource(os.getcwd()+"/"+attachment) as file:
        msg.attach(attachment, "image/png", file.read())
    thread = Thread(target=sendAsyncEmail, args=[app, msg])
    thread.start()
