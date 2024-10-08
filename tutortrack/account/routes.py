from flask import (
    render_template, redirect, url_for, flash, request, Blueprint
)
from flask_login import current_user, logout_user
from sqlalchemy import text
from tutortrack import db, bcrypt
from tutortrack.account.forms import (
    TutorAccountForm, ParentAccountForm, DeleteAccountForm,
    ChangePasswordForm, SearchForm, AddChildForm
)
from tutortrack.models import login_required
from tutortrack.users.utils import generateChildID
from tutortrack.account.utils import deleteTopicsAndSessions

account = Blueprint(
    "account", __name__, template_folder="templates",
    static_folder="static", static_url_path="/account/static"
)


@account.route("/account", methods=["GET", "POST"])
@login_required()
def account_details():
    if current_user.type == "tutor":
        form = TutorAccountForm()
    elif current_user.type == "parent":
        form = ParentAccountForm()
        with db.engine.connect() as conn:
            # Get parent's children
            children = conn.execute(text(
                "SELECT * FROM Child WHERE ParentID=:id " +
                "ORDER BY Surname, Firstname"
            ),
                {"id": current_user.userID}
            ).fetchall()

    if form.validate_on_submit():
        # If form is valid and submitted
        with db.engine.connect() as conn:
            with conn.begin():
                # Update account details
                conn.execute(text(
                    "UPDATE User SET Firstname=:fn, Surname=:sn, Email=:em " +
                    "WHERE UserID=:id"
                ),
                    {
                        "fn": form.firstname.data, "sn": form.surname.data,
                        "em": form.email.data, "id": current_user.userID
                }
                )
        flash("Your account details have been updated!", "success")
        return redirect(url_for("account.account_details"))
    elif request.method == "GET":
        # Fill the form fields with current info
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        if current_user.type == "tutor":
            form.tutorCode.data = current_user.userID

    if current_user.type == "tutor":
        return render_template(
            "tutor_account_details.html", title="Account", form=form
        )
    elif current_user.type == "parent":
        return render_template(
            "parent_account_details.html", title="Account", form=form,
            children=children
        )


@account.route("/delete/account", methods=["GET", "POST"])
@login_required()
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        # If form is valid and submitted
        with db.engine.connect() as conn:
            with conn.begin():
                if current_user.type == "tutor":
                    # Get parents linked to tutor
                    parentIDs = conn.execute(
                        text("SELECT ParentID FROM Parent WHERE TutorID=:id"),
                        {"id": current_user.userID}
                    ).fetchall()

                    # Delete all parent records linked to tutor
                    # (Will delete the child records automatically)
                    for parentID in parentIDs:
                        conn.execute(
                            text("DELETE FROM User WHERE UserID=:id"),
                            {"id": parentID[0]}
                        )
                # Delete user's account record
                conn.execute(
                    text("DELETE FROM User WHERE UserID=:id"),
                    {"id": current_user.userID}
                )

        # Delete topics and sessions that are now linked to no children
        deleteTopicsAndSessions()

        logout_user()
        return redirect(url_for("users.login"))

    return render_template("delete_account.html", form=form)


@account.route("/password/change", methods=["GET", "POST"])
@login_required()
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # If form is valid and submitted
        # Encrypt password
        hashedPassword = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")
        with db.engine.connect() as conn:
            with conn.begin():
                # Update password
                conn.execute(
                    text("UPDATE User SET Password=:pw WHERE UserID=:id"),
                    {"pw": hashedPassword, "id": current_user.userID}
                )
        flash(
            "Password change successful. You may now log in with your " +
            "new password!",
            "success"
        )
        return redirect(url_for("account.account_details"))

    return render_template("change_password.html", form=form)


@account.route("/parent/accounts", methods=["GET", "POST"])
@login_required(type="tutor")
def parent_accounts():
    with db.engine.connect() as conn:
        # Get parents linked to tutor
        parents = conn.execute(text(
            "SELECT * " +
            "FROM User JOIN Parent ON User.UserID=Parent.ParentID " +
            "WHERE Parent.TutorID=:id AND User.Confirmed=1 " +
            "ORDER BY Surname, Firstname"
        ),
            {"id": current_user.userID}
        ).fetchall()

        form = SearchForm()
        if request.method == "POST":
            # Remove any spaces from the user's search
            search = "%" + request.form["search"].replace(" ", "") + "%"

            # Get parents linked to tutor matching the search
            parents = conn.execute(text(
                "SELECT * " +
                "FROM User JOIN Parent ON User.UserID=Parent.ParentID " +
                "WHERE Parent.TutorID=:id AND User.Confirmed=1 AND " +
                "(Firstname LIKE :search OR Surname LIKE :search OR " +
                "(Firstname || Surname) LIKE :search) " +  # || = concatenation
                "ORDER BY Surname, Firstname"
            ),
                {"id": current_user.userID, "search": search}
            ).fetchall()

            return render_template(
                "search_parent_accounts.html", title="Parent Accounts",
                parents=parents, form=form
            )

        return render_template(
            "tutor_parent_accounts.html", title="Parent Accounts",
            parents=parents, form=form
        )


@account.route("/parent<parentID>", methods=["GET", "POST"])
@login_required(type="tutor")
def parent_details(parentID):
    with db.engine.connect() as conn:
        # Get the parent's details
        parent = conn.execute(text(
            "SELECT User.Firstname, User.Surname, User.Email, " +
            "Parent.TutorID " +
            "FROM User, Parent " +
            "WHERE UserID=ParentID AND UserID=:id"
        ),
            {"id": parentID}
        ).fetchall()[0]

        # If user is not the parent's tutor, redirect them
        if current_user.userID != parent[3]:
            flash("You are not permitted to access this page.", "danger")
            return redirect(url_for("other.home"))

        # Get parent's children
        children = conn.execute(text(
            "SELECT Firstname, Surname " +
            "FROM Child " +
            "WHERE ParentID=:id " +
            "ORDER BY Surname, Firstname"
        ),
            {"id": parentID}
        ).fetchall()

    return render_template(
        "tutor_parent_details.html", title="Parent Accounts", parent=parent,
        children=children
    )


@account.route("/add/child", methods=["GET", "POST"])
@login_required(type="parent")
def add_child():
    form = AddChildForm()
    if form.validate_on_submit():
        # If form valid and submitted
        childID = generateChildID()
        with db.engine.connect() as conn:
            with conn.begin():
                # Add child record
                conn.execute(
                    text("INSERT INTO Child VALUES (:id, :fn, :sn, :pID)"),
                    {
                        "id": childID, "fn": form.childFirstname.data,
                        "sn": form.childSurname.data,
                        "pID": current_user.userID
                    }
                )
        flash(
            f"{form.childFirstname.data} has been successfully added to " +
            "your account.",
            "success"
        )
        return redirect(url_for("account.account_details"))

    return render_template("add_child.html", title="Add Child", form=form)


@account.route("/delete/child<childID>")
@login_required(type="parent")
def delete_child(childID):
    parent = False
    with db.engine.connect() as conn:
        # Get child IDs
        childIDs = conn.execute(
            text("SELECT ChildID FROM Child WHERE ParentID=:id"),
            {"id": current_user.userID}
        ).fetchall()
    # Determine whether user is the child's parent
    for child in childIDs:
        if str(childID) == str(child[0]):
            parent = True

    if parent == True:
        if len(childIDs) > 1:
            # If more than 1 child
            with db.engine.connect() as conn:
                with conn.begin():
                    # Delete child
                    conn.execute(
                        text("DELETE FROM Child WHERE ChildID=:id"),
                        {"id": childID}
                    )
            flash(
                "The selected child has been deleted from your account.",
                "info"
            )
        else:
            # A parent cannot have less than one child registered on
            # their account
            flash(
                "You must have at least one child linked to your account.",
                "danger"
            )
        # Delete topics and sessions now linked to no children
        deleteTopicsAndSessions()
    else:
        flash("You are not permitted to access this page.", "danger")

    return redirect(url_for("account.account_details"))
