from flask import (
    render_template, redirect, url_for, flash, request, Blueprint
)
from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.models import User, login_required
from tutortrack.utils import getChildrenSelectList
from tutortrack.sessions.forms import LogSessionForm, UpdateSessionForm
from tutortrack.sessions.utils import logSession, updateSession
import datetime

sessions = Blueprint(
    "sessions", __name__, template_folder="templates",
    static_folder="static", static_url_path="/sessions/static"
)


@sessions.route("/log/session", methods=["GET", "POST"])
@login_required(type="tutor")
def log_session():
    children = getChildrenSelectList()
    form = LogSessionForm()
    form.child.choices = children  # Set the child select options
    if form.validate_on_submit():
        # If form valid and submitted
        logSession(form)
        return redirect(url_for("sessions.view_sessions"))
    return render_template("log_session.html", title="Log Session", form=form)


@sessions.route("/view/sessions", methods=["GET", "POST"])
@login_required()
def view_sessions():
    with db.engine.connect() as conn:
        form = LogSessionForm()
        if current_user.type == "tutor":
            children = getChildrenSelectList(True)
            form.child.choices = children  # Set the child select options

            sessions = conn.execute(text(
                "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                "Session.SessionID, Session.Date, Session.Time, " +
                "ChildSession.Ranking " +
                "FROM User, Parent, Child, Session, ChildSession " +
                "WHERE User.UserID=Parent.TutorID AND Parent.ParentID=" +
                "Child.ParentID AND Child.ChildID=ChildSession.ChildID AND " +
                "Session.SessionID=ChildSession.SessionID AND User.UserID=" +
                ":id " +
                "ORDER BY Session.Date DESC, Session.Time DESC"
            ),
                {"id": current_user.userID}
            ).fetchall()
            if request.method == "POST":
                # Selecting all children gives a value of ""
                if form.child.data != "":
                    sessions = conn.execute(text(
                        "SELECT Child.ChildID, Child.Firstname, " +
                        "Child.Surname, Session.SessionID, Session.Date, " +
                        "Session.Time, ChildSession.Ranking " +
                        "FROM User, Parent, Child, Session, ChildSession " +
                        "WHERE User.UserID=Parent.TutorID AND " +
                        "Parent.ParentID=Child.ParentID AND Child.ChildID=" +
                        "ChildSession.ChildID AND Session.SessionID=" +
                        "ChildSession.SessionID AND User.UserID=:tID AND " +
                        "Child.ChildID=:cID " +
                        "ORDER BY Session.Date DESC, Session.Time DESC"
                    ),
                        {"tID": current_user.userID, "cID": form.child.data}
                    ).fetchall()
                return render_template(
                    "view_child_sessions.html", title="Sessions",
                    sessions=sessions, form=form
                )
        elif current_user.type == "parent":
            # Parents do not have the option to select all children
            children = getChildrenSelectList()
            form.child.choices = children  # Set the child select options
            sessions = conn.execute(text(
                "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                "Session.SessionID, Session.Date, Session.Time, " +
                "ChildSession.Ranking FROM Parent, Child, Session, " +
                "ChildSession WHERE Parent.ParentID=Child.ParentID AND " +
                "Child.ChildID=ChildSession.ChildID AND Session.SessionID=" +
                "ChildSession.SessionID AND Parent.ParentID=:pID AND " +
                "Child.ChildID=:cID " +
                "ORDER BY Session.Date DESC, Session.Time DESC"
            ),
                {"pID": current_user.userID, "cID": children[0][0]}
            ).fetchall()
            if request.method == "POST":
                sessions = conn.execute(text(
                    "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                    "Session.SessionID, Session.Date, Session.Time, " +
                    "ChildSession.Ranking " +
                    "FROM Parent, Child, Session, ChildSession " +
                    "WHERE Parent.ParentID=Child.ParentID AND " +
                    "Child.ChildID=ChildSession.ChildID AND " +
                    "Session.SessionID=ChildSession.SessionID AND " +
                    "Parent.ParentID=:pID AND Child.ChildID=:cID " +
                    "ORDER BY Session.Date DESC, Session.Time DESC"
                ),
                    {"pID": current_user.userID, "cID": form.child.data}
                ).fetchall()
                return render_template(
                    "view_child_sessions.html", title="Sessions",
                    sessions=sessions, form=form
                )
        return render_template(
            "view_sessions.html", title="Sessions", sessions=sessions,
            form=form
        )


@sessions.route("/delete/session/<childID>/<sessionID>")
@login_required(type="tutor")
def delete_session(childID, sessionID):
    with db.engine.connect() as conn:
        with conn.begin():
            child = conn.execute(text(
                "SELECT Parent.TutorID, Parent.ParentID " +
                "FROM Parent, Child " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()
            if (
                current_user.userID == child[0][0] or
                current_user.userID == child[0][1]
            ):
                # Get number of children that are linked to current session
                numChildren = conn.execute(text(
                    "SELECT ChildID " +
                    "FROM ChildSession " +
                    "WHERE SessionID=:sID AND ChildID!=:cID"
                ),
                    {"sID": sessionID, "cID": childID}
                ).fetchall()

                if len(numChildren) == 0:
                    # Automatically deletes the linked ChildSession
                    conn.execute(
                        text("DELETE FROM Session WHERE SessionID=:id"),
                        {"id": sessionID}
                    )
                else:
                    # Session record is not deleted if other children are
                    # linked to it
                    conn.execute(text(
                        "DELETE FROM ChildSession WHERE ChildID=:cID AND " +
                        "SessionID=:sID"
                    ),
                        {"cID": childID, "sID": sessionID}
                    )
                flash("The session has been successfully deleted.", "info")
                return redirect(url_for("sessions.view_sessions"))
            else:
                flash("You are not permitted to access this page.", "danger")
                return redirect(url_for("other.home"))


@sessions.route("/session/<childID>/<sessionID>", methods=["GET", "POST"])
@login_required()
def session_details(childID, sessionID):
    with db.engine.connect() as conn:
        if current_user.type == "tutor":
            child = conn.execute(text(
                "SELECT User.UserID, Child.ChildID, Child.Firstname, " +
                "Child.Surname " +
                "FROM User, Parent, Child " +
                "WHERE User.UserID=Parent.TutorID AND Parent.ParentID=" +
                "Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()
            if child[0][0] != current_user.userID:
                flash("You are not permitted to access this page.", "danger")
                return redirect(url_for("other.home"))
        elif current_user.type == "parent":
            child = conn.execute(text(
                "SELECT Parent.ParentID, Child.ChildID, Child.Firstname, " +
                "Child.Surname " +
                "FROM Parent, Child " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()
            if child[0][0] != current_user.userID:
                flash("You are not permitted to access this page.", "danger")
                return redirect(url_for("other.home"))

        child = child[0]
        sessionDetails = conn.execute(text(
            "SELECT Session.SessionID, Session.Date, Session.Time, " +
            "Session.Duration, ChildSession.GeneralDescription, " +
            "ChildSession.FocusDescription, ChildSession.Ranking " +
            "FROM Session, ChildSession, Child " +
            "WHERE Session.SessionID=ChildSession.SessionID AND " +
            "Child.ChildID=ChildSession.ChildID AND Child.ChildID=:cID " +
            "AND Session.SessionID=:sID"
        ),
            {"cID": childID, "sID": sessionID}
        ).fetchall()
        session = sessionDetails[0]
        return render_template(
            "session_details.html", title="Session Details", child=child,
            session=session
        )


@sessions.route(
    "/view/change/session/details/<childID>/<sessionID>",
    methods=["GET", "POST"]
)
@sessions.route(
    "/change/session/details/<childID>/<sessionID>", methods=["GET", "POST"]
)
@login_required(type="tutor")
def change_session_details(childID, sessionID):
    with db.engine.connect() as conn:
        child = conn.execute(text(
            "SELECT Parent.TutorID, Parent.ParentID " +
            "FROM Parent, Child " +
            "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
        ),
            {"id": childID}
        ).fetchall()
        if (
            current_user.userID == child[0][0] or
            current_user.userID == child[0][1]
        ):
            form = UpdateSessionForm()
            # Get child details
            child = conn.execute(text(
                "SELECT Firstname, Surname FROM Child WHERE ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()
            child = child[0]
            # Get session details to display in form
            currentSession = conn.execute(text(
                "SELECT Session.Date, Session.Time, Session.Duration, " +
                "ChildSession.GeneralDescription, " +
                "ChildSession.FocusDescription, ChildSession.Ranking " +
                "FROM Session, ChildSession " +
                "WHERE Session.SessionID=ChildSession.SessionID AND " +
                "ChildSession.ChildID=:cID AND ChildSession.SessionID=:sID"
            ),
                {"cID": childID, "sID": sessionID}
            ).fetchall()
            if form.validate_on_submit():
                # If form valid and submitted
                update = updateSession(form, childID, sessionID)
                return update
            elif request.method == "GET":
                # Display the current session details
                form.date.data = datetime.datetime.strptime(
                    currentSession[0][0], "%Y-%m-%d"
                )
                form.time.data = datetime.datetime.strptime(
                    currentSession[0][1], "%H:%M:%S"
                )
                form.duration.data = currentSession[0][2]
                form.description.data = currentSession[0][3]
                form.childFocus.data = currentSession[0][4]
                form.ranking.data = currentSession[0][5]
            return render_template(
                "change_session_details.html", title="Change Session Details",
                child=child, form=form
            )
        else:
            flash("You are not permitted to access this page.", "danger")
            return redirect(url_for("other.home"))
