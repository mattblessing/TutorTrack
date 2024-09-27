from flask import render_template, Blueprint
from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.models import login_required
from tutortrack.other.utils import recentUpdates

other = Blueprint(
    "other", __name__, template_folder="templates",
    static_folder="static", static_url_path="/other/static"
)


@other.route("/home")
@login_required()
def home():
    with db.engine.connect() as conn:
        children = conn.execute(text(
            "SELECT Child.Firstname, Child.Surname " +
            "FROM User, Parent, Child " +
            "WHERE User.UserID=Parent.ParentID AND Parent.ParentID=" +
            "Child.ParentID AND Parent.TutorID=:id AND User.Confirmed=1 " +
            "ORDER BY Child.Surname, Child.Firstname"
        ),
            {"id": current_user.userID}
        ).fetchall()

    sessions = {
        "tutors": [["Log a session", "/log/session"]],
        "both": [["View sessions", "/view/sessions"]]
    }
    topics = {
        "tutors": [
            ["Create a topic", "/create/topic"],
            ["View topics", "/view/topics"]
        ]
    }
    results = {
        "tutors": [["Log a result", "/log/result"]],
        "both": [["View results", "/view/results"]]
    }
    reports = {"tutors": [["View reports", "/reports"]]}

    if current_user.type == "parent":
        # Get up to 5 of the most recent sessions/results
        updates = recentUpdates()

        for update in updates:
            if len(update) == 6:  # Update is a session
                update.insert(0, "SESSION")
            else:
                update.insert(0, "RESULT")
    else:
        updates = []

    return render_template(
        "home.html", title="Home", children=children, sessions=sessions,
        topics=topics, results=results, reports=reports, recentUpdates=updates
    )
