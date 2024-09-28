from sqlalchemy import text
from tutortrack import db
from tutortrack.utils import tutorGetResults, quicksort, topicTreeLength
import datetime
import math


def getHistogramData(results):
    """
    Get the data for the histogram showing the distribution of results.

    Notes:
        The histogram bins are 0-10%, 10-20%, ..., 90-100%.

    Args:
        results (list): A list of result records.

    Returns:
        histogram (list): The histogram data (the frequency in each 
            bin).
    """
    histogram = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for result in results:
        percent = float(result[6])

        # If 100%, then the first digit won"t correspond to the bin
        # number (the bin number corresponds to the tens digit)
        if percent == 100:
            histogram[9] += 1
        # If <10%, then the first digit won"t correspond to the bin
        # number (the bin number corresponds to the tens digit)
        elif percent < 10:
            histogram[0] += 1
        else:
            index = math.floor(percent/10)
            histogram[index] += 1

    return histogram


def getMeans(childID, topics, startDate, endDate):
    """
    Get a particular child"s mean score in a set of topics.

    Args:
        childID (str): The child ID.
        topics (list): A list of topic records.
        startDate (datetime.datetime): The start of the date range 
            to consider.
        endDate (datetime.datetime): The end of the date range 
            to consider.

    Returns:
        means (list): A list of (topic name, mean score, num results)
            tuples.
    """
    means = []
    for topic in topics:
        # Get results for topic
        results = tutorGetResults(childID, topic[0], startDate, endDate)
        if len(results) != 0:
            means.append([topic[1], meanResult(results), len(results)])
    return means


def meanResult(results):
    """
    Given a list of result records, calculate the mean score.

    Args:
        results (list): A list of result records.

    Results:
        mean (scalar): The mean score.
    """
    total = 0
    for result in results:
        total += float(result[6])
    # Divide by number of results and round to 1 d.p
    mean = round(total/(len(results)), 1)
    return mean


def childMean(childID, startDate, endDate):
    """
    Get a particular child"s overall mean score.

    Args:
        childID (str): The child ID.
        startDate (datetime.datetime): The start of the date range 
            to consider.
        endDate (datetime.datetime): The end of the date range 
            to consider.

    Returns:
        mean (scalar | None): The mean score. None if the child has no
            results.
    """
    mean = None
    # Get all results for child
    results = tutorGetResults(childID, "0", startDate, endDate)
    if len(results) != 0:
        # Get the mean score of child"s results for all topics
        mean = meanResult(results)
    return mean


def createRevisionList(childID, topics, startDate, endDate):
    """
    Create a revision list for a child given the mean scores in the
    topics they are studying in a given date range.

    Args:
        childID (str): The child ID.
        topics (list): A list of (topic name, mean score, num results)
            tuples.
        startDate (datetime.datetime): The start of the date range 
            to consider.
        endDate (datetime.datetime): The end of the date range 
            to consider.

    Returns:
        revisionList (list): 
    """
    revisionList = []

    # Get overall mean score
    mean = childMean(childID, startDate, endDate)
    if mean == None:
        # If mean is None then child has no results
        return []

    for topic in topics:
        # Remove tabs
        topic[0] = topic[0].replace("\xa0", "")
        with db.engine.connect() as conn:
            # Get topic ID from name
            topicID = conn.execute(
                text("SELECT TopicID FROM Topic WHERE Name=:n"),
                {"n": topic[0]}
            ).fetchall()
            # Get child's results for topic in date range
            results = conn.execute(text(
                "SELECT * " +
                "FROM Result " +
                "WHERE ChildID=:cID AND (Date BETWEEN :sD1 AND :eD1 OR " +
                "Date=:sD2 OR Date=:eD2) AND TopicID=:tID " +
                "ORDER BY Date"
            ),
                {
                    "cID": childID, "tID": topicID[0][0],
                    "sD1": datetime.datetime.strptime(startDate, "%Y-%m-%d"),
                    "sD2": datetime.datetime.strptime(
                        startDate, "%Y-%m-%d"
                    ).strftime("%Y-%m-%d"),
                    "eD1": datetime.datetime.strptime(endDate, "%Y-%m-%d"),
                    "eD2": datetime.datetime.strptime(
                        endDate, "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
            }
            ).fetchall()

        topicTreeSize = topicTreeLength(childID, topicID[0][0])
        if topicTreeSize == 1 or len(results) != 0:
            # Topics with no subtopics can be added (tree size 1) to
            # revision list
            # Topics with subtopics can only be added to the revision
            # list when they have results logged for them
            if topic[1] < mean or topic[1] < 70:
                # If topic mean score is less than 70 or the child's
                # overall mean score
                revisionList.append(topic)

    # Revision list will be limited to 3 topics
    if len(revisionList) > 3:
        # Order revision list topics in order of mean percentage score
        revisionList = quicksort(
            revisionList, 0, len(revisionList)-1, "score"
        )
        # Keep 3 topics with lowest mean scores
        revisionList = revisionList[:3]

    return revisionList
