import sqlite3
from sqlite3 import Error


def createConnection(dbFile):
    """
    Create a database connection to the given database file.

    Args:
        dbFile (str): The path to the database .db file.

    Returns:
        connection (sqlite3.Connection | None): The connection to the
            database or None.
    """
    connection = None
    try:
        connection = sqlite3.connect(dbFile)
    except Error as error:
        print(error)

    return connection


def createDatabase(dbFile="database.db"):
    """
    Create the database at the given file path.

    Args:
        dbFile (str): The path to the database file.
    """
    userTableSQL = (
        "CREATE TABLE IF NOT EXISTS User (" +
        "UserID INTEGER PRIMARY KEY," +
        "Firstname VARCHAR(20) NOT NULL," +
        "Surname VARCHAR(40) NOT NULL," +
        "Email VARCHAR(320) NOT NULL," +
        "Password VARCHAR(128) NOT NULL," +
        "Confirmed BOOLEAN NOT NULL," +
        "PasswordReset BOOLEAN NOT NULL," +
        "Type VARCHAR(20) NOT NULL);"
    )

    tutorTableSQL = (
        "CREATE TABLE IF NOT EXISTS Tutor (" +
        "TutorID INTEGER PRIMARY KEY," +
        "FOREIGN KEY (TutorID) REFERENCES User (UserID) ON DELETE CASCADE);"
    )

    parentTableSQL = (
        "CREATE TABLE IF NOT EXISTS Parent (" +
        "ParentID INTEGER PRIMARY KEY," +
        "TutorID INTEGER NOT NULL," +
        "FOREIGN KEY (ParentID) REFERENCES User (UserID) ON DELETE CASCADE," +
        "FOREIGN KEY (TutorID) REFERENCES Tutor (TutorID) ON DELETE CASCADE);"
    )

    childTableSQL = (
        "CREATE TABLE IF NOT EXISTS Child (" +
        "ChildID INTEGER PRIMARY KEY," +
        "Firstname VARCHAR(20) NOT NULL," +
        "Surname VARCHAR(40) NOT NULL," +
        "ParentID INTEGER NOT NULL," +
        "FOREIGN KEY (ParentID) REFERENCES Parent (ParentID) ON DELETE " +
        "CASCADE);"
    )

    sessionTableSQL = (
        "CREATE TABLE IF NOT EXISTS Session (" +
        "SessionID INTEGER PRIMARY KEY," +
        "Date DATE NOT NULL," +
        "Time TIME NOT NULL," +
        "Duration INTEGER NOT NULL);"
    )

    childSessionTableSQL = (
        "CREATE TABLE IF NOT EXISTS ChildSession (" +
        "ChildID INTEGER NOT NULL," +
        "SessionID INTEGER NOT NULL," +
        "GeneralDescription VARCHAR(500) NOT NULL," +
        "FocusDescription VARCHAR(500) NOT NULL," +
        "Ranking INTEGER NOT NULL," +
        "FOREIGN KEY (ChildID) REFERENCES Child (ChildID) ON DELETE " +
        "CASCADE," +
        "FOREIGN KEY (SessionID) REFERENCES Session (SessionID) ON DELETE " +
        "CASCADE," +
        "PRIMARY KEY (ChildID, SessionID));"
    )

    topicTableSQL = (
        "CREATE TABLE IF NOT EXISTS Topic (" +
        "TopicID INTEGER PRIMARY KEY," +
        "Name VARCHAR(40) NOT NULL);"
    )

    childTopicTableSQL = (
        "CREATE TABLE IF NOT EXISTS ChildTopic (" +
        "ChildID INTEGER NOT NULL," +
        "TopicID INTEGER NOT NULL," +
        "Level INTEGER NOT NULL," +
        "ParentTopicID INTEGER NOT NULL," +
        "FOREIGN KEY (ChildID) REFERENCES Child (ChildID) ON DELETE " +
        "CASCADE," +
        "FOREIGN KEY (TopicID) REFERENCES Topic (TopicID) ON DELETE " +
        "CASCADE," +
        "PRIMARY KEY (ChildID, TopicID));"
    )

    resultTableSQL = (
        "CREATE TABLE IF NOT EXISTS Result (" +
        "ResultID INTEGER PRIMARY KEY," +
        "Date DATE NOT NULL," +
        "Type VARCHAR(20) NOT NULL," +
        "StudentMark INTEGER NOT NULL," +
        "TotalMark INTEGER NOT NULL," +
        "Percentage REAL NOT NULL," +
        "ChildID INTEGER NOT NULL," +
        "TopicID INTEGER NOT NULL," +
        "FOREIGN KEY (ChildID) REFERENCES Child (ChildID) ON DELETE " +
        "CASCADE," +
        "FOREIGN KEY (TopicID) REFERENCES Topic (TopicID) ON DELETE CASCADE);"
    )

    connection = createConnection(dbFile)
    conn = connection.cursor()

    if conn is not None:
        conn.execute(userTableSQL)
        conn.execute(tutorTableSQL)
        conn.execute(parentTableSQL)
        conn.execute(childTableSQL)
        conn.execute(sessionTableSQL)
        conn.execute(childSessionTableSQL)
        conn.execute(topicTableSQL)
        conn.execute(childTopicTableSQL)
        conn.execute(resultTableSQL)
    else:
        print("Error! Cannot create the database connection.")


if __name__ == "__main__":
    createDatabase()
