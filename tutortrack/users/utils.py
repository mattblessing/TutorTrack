from flask import render_template, url_for
from sqlalchemy import text
from tutortrack import db, bcrypt
from tutortrack.models import User
from tutortrack.token import generateToken
from tutortrack.email import sendEmail
import random
import time


def generateUserID():
    """
    Generate a unique ID for a new user.
    """
    unique = False
    while unique == False:
        id = random.randint(100000, 999999)
        with db.engine.connect() as conn:
            idSearch = conn.execute(
                text("SELECT * FROM User WHERE UserID=:id"), {"id": id}
            ).fetchall()
        if len(idSearch) == 0:
            unique = True
    return id


def generateChildID():
    """
    Generate a unique ID for a new child.
    """
    unique = False
    while unique == False:
        id = random.randint(100000, 999999)
        with db.engine.connect() as conn:
            idSearch = conn.execute(
                text("SELECT * FROM Child WHERE ChildID=:generatedID"),
                {"generatedID": id}
            ).fetchall()
        if len(idSearch) == 0:
            unique = True
    return id


def createTutor(form):
    """
    Add a tutor record to the database.

    Args:
        form: The validated and submitted tutor registration form.

    Returns:
        user: A user object for the tutor.
    """
    # Encrypt password
    hashedPassword = bcrypt.generate_password_hash(
        form.password.data
    ).decode("utf-8")

    tutorID = generateUserID()
    user = User(
        userID=tutorID, firstname=form.firstname.data,
        surname=form.surname.data, email=form.email.data.lower(),
        password=hashedPassword, confirmed=False, passwordReset=False,
        type="tutor"
    )

    # Add tutor record
    with db.engine.connect() as conn:
        with conn.begin():
            conn.execute(text(
                "INSERT INTO User VALUES (:id, :fn, :sn, :em, :pw, :cf, " +
                ":pr, :type)"
            ),
                {
                    "id": user.userID, "fn": user.firstname,
                    "sn": user.surname, "em": user.email,
                    "pw": hashedPassword, "cf": user.confirmed,
                    "pr": user.passwordReset, "type": user.type
            }
            )
            conn.execute(
                text("INSERT INTO Tutor VALUES (:id)"), {"id": user.userID}
            )

    return user


def createParentandChildren(form):
    """
    Add parent and child records to the database.

    Args:
        form: The validated and submitted parent registration form.

    Returns:
        user: A user object for the parent.
    """
    # Encrypt password
    hashedPassword = bcrypt.generate_password_hash(
        form.password.data
    ).decode("utf-8")

    parentID = generateUserID()
    user = User(
        userID=parentID, firstname=form.firstname.data,
        surname=form.surname.data, email=form.email.data.lower(),
        password=hashedPassword, confirmed=False, passwordReset=False,
        type="parent"
    )

    # Add parent record
    with db.engine.connect() as conn:
        with conn.begin():
            conn.execute(text(
                "INSERT INTO User VALUES (:id, :fn, :sn, :em, :pw, :cf, " +
                ":pr, :type)"
            ),
                {
                    "id": user.userID, "fn": user.firstname,
                    "sn": user.surname, "em": user.email,
                    "pw": hashedPassword, "cf": user.confirmed,
                    "pr": user.passwordReset, "type": user.type
            }
            )
            conn.execute(
                text("INSERT INTO Parent VALUES (:id, :tID)"),
                {"id": user.userID, "tID": form.tutorCode.data}
            )

    # Add child records
    for child in form.children.data:
        childID = generateChildID()
        with db.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("INSERT INTO Child VALUES (:id, :fn, :sn, :pID)"),
                    {
                        "id": childID, "fn": child["childFirstname"],
                        "sn": child["childSurname"], "pID": user.userID
                    }
                )

    return user


def verificationEmail(email):
    """
    Send a user verification email.

    Args:
        email (str): The recipient email address.
    """
    token = generateToken(email)
    confirmUrl = url_for("users.confirm_email", token=token, _external=True)
    html = render_template(
        "emails/account_confirmation.html", confirm_url=confirmUrl
    )
    subject = "Account confirmation"
    sendEmail(email, subject, html)


def resetEmail(email):
    """
    Send a password reset email.

    Args:
        email (str): The recipient email address.
    """
    token = generateToken(email)
    resetUrl = url_for("users.reset_password", token=token, _external=True)
    html = render_template("emails/password_reset.html", reset_url=resetUrl)
    subject = "Password reset"
    sendEmail(email, subject, html)


def passwordResetTimer(app, user):
    """
    Set the password reset attribute to 0 for a user 30 minutes after
    their password reset email is sent.

    Args:
        app: The Flask application object.
        user: The user database record.
    """
    with app.app_context():
        # Wait 30 minutes
        time.sleep(1800)
        with db.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("UPDATE User SET PasswordReset=0 WHERE UserID=:id"),
                    {"id": user[0][0]}
                )
