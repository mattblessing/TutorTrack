from flask import redirect, url_for, flash
from markupsafe import Markup
from sqlalchemy import text
from tutortrack import db
import random


def createTopic(form):
    """
    Add a topic to the database.

    Args:
        form: The topic form filled out by a tutor.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            level = 0
            if form.type.data == "topic":
                form.parentTopic.data = 0
                level = 0
            else:
                parentTopic = conn.execute(text(
                    "SELECT Level " +
                    "FROM ChildTopic " +
                    "WHERE ChildID=:cID AND TopicID=:tID"
                ),
                    {"cID": form.child.data, "tID": form.parentTopic.data}
                ).fetchall()[0]
                level = parentTopic[0] + 1
            topics = conn.execute(
                text("SELECT * FROM Topic WHERE Name=:name"),
                {"name": form.name.data}
            ).fetchall()

            if len(topics) == 0:
                # If topic doesn't already exist in Topic table
                topicID = generateTopicID()
                conn.execute(
                    text("INSERT INTO Topic VALUES (:id, :name)"),
                    {"id": topicID, "name": form.name.data}
                )
            else:
                # New topic record does not need to be created
                topicID = topics[0][0]

            childTopics = conn.execute(text(
                "SELECT * FROM ChildTopic WHERE ChildID=:cID AND TopicID=:tID"
            ),
                {"cID": form.child.data, "tID": topicID}
            ).fetchall()
            if len(childTopics) == 0:
                # If a child-topic record does not already exist for that
                # childID and topicID
                conn.execute(text(
                    "INSERT INTO ChildTopic VALUES (:cID, :tID, :lvl, :ptID)"
                ),
                    {
                        "cID": form.child.data, "tID": topicID, "lvl": level,
                        "ptID": form.parentTopic.data
                }
                )
                flash("The topic was successfully created.", "success")
            else:
                # Display error message with link
                flash(
                    Markup(
                        "That Topic has already been created. You can " +
                        'change its details <a href="topic/' +
                        f'{form.child.data}/{form.name.data}">here</a>"'
                    ),
                    "info"
                )


def generateTopicID():
    """
    Generate a unique ID for a new session.
    """
    unique = False
    while unique == False:
        id = random.randint(100000, 999999)
        with db.engine.connect() as conn:
            idSearch = conn.execute(
                text("SELECT * FROM Topic WHERE TopicID=:id"), {"id": id}
            ).fetchall()
        if len(idSearch) == 0:
            unique = True
    return id


def updateTopic(form, childID, topicID, level, parentTopicID, topicName):
    """
    Update the details of a particular child's topic.

    Args:
        form: The updated topic form filled out by a tutor.
        childID (str): The child's ID.
        topicID (str): The existing topic's ID.
        level (int): The topic's new level in the child's topic hierarchy.
        parentTopicID (str | int): The topic's new parent topic ID.
        topicName (str): 
    """
    # Get children linked to the topic that matches form data
    with db.engine.connect() as conn:
        with conn.begin():
            topics = conn.execute(text(
                "SELECT Topic.TopicID, Child.ChildID, Topic.Name " +
                "FROM Topic, ChildTopic, Child " +
                "WHERE Name=:name AND Child.ChildID=ChildTopic.ChildID AND " +
                "Topic.TopicID=ChildTopic.TopicID"
            ),
                {"name": form.name.data}
            ).fetchall()

            results = conn.execute(
                text("SELECT * FROM Result WHERE TopicID=:id"), {"id": topicID}
            ).fetchall()

            if len(topics) != 0:
                # If there is a topic that matches form data
                for topic in topics:
                    if (
                        str(topic[1]) == str(childID) and
                        str(topic[0]) != str(topicID)
                    ):
                        # If topic is already linked to a child-topic record
                        # for the selected child
                        flash(
                            "A topic with the entered name already exists " +
                            "for this child.",
                            "danger"
                        )
                        return redirect(url_for(
                            "topics.change_topic_details", childID=childID,
                            topicName=topicName
                        ))

                # If the topic is the selected topic, then only update
                # ChildTopic
                if str(topics[0][0]) == str(topicID):
                    conn.execute(text(
                        "UPDATE ChildTopic SET Level=:lvl, " +
                        "ParentTopicID=:ptID " +
                        "WHERE ChildID=:cID AND TopicID=:tID"
                    ),
                        {
                            "lvl": level, "ptID": parentTopicID,
                            "cID": childID, "tID": topicID
                    }
                    )
                else:
                    # Get number of children that belong to selected topic
                    numChildren = conn.execute(text(
                        "SELECT ChildID " +
                        "FROM ChildTopic " +
                        "WHERE TopicID=:tID AND ChildID!=:cID"
                    ),
                        {"tID": topicID, "cID": childID}
                    ).fetchall()
                    if len(numChildren) == 0:
                        # If selected topic doesn't belong to any other
                        # children, delete selected topic
                        conn.execute(
                            text("DELETE FROM Topic WHERE TopicID=:id"),
                            {"id": topicID}
                        )  # Also delete results for topic
                    # Update TopicID in ChildTopic
                    conn.execute(text(
                        "DELETE FROM ChildTopic WHERE ChildID=:cID AND " +
                        "TopicID=:tID"
                    ),
                        {"cID": childID, "tID": topicID}
                    )
                    conn.execute(text(
                        "INSERT INTO ChildTopic VALUES (:cID, :tID, :lvl, " +
                        ":ptID)"
                    ),
                        {
                            "cID": childID, "tID": topics[0][0], "lvl": level,
                            "ptID": parentTopicID
                    }
                    )
                    # Update parent topic IDs of updated topic's subtopics
                    conn.execute(text(
                        "UPDATE ChildTopic SET ParentTopicID=:ptID WHERE " +
                        "ParentTopicID=:id"
                    ),
                        {"ptID": topics[0][0], "id": topicID}
                    )
                    # Update topic IDs of results linked to topic
                    for result in results:
                        conn.execute(text(
                            "INSERT INTO Result VALUES (:rID, :date, :type," +
                            " :sm, :tm, :pc, :cID, :tID)"
                        ),
                            {
                                "rID": result[0], "date": result[1],
                                "type": result[2], "sm": result[3],
                                "tm": result[4], "pc": result[5],
                                "cID": result[6], "tID": topics[0][0]
                        }
                        )
            else:
                # If a new topic needs to be created
                numChildren = conn.execute(text(
                    "SELECT ChildID FROM ChildTopic WHERE TopicID=:tID AND " +
                    "ChildID != :cID"
                ),
                    {"tID": topicID, "cID": childID}
                ).fetchall()
                if len(numChildren) == 0:
                    # If selected topic doesn't belong to any other
                    # children, just change the name of the topic
                    conn.execute(
                        text("UPDATE Topic SET Name=:name WHERE TopicID=:id"),
                        {"name": form.name.data, "id": topicID}
                    )
                else:
                    newTopicID = generateTopicID()
                    conn.execute(
                        text("INSERT INTO Topic VALUES (:tID, :name)"),
                        {"tID": newTopicID, "name": form.name.data}
                    )
                    # Update TopicID in ChildTopic
                    conn.execute(text(
                        "DELETE FROM ChildTopic " +
                        "WHERE ChildID=:cID AND TopicID=:tID"
                    ),
                        {"cID": childID, "tID": topicID}
                    )
                    conn.execute(text(
                        "INSERT INTO ChildTopic VALUES (:cID, :tID, :lvl, " +
                        ":ptID)"
                    ),
                        {
                            "cID": childID, "tID": newTopicID, "lvl": level,
                            "ptID": parentTopicID
                    }
                    )
                    # Update parent topic IDs of topic's subtopics
                    conn.execute(text(
                        "UPDATE ChildTopic SET ParentTopicID=:ptID WHERE " +
                        "ParentTopicID=:id"
                    ),
                        {"ptID": newTopicID, "id": topicID}
                    )
                    # Update topic IDs of results linked to topic
                    for result in results:
                        conn.execute(text(
                            "UPDATE Result SET TopicID=:tID WHERE ResultID=" +
                            ":rID AND ChildID=:cID"
                        ),
                            {
                                "tID": newTopicID, "rID": result[0],
                                "cID": childID
                        }
                        )
        flash("The topic details were successfully changed.", "success")

    return redirect(url_for("topics.view_topics"))


def changeSubtopicLevels(childID, topics, levelChange):
    """
    Update the level of each topic in the subtrees of a set of topics 
    for a particular child.

    Args:
        childID (str): A child ID.
        topics (list): A list of topic records.
        levelChange (int): The change in level for the topics.
    """
    for topic in topics:
        with db.engine.connect() as conn:
            subtopics = conn.execute(text(
                "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
                "ChildTopic.ParentTopicID " +
                "FROM Topic, ChildTopic " +
                "WHERE Topic.TopicID=ChildTopic.TopicID AND " +
                "ChildTopic.ParentTopicID=:id " +
                "ORDER BY ChildTopic.Level, Topic.Name"
            ),
                {"id": topic[0]}
            ).fetchall()
        # Recursively update the level of each topic in topic tree
        changeSubtopicLevels(childID, subtopics, levelChange)
        for subtopic in subtopics:
            level = subtopic[2] + levelChange
            with db.engine.connect() as conn:
                with conn.begin():
                    conn.execute(text(
                        "UPDATE ChildTopic SET Level=:lvl " +
                        "WHERE TopicID=:tID AND ChildID=:cID"
                    ),
                        {"lvl": level, "tID": subtopic[0], "cID": childID}
                    )


def deleteSubtopics(childID, topics):
    """
    Delete all topics in the subtrees of a set of topics for a particular
    child.

    Args:
        childID (str): A child ID.
        topics (list): A list of topic records.
    """
    for topic in topics:
        with db.engine.connect() as conn:
            subtopics = conn.execute(text(
                "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
                "ChildTopic.ParentTopicID " +
                "FROM Topic, ChildTopic " +
                "WHERE Topic.TopicID=ChildTopic.TopicID AND " +
                "ChildTopic.ParentTopicID=:id " +
                "ORDER BY ChildTopic.Level, Topic.Name"
            ),
                {"id": topic[0]}
            ).fetchall()
        # Recursively delete each topic in topic tree
        deleteSubtopics(childID, subtopics)
        for subtopic in subtopics:
            deleteTopic(childID, subtopic[0])


def deleteTopic(childID, topicID):
    """
    Delete a particular child's topic from the database once all its 
    subtopics have been deleted.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            children = conn.execute(text(
                "SELECT ChildID " +
                "FROM ChildTopic " +
                "WHERE TopicID=:tID AND ChildID!=:cID"
            ),
                {"tID": topicID, "cID": childID}
            ).fetchall()
            results = conn.execute(text(
                "SELECT * FROM Result WHERE TopicID=:tID AND ChildID=:cID"
            ),
                {"tID": topicID, "cID": childID}
            ).fetchall()

            if len(children) == 0:
                # If no other children are linked to the topic
                # Automatically deletes ChildTopic and Result records
                conn.execute(
                    text("DELETE FROM Topic WHERE TopicID=:id"),
                    {"id": topicID}
                )
            else:
                # Only delete ChildTopic record, not Topic record
                conn.execute(text(
                    "DELETE FROM ChildTopic WHERE ChildID=:cID AND " +
                    "TopicID=:tID"
                ),
                    {"cID": childID, "tID": topicID}
                )
                # Delete all results linked to topic and child
                for result in results:
                    conn.execute(
                        text("DELETE FROM Result WHERE ResultID=:id"),
                        {"id": result[0]}
                    )


def createTopicTrees(childID, topics, level, trees):
    """
    Add a set of topics (and their subtopics) to a given tree 
    structure at a particular level.

    Args:
        childID (str): A child ID.
        topics (list): A list of topic records.
        level (int): The hierarchy level to insert the topics at.
        trees (list): A list of trees (the hierarchy chart).

    Returns:
        trees (list): The tree structure with the topics (and their 
        subtopics) added.
    """
    for topic in topics:
        for tree in trees:
            if str(topic[0]) + "," + topic[1] in tree:
                # If topic's entry in adjacency list has not already
                # been created
                if len(tree[str(topic[0]) + "," + topic[1]]) == 0:
                    with db.engine.connect() as conn:
                        subtopics = conn.execute(text(
                            "SELECT Topic.TopicID, Topic.Name, " +
                            "ChildTopic.Level, ChildTopic.ParentTopicID " +
                            "FROM Topic, ChildTopic, Child " +
                            "WHERE Topic.TopicID=ChildTopic.TopicID AND " +
                            "Child.ChildID=ChildTopic.ChildID AND " +
                            "Child.ChildID=:cID AND " +
                            "ChildTopic.ParentTopicID=:ptID " +
                            "ORDER BY ChildTopic.Level, Topic.Name"
                        ),
                            {"cID": childID, "ptID": topic[0]}
                        ).fetchall()
                    for subtopic in subtopics:
                        # Add subtopic to topic's list
                        tree[str(topic[0]) + "," + topic[1]].append(
                            str(subtopic[0]) + "," + subtopic[1]
                        )
                        # Create subtopic's entry in adjacency list
                        tree[str(subtopic[0]) + "," + subtopic[1]] = []
                    createTopicTrees(childID, subtopics, level + 1, trees)
    return trees


def createTopicList(trees, allTopics=False):
    """
    Convert a set of topic trees into a list of topics, with 
    indentation reflecting the different levels.

    Args:
        trees (list): A list of topic trees.
        allTopics (bool): Whether 'All topics' should be included or 
            not.

    Returns:
        topics (list): A list of tuples (topic ID, topic name).
    """
    topics = []
    if allTopics == True:
        # Add "All topics" selection to start of topic list so it is
        # the default selection
        topics.append((0, "All topics"))
    for tree in trees:
        topic = list(tree)[0]  # The root of the tree
        topics = formTopicList(tree, topic, topics, 0)
    return topics


def formTopicList(tree, currentNode, visited, indent):
    """
    A recursive algorithm that uses pre order traversal logic to form 
    a list of topics from a topic tree.

    Args:
        tree (dict): A topic tree.
        currentNode (str): The current topic's ID and name as a string
            separated by a comma.
        visited (list): A list of visited topics.
        indent (str): The indent for the particular topic based on the
            tree level.

    Returns:
        visited (list): A list of visited topics after the pre-order 
            traversal.
    """
    # Add a tuple with the topicID and topic name (with indentation)
    visited.append((currentNode[:6], u"\xa0"*5*indent+currentNode[7:]))
    for node in tree[currentNode]:
        if node not in visited:
            formTopicList(tree, node, visited, indent + 1)
    return visited


def getHierarchyChartData(childID):
    """
    Get the topic hierarchy chart data for a particular child.

    Args:
        childID (str): A particular child's ID.

    Returns:
        data (list): A list of [topic] and [parent topic, child topic] 
            lists.
    """
    # Get the topics for the selected child
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
            trees.append({})
            # Initialise the tree for each of the user's topics (ones at
            # level 0)
            trees[len(trees)-1][str(topics[i][0]) + "," + topics[i][1]] = []

    if len(topics) > 0:
        # Each topic has its own tree, so a list of trees is produced
        trees = createTopicTrees(childID, topics, 0, trees)
        # Convert to a list of topics
        data = createHierarchyChartTopicList(trees)
    else:
        # If there are no topics then this node is displayed in chart
        data = [["No topics currently exist for this child! Create a topic!"]]

    return data


def createHierarchyChartTopicList(trees):
    """
    Convert a list of topic trees into hierarchy chart data to be 
    visualised.

    Args:
        trees (list): A list of topic trees.

    Returns:
        topics (list): A list of [topic] and [parent topic, child 
            topic] lists.
    """
    topics = []
    for tree in trees:
        topic = list(tree)[0]  # The root of the tree
        topics = formHierarchyChartTopicList(tree, topic, topics, 0)
    return topics


def formHierarchyChartTopicList(tree, currentTopic, topics, parentTopic):
    """
    A recursive algorithm that uses pre order traversal logic to form 
    a list of topics from a topic tree for visualisation.

    Args:
        tree (dict): A topic tree.
        currentTopic (str): The ID and name of the topic to add as a 
            string separated by a comma.
        topics (list): A list of [topic] and [parent topic, child 
            topic] lists.
        parentTopic (str): The ID and name of the new topic's parent 
            as a string separated by a comma.

    Returns:
        topics (list): The list of [topic] and [parent topic, child 
            topic] lists with 'currentTopic' added.
    """
    if parentTopic != 0:
        # Add [parent topic name, topic name]
        topics.append([str(parentTopic)[7:], str(currentTopic)[7:]])
    # If topic is a topic (parent topic = 0) and has no subtopics
    elif parentTopic == 0 and len(tree[currentTopic]) == 0:
        # Add the topic with no link to any other nodes to the chart
        topics.append([str(currentTopic)[7:]])
    for node in tree[currentTopic]:
        formHierarchyChartTopicList(tree, node, topics, currentTopic)

    return topics


def getChangeParentTopicList(childID, topicID):
    """
    Get a list of possible new parent topics for a given topic for a 
    child. This includes all topics that are not in the tree rooted at
    the given topic.

    Args:
        childID (str): A child ID.
        topicID (str): A topic ID.

    Returns:
        topicList (list): A list of possible new parent topics.
    """
    # Get the topics for the selected child
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
        # Initialise trees for all topics except topic with topicID
        if topics[i][2] == 0 and topics[i][0] != topicID:
            trees.append({})
            trees[len(trees)-1][str(topics[i][0])+","+topics[i][1]] = []
    # Create list of topic trees
    trees = createTopicTrees(childID, topics, 0, trees)
    # Turn it into a list of topics
    topicList = createChangeParentTopicList(trees, topicID)

    return topicList


def createChangeParentTopicList(trees, currentTopicID):
    """
    Convert a list of topic trees into a list of topics not including
    any topics in the tree rooted at the current topic.

    Args:
        trees (list): A list of topic trees.
        currentTopicID (str): The current topic ID.

    Returns:
        topics (list): A list of (topic ID, topic name) tuples.
    """
    topics = []
    for tree in trees:
        topic = list(tree)[0]  # The root of the tree
        topics = formChangeParentTopicList(
            tree, topic, topics, 0, currentTopicID
        )
    return topics


def formChangeParentTopicList(
        tree, currentNode, visited, indent, currentTopicID
):
    """
    A recursive algorithm that uses pre order traversal logic to form 
    a list of topics from a topic tree while not including the topics 
    in the tree rooted at the topic with ID `currentTopicID`.

    Args:
        tree (dict): A topic tree.
        currentNode (str): The current topic's ID and name as a string
            separated by a comma.
        visited (list): A list of visited topics.
        indent (str): The indent for the particular topic based on the
            tree level.
        currentTopicID (str): The ID of the topic to ignore the tree 
            of.

    Returns:
        visited (list): A list of visited topics after the pre-order 
            traversal.
    """
    if str(currentNode[:6]) != str(currentTopicID):
        # Add tuple with topic ID and topic name (with indentation)
        visited.append((currentNode[:6], u"\xa0"*5*indent+currentNode[7:]))
    for node in tree[currentNode]:
        if node not in visited and str(node[:6]) != str(currentTopicID):
            formChangeParentTopicList(
                tree, node, visited, indent + 1, currentTopicID
            )
    return visited
