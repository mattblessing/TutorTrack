from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.email import sendEmail
from tutortrack.topics.utils import createTopicTrees, createTopicList
import datetime


def getChildrenSelectList(allChildren=False):
    """
    Form a list of tuples for the 'child select' field for the current
    user.

    Args:
        allChildren (bool): Whether 'All students' should be an
            option. Default = False.

    Returns:
        children (list): A list of (child ID, child name) tuples.
    """
    children = []

    # Get all children linked to user
    if current_user.type == "tutor":
        with db.engine.connect() as conn:
            search = conn.execute(text(
                "SELECT Child.ChildID, Child.Firstname, Child.Surname " +
                "FROM User, Parent, Child " +
                "WHERE User.UserID=Parent.ParentID AND Parent.ParentID=" +
                "Child.ParentID AND Parent.TutorID=:id AND " +
                "User.Confirmed=1 " +
                "ORDER BY Child.Surname, Child.Firstname"
            ),
                {"id": current_user.userID}
            ).fetchall()
    elif current_user.type == "parent":
        with db.engine.connect() as conn:
            search = conn.execute(text(
                "SELECT ChildID, Firstname, Surname " +
                "FROM Child " +
                "WHERE Child.ParentID=:id " +
                "ORDER BY Surname, Firstname"
            ),
                {"id": current_user.userID}
            ).fetchall()

    # If 'All students' is to be a valid option
    if allChildren == True:
        children.append(("", "All students"))

    for record in search:
        # Add (child ID, child name) to the list
        children.append((record[0], record[1] + " " + record[2]))

    return children


def getTopicSelectList(childID, allTopics=False):
    """
    Form a list of tuples for the 'topic select' field for a child.

    Args:
        childID (str): The child's ID.
        allTopics (bool): Whether 'All topics' should be an option.
            Default = False.

    Returns:
        topicList (list): A list of (topic ID, topic name) tuples.
    """
    # Get the topics for the child
    with db.engine.connect() as conn:
        topics = conn.execute(text(
            "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
            "ChildTopic.ParentTopicID " +
            "FROM Topic, ChildTopic " +
            "WHERE Topic.TopicID=ChildTopic.TopicID AND ChildTopic.ChildID=" +
            ":id " +
            "ORDER BY ChildTopic.Level, Topic.Name"
        ),
            {"id": childID}
        ).fetchall()

    trees = []
    for i in range(len(topics)):
        if topics[i][2] == 0:
            # If level is 0, initialise a topic tree
            topicKey = f"{topics[i][0]},{topics[i][1]}"
            trees.append({topicKey: []})

    # Get the topic tree structure
    trees = createTopicTrees(childID, topics, 0, trees)

    # Convert to a list of (topic ID, topic name) tuples
    topicList = createTopicList(trees, allTopics)

    return topicList


def notificationEmail(email, html):
    """
    Send a notification email for a session or result being logged.

    Args:
        email (str): The recipient email address.
        html: The email HTML content.
    """
    subject = "Update"
    sendEmail(email, subject, html)


def topicsInTopicTree(childID, topicID):
    """
    Form a list of tuples for the set of topics in the tree rooted at
    a particular topic.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.

    Returns:
        topicList (list): A list of (topic ID, topic name) tuples.
    """
    with db.engine.connect() as conn:
        topics = conn.execute(text(
            "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
            "ChildTopic.ParentTopicID " +
            "FROM Topic, ChildTopic " +
            "WHERE Topic.TopicID=ChildTopic.TopicID AND ChildTopic.ChildID=" +
            ":id " +
            "ORDER BY ChildTopic.Level, Topic.Name"
        ),
            {"id": childID}
        ).fetchall()

    tree = []
    for i in range(len(topics)):
        # Initialise the topic tree rooted at the topic with `topicID`
        if str(topics[i][0]) == str(topicID):
            tree.append({})
            tree[len(tree)-1][str(topics[i][0]) + "," + topics[i][1]] = []
    # Create the topic tree
    tree = createTopicTrees(childID, topics, 0, tree)
    # Convert it into a list of topics
    topicList = createTopicList(tree)

    return topicList


def topicTreeLength(childID, topicID):
    """
    Get the number of topics in the topic tree rooted at the topic with
    ID `topicID`.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.

    Returns:
        The number of topics in the topic tree.
    """
    topicList = topicsInTopicTree(childID, topicID)
    return len(topicList)


def topicAndSubtopicResults(childID, topicID, startDate, endDate):
    """
    Get a child's results for a particular topic and all of its
    subtopics in a particular date range.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.
        startDate (datetime.datetime): The start date for the date
            range to consider results in.
        endDate (datetime.datetime): The end date for the date range
            to consider results in.

    Returns:
        The results sorted by date.
    """
    if startDate == None and endDate == None:
        topicList = topicsInTopicTree(childID, topicID)
        results = []
        # For each topic in topic tree
        for topic in topicList:
            if current_user.type == "tutor":
                with db.engine.connect() as conn:
                    resultList = conn.execute(text(
                        "SELECT Child.ChildID, Child.Firstname, " +
                        "Child.Surname, Result.ResultID, Result.Date, " +
                        "Result.Type, CAST(Result.Percentage AS varchar), " +
                        "Topic.Name " +
                        "FROM Parent, Child, Result, Topic " +
                        "WHERE Parent.ParentID=Child.ParentID AND " +
                        "Child.ChildID=Result.ChildID AND Topic.TopicID=" +
                        "Result.TopicID AND Parent.TutorID=:tID AND " +
                        "Child.ChildID=:cID AND Topic.TopicID=:topID " +
                        "ORDER BY Result.Date DESC"
                    ),
                        {
                            "tID": current_user.userID,
                            "cID": childID,
                            "topID": topic[0]
                    }
                    ).fetchall()
            elif current_user.type == "parent":
                with db.engine.connect() as conn:
                    resultList = conn.execute(text(
                        "SELECT Child.ChildID, Child.Firstname, " +
                        "Child.Surname, Result.ResultID, Result.Date, " +
                        "Result.Type, CAST(Result.Percentage AS varchar), " +
                        "Topic.Name " +
                        "FROM Child, Result, Topic " +
                        "WHERE Child.ChildID=Result.ChildID AND " +
                        "Topic.TopicID=Result.TopicID AND Child.ParentID=" +
                        ":pID AND Child.ChildID=:cID AND Topic.TopicID=" +
                        ":topID " +
                        "ORDER BY Result.Date DESC"
                    ),
                        {
                            "pID": current_user.userID,
                            "cID": childID,
                            "topID": topic[0]
                    }
                    ).fetchall()
            if len(resultList) != 0:
                for result in resultList:
                    # Add each result to a list
                    results.append(result)
    else:
        # Get results within a date range
        topicList = topicsInTopicTree(childID, topicID)
        results = []
        # For each topic in topic tree
        for topic in topicList:
            if current_user.type == "tutor":
                with db.engine.connect() as conn:
                    resultList = conn.execute(text(
                        "SELECT Child.ChildID, Child.Firstname, " +
                        "Child.Surname, Result.ResultID, Result.Date, " +
                        "Result.Type, CAST(Result.Percentage AS varchar), " +
                        "Topic.Name " +
                        "FROM Parent, Child, Result, Topic " +
                        "WHERE Parent.ParentID=Child.ParentID AND " +
                        "Child.ChildID=Result.ChildID AND Topic.TopicID=" +
                        "Result.TopicID AND Parent.TutorID=:tID AND " +
                        "Child.ChildID=:cID AND Topic.TopicID=:topID AND " +
                        "Result.Date BETWEEN :sD AND :eD " +
                        "ORDER BY Result.Date DESC"
                    ),
                        {
                            "tID": current_user.userID, "cID": childID,
                            "topID": topic[0],
                            "sD": (
                                startDate - datetime.timedelta(days=1)
                            ).replace(hour=11, minute=59, second=59),
                            "eD": endDate.replace(hour=11, minute=59, second=59)
                    }
                    ).fetchall()
            elif current_user.type == "parent":
                with db.engine.connect() as conn:
                    resultList = conn.execute(text(
                        "SELECT Child.ChildID, Child.Firstname, " +
                        "Child.Surname, Result.ResultID, Result.Date, " +
                        "Result.Type, CAST(Result.Percentage AS varchar), " +
                        "Topic.Name " +
                        "FROM Child, Result, Topic " +
                        "WHERE Child.ChildID=Result.ChildID AND " +
                        "Topic.TopicID=Result.TopicID AND Child.ParentID=" +
                        ":pID AND Child.ChildID=:cID AND Topic.TopicID=" +
                        ":topID AND Result.Date BETWEEN :sD AND :eD OR " +
                        "Result.Date=:sD2 OR Result.Date=:eD2) " +
                        "ORDER BY Result.Date DESC"
                    ),
                        {
                            "pID": current_user.userID, "cID": childID,
                            "topID": topic[0],
                            "sD": (
                                startDate - datetime.timedelta(days=1)
                            ).replace(hour=11, minute=59, second=59),
                            "eD": endDate.replace(hour=11, minute=59, second=59)
                    }
                    ).fetchall()
            if len(resultList) != 0:
                for result in resultList:
                    # Add each result to a list
                    results.append(result)

    return results


def tutorGetResults(childID, topicID, startDate, endDate):
    """
    Get the results logged by a particular tutor for all topics in the
    tree rooted at the topic with ID `topicID`.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.
        startDate (datetime.datetime): The start date for the date
            range to consider results in.
        endDate (datetime.datetime): The end date for the date range
            to consider results in.

    Returns:
        results (list): A list of result records in the form of lists.
    """
    if startDate == None and endDate == None:
        if topicID == "0":  # Get all results for all topics
            with db.engine.connect() as conn:
                results = conn.execute(text(
                    "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                    "Result.ResultID, Result.Date, Result.Type, " +
                    "CAST(Result.Percentage as varchar), Topic.Name " +
                    "FROM Parent, Child, Result, Topic " +
                    "WHERE Parent.ParentID=Child.ParentID AND " +
                    "Child.ChildID= Result.ChildID AND Topic.TopicID=" +
                    "Result.TopicID AND Parent.TutorID=:uID AND " +
                    "Child.ChildID=:cID " +
                    "ORDER BY Result.Date DESC"
                ),
                    {"uID": current_user.userID, "cID": childID}
                ).fetchall()
        else:  # Get all results for topics in topic tree
            results = topicAndSubtopicResults(childID, topicID, None, None)
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        if topicID == "0":  # Get results for all topics within date range
            with db.engine.connect() as conn:
                results = conn.execute(text(
                    "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                    "Result.ResultID, Result.Date, Result.Type, " +
                    "CAST(Result.Percentage as varchar), Topic.Name " +
                    "FROM Parent, Child, Result, Topic " +
                    "WHERE Parent.ParentID=Child.ParentID AND " +
                    "Child.ChildID=Result.ChildID AND Topic.TopicID=" +
                    "Result.TopicID AND Parent.TutorID=:tID AND " +
                    "Child.ChildID=:cID AND Result.Date BETWEEN :sD AND " +
                    ":eD " +
                    "ORDER BY Result.Date DESC"""
                ),
                    {
                        "tID": current_user.userID, "cID": childID,
                        "sD": (
                            startDate - datetime.timedelta(days=1)
                        ).replace(hour=11, minute=59, second=59),
                        "eD": endDate.replace(hour=11, minute=59, second=59)
                }
                ).fetchall()
        else:  # Get results for topics in topic tree within date range
            results = topicAndSubtopicResults(
                childID, topicID, startDate, endDate
            )
    results = [list(row) for row in results]  # Convert each tuple to a list

    return results


def parentGetResults(childID, topicID, startDate, endDate):
    """
    Get the results for a particular child for all topics in the
    tree rooted at the topic with ID `topicID`.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.
        startDate (datetime.datetime): The start date for the date
            range to consider results in.
        endDate (datetime.datetime): The end date for the date range
            to consider results in.

    Returns:
        results (list): A list of result records in the form of lists.
    """
    if startDate == None and endDate == None:
        if topicID == "0":  # Get all results for all topics
            with db.engine.connect() as conn:
                results = conn.execute(text(
                    "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                    "Result.ResultID, Result.Date, Result.Type, " +
                    "CAST(Result.Percentage as varchar), Topic.Name " +
                    "FROM Child, Result, Topic WHERE Child.ChildID=" +
                    "Result.ChildID AND Topic.TopicID=Result.TopicID AND " +
                    "Child.ParentID=:uID AND Child.ChildID=:cID " +
                    "ORDER BY Result.Date DESC"
                ),
                    {"uID": current_user.userID, "cID": childID}
                ).fetchall()
        else:  # Get all results for topics in topic tree
            results = topicAndSubtopicResults(childID, topicID, None, None)
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        if topicID == "0":  # Get results for all topics within date range
            with db.engine.connect() as conn:
                results = conn.execute(text(
                    "SELECT Child.ChildID, Child.Firstname, Child.Surname, " +
                    "Result.ResultID, Result.Date, Result.Type, " +
                    "CAST(Result.Percentage as varchar), Topic.Name " +
                    "FROM Child, Result, Topic " +
                    "WHERE Child.ChildID=Result.ChildID AND Topic.TopicID=" +
                    "Result.TopicID AND Child.ParentID=:tID AND " +
                    "Child.ChildID=:cID AND Result.Date BETWEEN :sD AND " +
                    ":eD " +
                    "ORDER BY Result.Date DESC"
                ),
                    {
                        "tID": current_user.userID, "cID": childID,
                        "sD": (
                            startDate - datetime.timedelta(days=1)
                        ).replace(hour=11, minute=59, second=59),
                        "eD": endDate.replace(hour=11, minute=59, second=59)
                }
                ).fetchall()
        else:  # Get results for topics in topic tree within date range
            results = topicAndSubtopicResults(
                childID, topicID, startDate, endDate
            )
    results = [list(row) for row in results]  # Convert each tuple to a list

    return results


def datePartition(aList, start, end):
    """
    Partition a list of results/sessions based on their date.

    Args:
        aList (list): A list of result/session records.
        start (int): The start index.
        end (int): The end index.

    Returns:
        rightmark (int): The point at which to partition the list.
    """
    pivot = aList[start]
    leftmark = start + 1
    rightmark = end
    done = False
    while done == False:
        while (
            leftmark <= rightmark and
            datetime.datetime.strptime(aList[leftmark][4], "%Y-%m-%d") <=
            datetime.datetime.strptime(pivot[4], "%Y-%m-%d")
        ):
            leftmark = leftmark + 1
        while (
            datetime.datetime.strptime(aList[rightmark][4], "%Y-%m-%d") >=
            datetime.datetime.strptime(pivot[4], "%Y-%m-%d") and
            rightmark >= leftmark
        ):
            rightmark = rightmark - 1
        if rightmark < leftmark:
            done = True
        else:
            temp = aList[leftmark]  # Swap the data items
            aList[leftmark] = aList[rightmark]
            aList[rightmark] = temp
    temp = aList[start]
    aList[start] = aList[rightmark]
    aList[rightmark] = temp
    return rightmark


def scorePartition(topics, start, end):
    """
    Partition a list of topics based on their mean score.

    Args:
        topics (list): A list of topic records.
        start (int): The start index.
        end (int): The end index.

    Returns:
        rightmark (int): The point at which to partition the list.
    """
    pivot = topics[start]
    leftmark = start + 1
    rightmark = end
    done = False
    while done == False:
        while leftmark <= rightmark and topics[leftmark][1] <= pivot[1]:
            leftmark = leftmark + 1
        while topics[rightmark][1] >= pivot[1] and rightmark >= leftmark:
            rightmark = rightmark - 1
        if rightmark < leftmark:
            done = True
        else:
            temp = topics[leftmark]  # Swap the data items
            topics[leftmark] = topics[rightmark]
            topics[rightmark] = temp
    temp = topics[start]
    topics[start] = topics[rightmark]
    topics[rightmark] = temp
    return rightmark


def quicksort(aList, start, end, sortType):
    """
    Quicksort a list of either results/sessions by date or topics by
    mean score.

    Args:
        aList (list): A list of either results/sessions or topics.
        start (int): The start index.
        end (int): The end index.
        sortType (str): Either "date" to sort results by date or
            "score" to sort topics by mean score.
    """
    if start < end:
        if sortType == "date":  # Sort based on date
            split = datePartition(aList, start, end)
            quicksort(aList, start, split - 1, "date")
            quicksort(aList, split + 1, end, "date")
        elif sortType == "score":  # Sort based on mean score
            split = scorePartition(aList, start, end)
            quicksort(aList, start, split - 1, "score")
            quicksort(aList, split + 1, end, "score")
    return aList
