from sqlalchemy import text
from tutortrack import db


def deleteTopicsAndSessions():
    """
    Delete the topics and sessions linked to no children.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            # Get all topic IDs
            topicIDs = conn.execute(
                text("SELECT TopicID FROM Topic")
            ).fetchall()
            # Get all session IDs
            sessionIDs = conn.execute(
                text("SELECT SessionID FROM Session")
            ).fetchall()

            for topicID in topicIDs:
                childTopics = conn.execute(
                    text("SELECT * FROM ChildTopic WHERE TopicID=:id"),
                    {"id": topicID[0]}
                ).fetchall()
                if len(childTopics) == 0:
                    # If no children linked to topic, delete
                    conn.execute(
                        text("DELETE FROM Topic WHERE TopicID=:id"),
                        {"id": topicID[0]}
                    )

            for sessionID in sessionIDs:
                childSessions = conn.execute(
                    text("SELECT * FROM ChildSession WHERE SessionID=:id"),
                    {"id": sessionID[0]}
                ).fetchall()
                if len(childSessions) == 0:
                    # If no children linked to session, delete
                    conn.execute(
                        text("DELETE FROM Session WHERE SessionID=:id"),
                        {"id": sessionID[0]}
                    )
