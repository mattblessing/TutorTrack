from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.utils import getChildrenSelectList, quicksort


def getSessions():
    """
    Get sessions for all children linked to parent.

    Returns:
        sessionList (list): The list of session records.
    """
    # Get list of parent's children
    children = getChildrenSelectList()

    sessionList = []
    for child in children:
        # For each child
        with db.engine.connect() as conn:
            # Get details of each session for the child
            sessions = conn.execute(text(
                "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                "Session.SessionID, Session.Date, Session.Time " +
                "FROM Parent, Child, Session, ChildSession " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=" +
                "ChildSession.ChildID AND Session.SessionID=" +
                "ChildSession.SessionID AND Parent.ParentID=:uID " +
                "AND Child.ChildID=:cID " +
                "ORDER BY Session.Date DESC"
            ),
                {"uID": current_user.userID, "cID": child[0]}
            ).fetchall()

        sessionList += sessions

    return sessionList


def getResults():
    """
    Get results for all children linked to parent.

    Returns:
        resultList (list): The list of result records.
    """
    # Get list of parent's children
    children = getChildrenSelectList()

    resultList = []
    for child in children:
        #  For each child
        with db.engine.connect() as conn:
            # Get details of each result for the child
            results = conn.execute(text(
                "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                "Result.ResultID, Result.Date, Result.Type, Topic.Name " +
                "FROM Parent, Child, Result, Topic " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=" +
                "Result.ChildID AND Topic.TopicID=Result.TopicID AND " +
                "Parent.ParentID=:uID AND Child.ChildID=:cID " +
                "ORDER BY Result.Date DESC"
            ),
                {"uID": current_user.userID, "cID": child[0]}
            ).fetchall()

        resultList += results

    return resultList


def recentUpdates():
    """
    Get up to 5 of the most recent sessions/results that have been 
    logged.

    Returns:
        recentUpdates (list): The most recent session/result records.
    """
    # Get all sessions and results linked to parent
    sessions = getSessions()
    results = getResults()

    # Combine list into a list of "updates"
    updates = sessions + results

    # Convert each tuple to a list for quicksort
    updates = [list(row) for row in updates]
    if len(updates) != 0:
        pivot = updates.pop(len(results)//2)
        # Set the pivot as the central item in the list
        updates.insert(0, pivot)
        # Sort the updates list into chronological order
        recentUpdates = quicksort(updates, 0, len(updates)-1, "date")
    else:
        recentUpdates = []
    # Put the list in reverse chronological order
    recentUpdates = recentUpdates[::-1]
    # Take the most recent 5 if more than 5
    if len(recentUpdates) > 5:
        recentUpdates = recentUpdates[:5]

    return recentUpdates
