from sqlalchemy import text
from tutortrack import db


def deleteTopicsAndSessions():
    """
    Delete the topics and sessions linked to no children.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            topics = conn.execute(
                text("SELECT TopicID FROM Topic")
            ).fetchall()
            sessions = conn.execute(
                text("SELECT SessionID FROM Session")
            ).fetchall()
            for topic in topics:
                topicSearch = conn.execute(
                    text("SELECT * FROM ChildTopic WHERE TopicID=:id"),
                    {"id": topic[0]}
                ).fetchall()
                if len(topicSearch) == 0:
                    conn.execute(
                        text("DELETE FROM Topic WHERE TopicID=:id"),
                        {"id": topic[0]}
                    )

            for session in sessions:
                sessionSearch = conn.execute(
                    text("SELECT * FROM ChildSession WHERE SessionID=:id"),
                    {"id": session[0]}
                ).fetchall()
                if len(sessionSearch) == 0:
                    conn.execute(
                        text("DELETE FROM Session WHERE SessionID=:id"),
                        {"id": session[0]}
                    )
