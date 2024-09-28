from flask import (
    render_template, redirect, url_for, flash, request, Blueprint, current_app
)
from flask_login import login_user, logout_user, current_user
from sqlalchemy import text
from threading import Thread
from tutortrack import db, bcrypt
from tutortrack.users.forms import (
    TutorRegistrationForm, ParentRegistrationForm, ChildForm, EmailForm,
    LoginForm, RequestResetForm, ResetForm
)
from tutortrack.users.utils import (
    createTutor, createParentandChildren, verificationEmail, resetEmail,
    passwordResetTimer
)
from tutortrack.models import User
from tutortrack.token import confirmToken

users = Blueprint(
    "users", __name__, template_folder="templates", static_folder="static",
    static_url_path="/users/static"
)


@users.route("/", methods=["GET", "POST"])
@users.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    form = LoginForm()
    if form.validate_on_submit():
        # If form valid and submitted
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user.confirmed == 1:
            # If user has confirmed their email address
            login_user(user, remember=form.remember.data)

            # If user tries to access a page without being logged in,
            # they will be taken to the login page but we then want to
            # redirect them to the page they tried to access once they
            # have logged in
            nextPage = request.args.get("next")
            if nextPage:
                # If there is a "next" argument then redirect user
                return redirect(nextPage)
            else:
                # Otherwise take them to home page
                return redirect(url_for("other.home"))
        else:
            # If user is yet to confirm their email address
            flash("Please confirm your account.", "warning")

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/tutor/register", methods=["GET", "POST"])
def tutor_register():
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    form = TutorRegistrationForm()
    if form.validate_on_submit():
        # If form valid and submitted
        # Add a tutor record to the database
        tutor = createTutor(form)
        # Send verification email to tutor
        verificationEmail(tutor.email)
        flash(
            "Registration successful. Check your inbox (and junk mail) for " +
            "a confirmation email!",
            "success"
        )
        return redirect(url_for("users.login"))

    return render_template("tutor_register.html", title="Register", form=form)


@users.route("/parent/register", methods=["GET", "POST"])
def parent_register():
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    form = ParentRegistrationForm()
    childForm = ChildForm(prefix="children-_-")
    if form.validate_on_submit():
        # If form valid and submitted
        # Add parent and child records to the database
        parent = createParentandChildren(form)
        # Send verification email to parent
        verificationEmail(parent.email)
        flash(
            "Registration successful. Check your inbox (and junk mail) for " +
            "a confirmation email!",
            "success"
        )
        return redirect(url_for("users.login"))

    return render_template(
        "parent_register.html", title="Register", form=form, _template=childForm
    )


@users.route("/confirm/<token>")
def confirm_email(token):
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    # Token is valid for an hour
    email = confirmToken(token)
    if email == False:
        # If token is invalid
        flash("The confirmation link is invalid or has expired.", "danger")
    else:
        with db.engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": email}
            ).fetchall()

        if len(user) != 0:
            if user[0][5] == 1:
                # If account is already confirmed
                flash("Account already confirmed.", "success")
            else:
                # Update user record
                with db.engine.connect() as conn:
                    with conn.begin():
                        conn.execute(text(
                            "UPDATE User SET Confirmed=1 WHERE UserID=:id"
                        ),
                            {"id": user[0][0]}
                        )
                flash(
                    "You have successfully confirmed your account.",
                    "success"
                )

    return redirect(url_for("users.login"))


@users.route("/resend/confirm", methods=["GET", "POST"])
def resend_confirm():
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    form = EmailForm()
    if form.validate_on_submit():
        # If form valid and submitted
        with db.engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": form.email.data.lower()}
            ).fetchall()[0]

        if user[5] != 1:
            # Resend verification email
            verificationEmail(user[3])
            flash(
                "We have resent you a confirmation email! Check your inbox " +
                "and junk folder.",
                "success"
            )
            return redirect(url_for("users.login"))
        else:
            # If account is already confirmed
            flash("Account already confirmed.", "success")

    return render_template(
        "resend_account_confirmation.html", title="Confirm", form=form
    )


@users.route("/request/reset", methods=["GET", "POST"])
def request_reset():
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        # If login form is submitted and valid
        with db.engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": form.email.data.lower()}
            ).fetchall()[0]

        if user[6] == 1:
            # If user has a valid password reset link already
            flash("A valid password reset link already exists.", "danger")
            return redirect(url_for("users.request_reset"))

        # Send password reset email
        resetEmail(user[3])
        with db.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "UPDATE User SET PasswordReset=1 WHERE UserID=:id"
                ),
                    {"id": user[0][0]}
                )

        # Set timer for password reset validity
        app = current_app._get_current_object()
        thread = Thread(target=passwordResetTimer, args=[app, user])
        thread.start()
        flash(
            "Request successful. Check your inbox (and junk mail) for a " +
            "password reset email!",
            "success"
        )
        return redirect(url_for("users.login"))
    return render_template("request_password_reset.html", form=form)


@users.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Redirect logged in users to the home page
    if current_user.is_authenticated:
        return redirect(url_for("other.home"))

    # Token is valid for half an hour
    email = confirmToken(token, 1800)

    if email == False:
        # If token is invalid
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for("users.login"))

    with db.engine.connect() as conn:
        user = conn.execute(
            text("SELECT * FROM User WHERE Email=:email"),
            {"email": email}
        ).fetchall()
    if len(user) != 0:
        if user[0][6] == 1:
            # If password reset link is valid
            form = ResetForm()
            if form.validate_on_submit():
                # If form valid and submitted
                if bcrypt.check_password_hash(
                    user[0][4], form.password.data
                ) == False:
                    # If new password
                    hashedPassword = bcrypt.generate_password_hash(
                        form.password.data
                    ).decode("utf-8")
                    with db.engine.connect() as conn:
                        with conn.begin():
                            conn.execute(text(
                                "UPDATE User SET Password=:pw, " +
                                "PasswordReset=0 WHERE UserID=:id"
                            ),
                                {"pw": hashedPassword, "id": user[0][0]}
                            )
                    flash(
                        "Password reset successful. You may now log in " +
                        "with your new password!",
                        "success"
                    )
                    return redirect(url_for("users.login"))
                else:
                    flash("Please enter a new password.", "danger")
        else:
            flash("This password reset link no longer works.", "danger")
            return redirect(url_for("users.login"))

    return render_template("password_reset.html", form=form)
