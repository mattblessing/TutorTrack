from flask import render_template, redirect, url_for, flash
from markupsafe import Markup
from sqlalchemy import text
from tutortrack import db
from tutortrack.utils import notificationEmail
import random


def logSession(form):
    """
    Add a submitted session to the database.

    Args:
        form: The session form filled out by a tutor.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            # Get parent email address
            parent = conn.execute(text(
                "SELECT Email " +
                "FROM User, Child " +
                "WHERE Child.ParentID=User.UserID AND Child.ChildID=:id"
            ),
                {"id": form.child.data}
            ).fetchall()
            sessions = conn.execute(text(
                "SELECT * " +
                "FROM Session " +
                "WHERE Date=:date AND Time=:time AND Duration=:duration"
            ),
                {
                    "date": form.date.data,
                    "time": form.time.data.strftime("%H:%M:%S"),
                    "duration": form.duration.data
            }
            ).fetchall()

            if len(sessions) == 0:
                # If a session does not exist with the entered details,
                # create a new record
                sessionID = generateSessionID()
                conn.execute(text(
                    "INSERT INTO Session VALUES (:id, :date, :time, " +
                    ":duration)"
                ),
                    {
                    "id": sessionID, "date": form.date.data,
                    "time": form.time.data.strftime("%H:%M:%S"),
                    "duration": form.duration.data
                }
                )
            else:
                sessionID = sessions[0][0]
            childSessions = conn.execute(text(
                "SELECT * FROM ChildSession WHERE ChildID=:cID AND " +
                "SessionID=:sID"
            ),
                {"cID": form.child.data, "sID": sessionID}
            ).fetchall()
            if len(childSessions) == 0:
                # If a child-session record does not already exist for the
                # childID and sessionID
                conn.execute(text(
                    "INSERT INTO ChildSession VALUES (:cID, :sID, :desc, " +
                    ":cf, :rank)"
                ),
                    {
                        "cID": form.child.data, "sID": sessionID,
                        "desc": form.description.data,
                        "cf": form.childFocus.data,
                        "rank": form.ranking.data
                }
                )
                email = render_template("emails/session_logged.html")
                notificationEmail(parent[0][0], email)
                flash("The session was successfully logged.", "success")
            else:
                # Display error message with link
                flash(
                    Markup(
                        "That session has already been logged. You can " +
                        'change its details <a href="/change/session/' +
                        f'details/{form.child.data}/{childSessions[0][1]}"' +
                        ">here</a>"
                    ),
                    "info"
                )


def generateSessionID():
    """
    Generate a unique ID for a new session.
    """
    unique = False
    while unique == False:
        id = random.randint(100000, 999999)
        with db.engine.connect() as conn:
            idSearch = conn.execute(
                text("SELECT * FROM Session WHERE SessionID=:id"),
                {"id": id}
            ).fetchall()
        if len(idSearch) == 0:
            unique = True
    return id


def updateSession(form, childID, sessionID):
    """
    Update the details of a particular session.

    Args:
        form: The updated result form filled out by a tutor.
        childID (str): The child's ID.
        sessionID (str): The existing session's ID.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            # Get child's parent
            parent = conn.execute(text(
                "SELECT Email " +
                "FROM User, Child " +
                "WHERE Child.ParentID=User.UserID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()
            # Get children that belong to session that matches form data
            sessions = conn.execute(text(
                "SELECT Session.SessionID, Child.ChildID " +
                "FROM Session, ChildSession, Child " +
                "WHERE Date=:date AND Time=:time AND Duration=:dr AND " +
                "Child.ChildID=ChildSession.ChildID AND Session.SessionID=" +
                "ChildSession.SessionID"
            ),
                {
                    "date": form.date.data,
                    "time": form.time.data.strftime("%H:%M:%S"),
                    "dr": form.duration.data
            }
            ).fetchall()

            # If there is a session that matches form data
            if len(sessions) != 0:
                # For each child in this session
                for session in sessions:
                    # If session is already linked to a child-session
                    # record for child
                    if (
                        str(session[1]) == str(childID) and
                        str(session[0]) != str(sessionID)
                    ):
                        flash(
                            "That session already exists for this child.",
                            "danger"
                        )
                        return redirect(url_for(
                            "sessions.change_session_details",
                            childID=childID,
                            sessionID=sessionID
                        ))
                # If the form contents match the selected session, then
                # only update ChildSession
                if str(sessions[0][0]) == str(sessionID):
                    conn.execute(text(
                        "UPDATE ChildSession SET GeneralDescription=:desc, " +
                        "FocusDescription=:cf, Ranking=:rank " +
                        "WHERE ChildID=:cID AND SessionID=:sID"
                    ),
                        {
                            "desc": form.description.data,
                            "cf": form.childFocus.data,
                            "rank": form.ranking.data,
                            "cID": childID,
                            "sID": sessionID
                    }
                    )
                else:
                    numChildren = conn.execute(text(
                        "SELECT ChildID " +
                        "FROM ChildSession " +
                        "WHERE SessionID=:sID AND ChildID!=:cID"
                    ),
                        {"sID": sessionID, "cID": childID}
                    ).fetchall()
                    if len(numChildren) == 0:
                        # If selected session doesn't have any other children
                        # Delete session
                        conn.execute(
                            text("DELETE FROM Session WHERE SessionID=:id"),
                            {"id": sessionID}
                        )
                    # Update SessionID in the ChildSession record
                    conn.execute(text(
                        "DELETE FROM ChildSession WHERE ChildID=:cID AND " +
                        "SessionID=:sID"
                    ),
                        {"cID": childID, "sID": sessionID}
                    )
                    conn.execute(text(
                        "INSERT INTO ChildSession VALUES (:cID, :sID, " +
                        ":desc, :cf, :rank)"
                    ),
                        {
                            "cID": childID,
                            "sID": sessions[0][0],
                            "desc": form.description.data,
                            "cf": form.childFocus.data,
                            "rank": form.ranking.data
                    }
                    )
            # If a new session needs to be created
            else:
                numChildren = conn.execute(text(
                    "SELECT ChildID " +
                    "FROM ChildSession " +
                    "WHERE SessionID=:sID AND ChildID!=:cID"
                ),
                    {"sID": sessionID, "cID": childID}
                ).fetchall()
                if len(numChildren) == 0:
                    # If selected session doesn't have any other children
                    # Delete session
                    conn.execute(
                        text("DELETE FROM Session WHERE SessionID=:id"),
                        {"id": sessionID}
                    )
                newSessionID = generateSessionID()
                # Create new session
                conn.execute(text(
                    "INSERT INTO Session VALUES (:sID, :date, :time, :dr)"
                ),
                    {
                        "sID": newSessionID, "date": form.date.data,
                        "time": form.time.data.strftime("%H:%M:%S"),
                        "dr": form.duration.data
                }
                )
                # Update SessionID in the ChildSession record
                conn.execute(text(
                    "DELETE FROM ChildSession WHERE ChildID=:cID AND " +
                    "SessionID=:sID"
                ),
                    {"cID": childID, "sID": sessionID}
                )
                conn.execute(text(
                    "INSERT INTO ChildSession VALUES (:cID, :sID, :desc, " +
                    ":cf, :rank)"
                ),
                    {
                        "cID": childID, "sID": newSessionID,
                        "desc": form.description.data,
                        "cf": form.childFocus.data,
                        "rank": form.ranking.data
                }
                )
        email = render_template("emails/session_updated.html")
        # Send parent notification
        notificationEmail(parent[0][0], email)
        flash("The session details were successfully changed.", "success")

        return redirect(url_for("sessions.view_sessions"))
