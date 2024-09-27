from flask import flash, redirect, url_for
from flask_login import UserMixin, current_user
from functools import wraps
from sqlalchemy.engine import Engine
from sqlalchemy import event
from tutortrack import db, login_manager


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@login_manager.user_loader
def user_loader(userID):
    return User.query.get(userID)


def login_required(type="any"):
    """
    Only allow logged in users of a particular type (tutor or parent)
    to access a particular route.
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.type != type and type != "any":
                flash("You are not permitted to access this page.", "danger")
                return redirect(url_for("other.home"))
            return function(*args, **kwargs)
        return wrapper
    return decorator


class User(db.Model, UserMixin):
    __tablename__ = "User"
    userID = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    passwordReset = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return (self.userID)
